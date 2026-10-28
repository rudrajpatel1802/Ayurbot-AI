"""
Runtime layer used by the Streamlit app:
  * load the Spark PipelineModel from HDFS
  * predict a Prakriti from the 15 quiz answers (through Spark, not sklearn)
  * append every completed quiz to HDFS as Parquet, for later analytics
"""

from datetime import datetime, timezone

from pyspark.ml import PipelineModel
from pyspark.sql.types import (DoubleType, IntegerType, StringType, StructField,
                               StructType, TimestampType)

import config
from spark_utils import hdfs_exists

_FEATURE_SCHEMA = StructType([StructField(f, IntegerType(), False) for f in config.FEATURES])

_RESPONSE_SCHEMA = StructType(
    [StructField("session_id", StringType(), False),
     StructField("event_time", TimestampType(), False),
     StructField("event_date", StringType(), False)]
    + [StructField(f, IntegerType(), False) for f in config.FEATURES]
    + [StructField("predicted", StringType(), False)]
    + [StructField(f"p_{l.lower()}", DoubleType(), False) for l in config.PRAKRITI_LABELS]
)


def model_exists(spark) -> bool:
    return hdfs_exists(spark, config.MODEL_PATH)


def load_model(spark) -> PipelineModel:
    return PipelineModel.load(config.MODEL_PATH)


def predict(spark, model: PipelineModel, answers):
    """answers: list of 15 ints (0/1/2). Returns (label, [p_vata, p_pitta, p_kapha])."""
    df = spark.createDataFrame([tuple(int(a) for a in answers)], _FEATURE_SCHEMA)
    row = model.transform(df).select("probability").first()
    proba = [float(p) for p in row["probability"].toArray()]
    label = config.PRAKRITI_LABELS[max(range(len(proba)), key=proba.__getitem__)]
    return label, proba


def log_response(spark, session_id, answers, label, proba):
    """Append one completed quiz to HDFS (Parquet, partitioned by event_date)."""
    now = datetime.now(timezone.utc)
    record = ((session_id, now, now.strftime("%Y-%m-%d"))
              + tuple(int(a) for a in answers) + (label,) + tuple(float(p) for p in proba))
    (spark.createDataFrame([record], _RESPONSE_SCHEMA)
          .write.mode("append").partitionBy("event_date").parquet(config.RESPONSES_PATH))
