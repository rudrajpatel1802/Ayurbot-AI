# 🌿 AyurBot — Big Data Edition (HDFS + PySpark)

Same Prakriti quiz + diet chatbot as the original project, rebuilt so that
**all storage lives in HDFS** and **all data processing / ML runs on PySpark**.

## Architecture

```
                         ┌──────────────────────────── HDFS ────────────────────────────┐
 generate_dataset.py ──▶ │ /ayurbot/dataset/prakriti_dataset.csv                        │
   (PySpark, parallel)   │                                                              │
                         │ /ayurbot/model/prakriti_rf_model   ◀── train_model.py        │
 setup_hdfs.sh (put) ──▶ │ /ayurbot/model/metrics (JSON)          (Spark MLlib)         │
                         │                                                              │
   app.py (Streamlit) ─▶ │ /ayurbot/responses/event_date=…/*.parquet  (every quiz)      │
   loads model,          │                                                              │
   predicts via Spark    │ /ayurbot/analytics/*        ◀── analytics.py (Spark SQL)     │
                         └──────────────────────────────────────────────────────────────┘
```

| File | Role |
|---|---|
| `config.py` | HDFS URI, paths, feature list – all set via env vars |
| `spark_utils.py` | SparkSession builder, HDFS `exists`, dataset ingest |
| `generate_dataset.py` | Distributed synthetic data generator (any number of rows) → HDFS |
| `train_model.py` | Spark MLlib `Pipeline(VectorAssembler → RandomForestClassifier)`; evaluation + 5-fold CV; saves model to HDFS |
| `predictor.py` | Loads model from HDFS, predicts with Spark, logs each quiz to HDFS as Parquet |
| `analytics.py` | Spark SQL reports over all stored responses; writes results to HDFS |
| `app.py` | Streamlit UI (same look & flow as before) |
| `content.py` | Questions, diet plans, rule-based chatbot (moved out of `app.py`, unchanged) |
| `setup_hdfs.sh` | Creates HDFS directories and uploads the seed CSV |

## Prerequisites

* Java 8 / 11 / 17 / 21 (`JAVA_HOME` set) — needed by Spark
* A running HDFS (`start-dfs.sh`), NameNode reachable at `HDFS_URI`
* `pip install -r requirements.txt`

## Run on HDFS

```bash
export HDFS_URI=hdfs://localhost:9000      # your NameNode (fs.defaultFS)
export HDFS_BASE_DIR=/ayurbot

./setup_hdfs.sh                            # 1. create dirs + upload dataset

# (optional) 2. generate a much bigger dataset in parallel instead of the 1,500-row CSV
python generate_dataset.py --rows 5000000 --partitions 40

python train_model.py                      # 3. train with Spark MLlib, model → HDFS
streamlit run app.py                       # 4. launch the chatbot
python analytics.py                        # 5. (after some quizzes) Spark SQL reports
```

If you skip step 3, the app trains the model on first launch and saves it to HDFS.

Inspect what's in HDFS:
```bash
hdfs dfs -ls -R /ayurbot
hdfs dfs -cat /ayurbot/model/metrics/part-*
```

## Run on a cluster (YARN)

```bash
export SPARK_MASTER=yarn
spark-submit --master yarn generate_dataset.py --rows 50000000 --partitions 200
spark-submit --master yarn train_model.py --skip-cv
```
`numpy` must be installed on the worker nodes for `generate_dataset.py`.

## Try it without Hadoop (local test mode)

Spark treats `file://` and `hdfs://` paths identically, so you can test the whole
project on a laptop with no HDFS:

```bash
export HDFS_URI=file://
export HDFS_BASE_DIR=/tmp/ayurbot_hdfs
python train_model.py && streamlit run app.py
```

## What changed vs. the original

| Original | Big Data edition |
|---|---|
| `dataset/*.csv` on local disk | CSV in HDFS (`/ayurbot/dataset`), read by Spark |
| NumPy generator, 1,500 rows | PySpark generator, parallel, any size, written to HDFS |
| scikit-learn `RandomForestClassifier` | Spark MLlib `RandomForestClassifier` in a `Pipeline` |
| `model/prakriti_model.pkl` (pickle) | Spark `PipelineModel` saved in HDFS |
| Predict with `model.predict_proba` | Predict with `model.transform(df)` on Spark |
| Nothing stored | Every quiz appended to HDFS (Parquet, partitioned by date) |
| — | `analytics.py` Spark SQL reports + live "compare with others" panel in the app |

Hyper-parameters are carried over (150 trees, depth 8, `sqrt` feature subset,
min 3 instances per leaf). MLlib has no equivalent of scikit-learn's
`min_samples_split`, and its train/test split (`randomSplit`) is random rather
than stratified — the classes are balanced so this doesn't matter here.

## Known limitations

* **Small files:** the app appends one tiny Parquet file per completed quiz. That is
  fine for a demo, but at real traffic it creates the classic HDFS small-files
  problem; buffer submissions (e.g. via Kafka / Spark Structured Streaming) or run
  a periodic compaction job.
* **Latency:** Spark adds ~1–2 s per prediction and a ~10–20 s cold start. The
  SparkSession and model are created once per Streamlit server and reused.
