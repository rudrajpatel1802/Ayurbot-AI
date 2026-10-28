"""
Spark / HDFS helpers shared by every job in the project.
"""

from pyspark.sql import SparkSession

import config


def get_spark(app_name: str = "AyurBot") -> SparkSession:
    """Create (or reuse) a SparkSession configured for this project."""
    spark = (
        SparkSession.builder
        .appName(app_name)
        .master(config.SPARK_MASTER)
        # The dataset is tiny relative to Spark's defaults - avoid 200 shuffle tasks
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


# ─── HDFS file-system helpers (via Hadoop's FileSystem API through the JVM) ───
def _fs_and_path(spark: SparkSession, path: str):
    jvm = spark._jvm
    hpath = jvm.org.apache.hadoop.fs.Path(path)
    fs = hpath.getFileSystem(spark._jsc.hadoopConfiguration())
    return fs, hpath


def hdfs_exists(spark: SparkSession, path: str) -> bool:
    fs, hpath = _fs_and_path(spark, path)
    return fs.exists(hpath)


def ensure_dataset(spark: SparkSession) -> None:
    """
    Make sure the training CSV exists in HDFS. If it doesn't, upload the seed
    CSV that ships with the project (equivalent to `hdfs dfs -put`).
    """
    if hdfs_exists(spark, config.DATASET_PATH):
        return
    print(f"[ingest] {config.DATASET_PATH} not found - uploading {config.LOCAL_DATASET}")
    df = spark.read.csv("file://" + config.LOCAL_DATASET, header=True, inferSchema=True)
    df.coalesce(1).write.mode("overwrite").csv(config.DATASET_PATH, header=True)
    print(f"[ingest] wrote {df.count()} rows to {config.DATASET_PATH}")
