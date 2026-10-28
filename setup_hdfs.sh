#!/usr/bin/env bash
# Create the AyurBot directory tree in HDFS and upload the seed dataset.
#
#   ./setup_hdfs.sh
#   HDFS_URI=hdfs://namenode:9000 HDFS_BASE_DIR=/user/me/ayurbot ./setup_hdfs.sh
set -euo pipefail

HDFS_URI="${HDFS_URI:-hdfs://localhost:9000}"
BASE="${HDFS_BASE_DIR:-/ayurbot}"
H="hdfs dfs -fs ${HDFS_URI}"

echo ">> Creating ${HDFS_URI}${BASE} ..."
$H -mkdir -p "${BASE}/dataset" "${BASE}/model" "${BASE}/responses" "${BASE}/analytics"

echo ">> Uploading dataset ..."
$H -put -f dataset/prakriti_dataset.csv "${BASE}/dataset/prakriti_dataset.csv"

echo ">> Contents:"
$H -ls -R "${BASE}"
