"""
Distributed Prakriti dataset generator (PySpark -> HDFS).

Same statistical recipe as the original single-machine script:
  * 55 % "pure" samples  : every feature = the class value, each flipped to
                           another dosha with probability 0.42
  * 45 % "mixed" samples : dual-dosha profile (65 % primary / ~25 % secondary /
                           ~10 % third dosha per feature)
  * Classes are balanced (Vata / Pitta / Kapha)

but rows are generated in parallel, one NumPy RNG per Spark partition, and the
result is written directly to HDFS - so the dataset can be as large as the
cluster allows.

Usage:
    python generate_dataset.py                       # 1,500 rows (same as original)
    python generate_dataset.py --rows 5000000 --partitions 40
    spark-submit generate_dataset.py --rows 50000000 --partitions 200
"""

import argparse

import numpy as np
from pyspark.sql.types import IntegerType, StringType, StructField, StructType

import config
from spark_utils import get_spark


def generate_partition(pid, rows, seed, n_features, labels_names,
                       noise=0.42, pure_frac=0.55, primary_w=0.65):
    """Generate `rows` samples for Spark partition `pid` (vectorised NumPy)."""
    rng = np.random.default_rng([seed, pid])          # independent stream per partition
    labels = np.arange(rows) % 3                       # balanced classes

    # Pure-dosha samples: class value, with `noise` chance of flipping to another dosha
    flips = rng.random((rows, n_features)) < noise
    other = (labels[:, None] + rng.integers(1, 3, (rows, n_features))) % 3
    pure_x = np.where(flips, other, labels[:, None])

    # Mixed dual-dosha samples: primary / secondary / third dosha per feature
    sec = (labels + rng.integers(1, 3, rows)) % 3
    third = 3 - labels - sec
    r = rng.random((rows, n_features))
    mixed_x = np.where(
        r < primary_w, labels[:, None],
        np.where(r < primary_w + (1 - primary_w) * 0.7, sec[:, None], third[:, None]),
    )

    is_pure = rng.random(rows) < pure_frac
    x = np.where(is_pure[:, None], pure_x, mixed_x)

    return [tuple(int(v) for v in row) + (labels_names[int(l)],)
            for row, l in zip(x, labels)]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rows", type=int, default=1500, help="total rows to generate")
    ap.add_argument("--partitions", type=int, default=4, help="Spark partitions")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--output", default=config.DATASET_PATH, help="HDFS output path")
    args = ap.parse_args()

    spark = get_spark("AyurBot-GenerateDataset")
    sc = spark.sparkContext

    rows_per_part = -(-args.rows // args.partitions)   # ceil
    n_features = len(config.FEATURES)
    names = config.PRAKRITI_LABELS
    seed = args.seed

    rdd = sc.parallelize(range(args.partitions), args.partitions).flatMap(
        lambda pid: generate_partition(pid, rows_per_part, seed, n_features, names)
    )

    schema = StructType(
        [StructField(f, IntegerType(), False) for f in config.FEATURES]
        + [StructField("prakriti", StringType(), False)]
    )
    df = spark.createDataFrame(rdd, schema).limit(args.rows)

    df.write.mode("overwrite").csv(args.output, header=True)

    out = spark.read.csv(args.output, header=True, inferSchema=True)
    print(f"\n✅ Wrote {out.count():,} rows x {len(out.columns)} cols -> {args.output}")
    out.groupBy("prakriti").count().orderBy("prakriti").show()
    spark.stop()


if __name__ == "__main__":
    main()
