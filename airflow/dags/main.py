"""
### PPML Main DAG
"""

from __future__ import annotations

import logging
import os
import sys
import uuid
from textwrap import dedent

import bentoml

# pylint: disable=E0401
import pendulum
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from airflow import DAG

sys.path.append("src")

# pylint: disable=C0413
from ingestion.download import articles_download, convert_pdf_to_text_in_parallel
from preparation.convert import create_text_corpus
from training import train_and_track_experiment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with DAG(
    "ppml_rr_main",
    default_args={"retries": 1},
    description="Main PPML RR DAG",
    schedule=None,
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    catchup=False,
    tags=["nlu"],
) as dag:
    dag.doc_md = __doc__

    # Validate the environment variables
    def validate_environment(**kwargs):
        """Validates the environment variables."""

        environment_variables_path = [
            "ARXIV_ARTICLE_LIST_SMALL10",
            "PDF_DATADIR",
            "TXT_DATADIR",
            "TEXT_CORPUS_DATADIR",
            "DOMAIN_KEYWORDS",
        ]

        environment_variables = [
            "BENTO_BASENAME",
            "BENTO_MODEL",
            "TEXT_CORPUS_FNAME",
        ]

        for env_var in environment_variables_path:
            if env_var not in os.environ:
                raise ValueError(f"Environment variable {env_var} is not set.")

        for env_var in environment_variables:
            if env_var not in os.environ:
                raise ValueError(f"Environment variable {env_var} is not set.")

    validate_env_task = PythonOperator(
        task_id="validate_environment",
        python_callable=validate_environment,
        op_kwargs={},
    )
    validate_env_task.doc_md = dedent("""#### Validate the environment variables""")

    # Downaload articles task (pdf) from arXiv
    download_task = PythonOperator(
        task_id="download_articles_pdf",
        python_callable=articles_download,
        op_kwargs={
            "urls_file_path": os.getenv("ARXIV_ARTICLE_LIST_SMALL10"),
            "pdf_output_directory": os.getenv("PDF_DATADIR"),
        },
    )
    download_task.doc_md = dedent("""#### Download PDF article from arXiv""")

    # Convert pdf to text task (sequential), for more speed use the mp.pool implementation
    convert_task = PythonOperator(
        task_id="pdf_to_text",
        python_callable=convert_pdf_to_text_in_parallel,
        op_kwargs={
            "pdf_input_directory": os.getenv("PDF_DATADIR"),
            "txt_output_directory": os.getenv("TXT_DATADIR"),
        },
    )
    convert_task.doc_md = dedent("""#### Convert pdf to text task""")

    # Create a single text corpus
    create_corpus_task = PythonOperator(
        task_id="create_corpus",
        python_callable=create_text_corpus,
        op_kwargs={
            "text_corpus_datadir": os.getenv("TEXT_CORPUS_DATADIR"),
            "text_outfile_path": os.getenv("TEXT_CORPUS_FNAME"),
            "txt_input_directory": os.getenv("TXT_DATADIR"),
        },
    )
    create_corpus_task.doc_md = dedent("""#### Create a single text corpus""")

    # Training task for training a model and tracking the experiment

    training_task = PythonOperator(
        task_id="training",
        python_callable=train_and_track_experiment,
        provide_context=True,
        op_kwargs={
            "model_uri": str(uuid.uuid4().hex)[:8],
            "text_corpus": os.getenv("TEXT_CORPUS_DATADIR")
            + os.getenv("TEXT_CORPUS_FNAME"),
            "domain_keywords": os.getenv("DOMAIN_KEYWORDS"),
        },
    )

    training_task.doc_md = dedent("""#### Train a model and track the experiment""")

    # Wrapper for importing a trained model into BentoML
    def model_import_wrapper(**kwargs):
        """
        Imports a trained into BentoML for serving.

        This function serves as a wrapper for importing a trained machine learning model.
        """

        url = kwargs["ti"].xcom_pull(task_ids="training")
        model_basename = os.getenv("BENTO_BASENAME")
        bento_model = model_basename + ":" + str(uuid.uuid4().hex)[:8]
        bentoml.mlflow.import_model(name=bento_model, model_uri=url)
        os.environ["BENTO_MODEL"] = bento_model

    # Task for importing a trained model into BentoML
    model_import_task = PythonOperator(
        task_id="model_import",
        python_callable=model_import_wrapper,
        provide_context=True,
        op_kwargs=(),
    )

    model_import_task.doc_md = dedent(
        """  #### Import the model from MLFlow to BentoML"""
    )

    # Build model with BentoML
    model_build = BashOperator(
        task_id="model_build",
        bash_command="echo ${BENTO_MODEL} && cd /opt/airflow && bentoml build",
    )
    model_build.doc_md = dedent("""#### Build a BentoML model""")

    # Containarize model with BentoML
    model_containerize = BashOperator(
        task_id="model_containerize",
        bash_command="bentoml containerize ${BENTO_BASENAME}:latest --image-tag=${BENTO_BASENAME}:latest",
    )
    model_containerize.doc_md = dedent("""#### Containerize a BentoML model""")

    # Define the DAG
    # PyLint complains about the following line, but it is correct
    # pylint: disable=W0104
    (
        validate_env_task
        >> download_task
        >> convert_task
        >> create_corpus_task
        >> training_task
        >> model_import_task
        >> model_build
        >> model_containerize
    )
