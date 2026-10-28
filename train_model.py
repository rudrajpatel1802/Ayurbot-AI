"""
Prakriti model training with PySpark MLlib.

  HDFS  /ayurbot/dataset/prakriti_dataset.csv
      -> Spark DataFrame
      -> Pipeline[VectorAssembler -> RandomForestClassifier]
      -> evaluation (accuracy / F1 / confusion matrix / 5-fold CV)
      -> HDFS  /ayurbot/model/prakriti_rf_model   (PipelineModel)
      -> HDFS  /ayurbot/model/metrics             (JSON)

Usage:
    python train_model.py
    python train_model.py --skip-cv          # faster on big datasets
    spark-submit train_model.py
"""

import argparse
import json

from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.sql import functions as F

import config
from spark_utils import ensure_dataset, get_spark


def load_training_data(spark):
    """Read the CSV from HDFS and add the numeric label (Vata=0, Pitta=1, Kapha=2)."""
    df = spark.read.csv(config.DATASET_PATH, header=True, inferSchema=True)

    label_expr = F.col("prakriti")
    mapping = F.create_map(*[x for i, name in enumerate(config.PRAKRITI_LABELS)
                             for x in (F.lit(name), F.lit(float(i)))])
    return df.withColumn("label", mapping[label_expr]).select(*config.FEATURES, "label")


def build_pipeline():
    assembler = VectorAssembler(inputCols=config.FEATURES, outputCol="features")
    rf = RandomForestClassifier(
        featuresCol="features",
        labelCol="label",
        numTrees=150,                    # n_estimators=150
        maxDepth=8,                      # max_depth=8
        minInstancesPerNode=3,           # min_samples_leaf=3
        featureSubsetStrategy="sqrt",    # max_features="sqrt"
        seed=42,
    )
    return Pipeline(stages=[assembler, rf]), rf


def train_and_save(spark=None, run_cv=True):
    own_session = spark is None
    spark = spark or get_spark("AyurBot-Train")

    print("=" * 60)
    print("  🌿 PRAKRITI DETERMINE — Spark MLlib Model Training")
    print("=" * 60)

    ensure_dataset(spark)
    df = load_training_data(spark).cache()
    n = df.count()
    print(f"\n📊 Loaded {n:,} rows x {len(config.FEATURES)} features from\n   {config.DATASET_PATH}")

    train, test = df.randomSplit([0.8, 0.2], seed=42)
    print(f"   Train: {train.count():,} | Test: {test.count():,}\n")

    print("🌲 Training Random Forest (Spark MLlib)...")
    pipeline, rf = build_pipeline()
    model = pipeline.fit(train)
    rf_model = model.stages[-1]

    # ── Metrics ─────────────────────────────────────────────────────────────
    pred = model.transform(test).cache()
    ev = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction")
    acc = ev.setMetricName("accuracy").evaluate(pred)
    f1 = ev.setMetricName("f1").evaluate(pred)

    print("\n" + "─" * 60)
    print(f"  ✅ Test Accuracy : {acc:.2%}   (weighted F1: {f1:.2%})")
    print("─" * 60)

    print("\n📋 Per-class precision / recall:")
    per_class = {}
    for i, name in enumerate(config.PRAKRITI_LABELS):
        p = ev.setMetricName("precisionByLabel").setMetricLabel(float(i)).evaluate(pred)
        r = ev.setMetricName("recallByLabel").setMetricLabel(float(i)).evaluate(pred)
        per_class[name] = {"precision": round(p, 4), "recall": round(r, 4)}
        print(f"   {name:<6} precision={p:.2%}  recall={r:.2%}")

    print("\n🔢 Confusion Matrix (rows = true, cols = predicted):")
    cm = (pred.groupBy("label")
              .pivot("prediction", [0.0, 1.0, 2.0])
              .count().na.fill(0).orderBy("label"))
    cm = cm.toDF("true", *[f"Pred_{l}" for l in config.PRAKRITI_LABELS])
    names = F.create_map(*[x for i, l in enumerate(config.PRAKRITI_LABELS)
                           for x in (F.lit(float(i)), F.lit(f"True_{l}"))])
    cm.withColumn("true", names[F.col("true")]).show()

    cv_mean = cv_std = None
    if run_cv:
        print("🔄 5-Fold Cross-Validation (on the full dataset)...")
        grid = ParamGridBuilder().addGrid(rf.numTrees, [150]).build()
        cv = CrossValidator(
            estimator=pipeline, estimatorParamMaps=grid,
            evaluator=MulticlassClassificationEvaluator(metricName="accuracy"),
            numFolds=5, seed=42, parallelism=2,
        )
        cv_model = cv.fit(df)
        cv_mean = float(cv_model.avgMetrics[0])
        if hasattr(cv_model, "stdMetrics"):
            cv_std = float(cv_model.stdMetrics[0])
        print(f"   Mean accuracy: {cv_mean:.2%}" + (f"  ±  {cv_std:.2%}" if cv_std else ""))

    print("\n📈 Top 5 Feature Importances:")
    imp = sorted(zip(config.FEATURES, rf_model.featureImportances.toArray()),
                 key=lambda x: -x[1])
    for feat, v in imp[:5]:
        print(f"   {feat:<22} {v:.3f}  {'█' * int(v * 100)}")

    # ── Save to HDFS ────────────────────────────────────────────────────────
    model.write().overwrite().save(config.MODEL_PATH)
    print(f"\n💾 Model saved → {config.MODEL_PATH}")

    metrics = {
        "rows": n, "accuracy": round(acc, 4), "f1": round(f1, 4),
        "cv_mean_accuracy": None if cv_mean is None else round(cv_mean, 4),
        "per_class": per_class,
        "feature_importances": {k: round(float(v), 4) for k, v in imp},
    }
    (spark.createDataFrame([(json.dumps(metrics),)], ["json"])
          .coalesce(1).write.mode("overwrite").text(config.METRICS_PATH))
    print(f"📝 Metrics saved → {config.METRICS_PATH}")
    print("=" * 60)

    pred.unpersist(); df.unpersist()
    if own_session:
        spark.stop()
    return model


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-cv", action="store_true", help="skip 5-fold cross-validation")
    train_and_save(run_cv=not ap.parse_args().skip_cv)
