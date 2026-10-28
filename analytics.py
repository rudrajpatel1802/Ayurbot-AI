"""
Analytics over every quiz submission stored in HDFS (Spark SQL).

    python analytics.py            # prints the reports and writes them to HDFS
    spark-submit analytics.py

Reports (written as Parquet under /ayurbot/analytics/):
  * prakriti_distribution : how many users fall in each Prakriti (+ avg confidence)
  * daily_activity        : submissions per day
  * feature_profile       : for each quiz question, how answers split per Prakriti
"""

from pyspark.sql import functions as F

import config
from spark_utils import get_spark, hdfs_exists


def read_responses(spark):
    if not hdfs_exists(spark, config.RESPONSES_PATH):
        return None
    return spark.read.parquet(config.RESPONSES_PATH)


def population_summary(spark):
    """
    Small summary used by the Streamlit app.
    Returns {"total": int, "distribution": {label: count}} or None if no data yet.
    """
    df = read_responses(spark)
    if df is None:
        return None
    rows = df.groupBy("predicted").count().collect()
    dist = {r["predicted"]: r["count"] for r in rows}
    return {"total": sum(dist.values()), "distribution": dist}


def run_reports(spark):
    df = read_responses(spark)
    if df is None or df.rdd.isEmpty():
        print(f"No responses found at {config.RESPONSES_PATH} yet - take the quiz first.")
        return

    df.createOrReplaceTempView("responses")
    total = df.count()
    print(f"\n📥 {total:,} quiz submissions read from {config.RESPONSES_PATH}\n")

    # 1) Distribution of predicted Prakriti
    distribution = spark.sql("""
        SELECT predicted                        AS prakriti,
               COUNT(*)                         AS users,
               ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct,
               ROUND(AVG(GREATEST(p_vata, p_pitta, p_kapha)), 3) AS avg_confidence
        FROM responses
        GROUP BY predicted
        ORDER BY users DESC
    """)
    print("── Prakriti distribution ──")
    distribution.show()

    # 2) Daily activity
    daily = spark.sql("""
        SELECT event_date, COUNT(*) AS submissions
        FROM responses GROUP BY event_date ORDER BY event_date
    """)
    print("── Daily activity ──")
    daily.show()

    # 3) Answer profile per question and Prakriti (wide -> long with stack())
    n = len(config.FEATURES)
    stack_expr = "stack({}, {}) AS (feature, answer)".format(
        n, ", ".join(f"'{f}', {f}" for f in config.FEATURES))
    profile = (df.selectExpr("predicted", stack_expr)
                 .groupBy("feature", "answer", "predicted").count()
                 .orderBy("feature", "predicted", "answer"))
    print("── Answer profile (first 12 rows) ──")
    profile.show(12)

    for name, frame in [("prakriti_distribution", distribution),
                        ("daily_activity", daily),
                        ("feature_profile", profile)]:
        out = f"{config.ANALYTICS_PATH}/{name}"
        frame.coalesce(1).write.mode("overwrite").parquet(out)
        print(f"💾 {out}")


if __name__ == "__main__":
    spark = get_spark("AyurBot-Analytics")
    run_reports(spark)
    spark.stop()
