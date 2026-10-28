"""
Central configuration for AyurBot (Big Data edition).

Everything that touches storage goes through the paths defined here, so the
whole project can be pointed at a different cluster - or at the local disk for
testing - purely with environment variables:

    HDFS_URI        NameNode address          default: hdfs://localhost:9000
    HDFS_BASE_DIR   Project root inside HDFS  default: /ayurbot
    SPARK_MASTER    Spark master URL          default: local[*]
                    (use "yarn" on a real cluster)

Local test mode (no Hadoop needed):
    export HDFS_URI=file://
    export HDFS_BASE_DIR=/tmp/ayurbot_hdfs
"""

import os

# ─── Cluster settings ─────────────────────────────────────────────────────────
HDFS_URI = os.environ.get("HDFS_URI", "hdfs://localhost:9000").rstrip("/")
HDFS_BASE_DIR = "/" + os.environ.get("HDFS_BASE_DIR", "/ayurbot").strip("/")
SPARK_MASTER = os.environ.get("SPARK_MASTER", "local[*]")

# ─── HDFS layout ──────────────────────────────────────────────────────────────
#   /ayurbot
#   ├── dataset/prakriti_dataset.csv     training data (CSV with header)
#   ├── model/prakriti_rf_model          Spark ML PipelineModel (RandomForest)
#   ├── model/metrics                    training metrics (JSON) 
#   ├── responses/                       every quiz submission (Parquet, appended)
#   └── analytics/                       output of analytics.py
def _p(*parts: str) -> str:
    return HDFS_URI + HDFS_BASE_DIR + "/" + "/".join(parts)


DATASET_PATH = _p("dataset", "prakriti_dataset.csv")
MODEL_PATH = _p("model", "prakriti_rf_model")
METRICS_PATH = _p("model", "metrics")
RESPONSES_PATH = _p("responses")
ANALYTICS_PATH = _p("analytics")

# Local seed CSV that ships with the project (uploaded to HDFS on first run)
LOCAL_DATASET = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "dataset", "prakriti_dataset.csv")

# ─── Model schema ─────────────────────────────────────────────────────────────
# Values: 0 = Vata tendency, 1 = Pitta tendency, 2 = Kapha tendency
FEATURES = [
    "body_frame", "skin_type", "hair_type", "appetite", "digestion",
    "sleep_pattern", "energy_level", "temperament", "memory", "speech",
    "weather_preference", "thirst", "sweat", "joints", "weight_tendency",
]

# Order matters: index in this list == numeric label used by the Spark model
PRAKRITI_LABELS = ["Vata", "Pitta", "Kapha"]
