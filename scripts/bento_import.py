"""
Imports an MLflow model into the BentoML model store.
"""

import argparse

import bentoml

parser = argparse.ArgumentParser(
    description="Import a MLflow model into BentoML model store."
)

parser.add_argument("-b", "--bento", required=True, help="The bento <bento>:<tag>")
parser.add_argument(
    "-s", "--s3-path", dest="s3_path", required=True, help="The MLflow s3:// path"
)

args = parser.parse_args()

bento = args.bento
s3_uri = args.s3_path

model = bentoml.mlflow.import_model(
    bento,
    s3_uri,
)
