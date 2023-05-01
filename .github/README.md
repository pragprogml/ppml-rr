<!-- <h1 align="center">
	<img width="200"
		src="media/ppml-cover.png">
</h1> -->

<h1 align="center">
	<img width="200"
		src="https://raw.githubusercontent.com/pragprogml/ppml-rr/main/media/ppml-cover.svg?token=GHSAT0AAAAAACAOY62F5RF2ZUBJTUAQXOM6ZB65TDA">
</h1>

<h3 align="center">
	Recommending Recommendations: A Recommender System Using Natural Language Understanding
</h3>

<p align="center">
	<strong>
		<a href="https://www.routledge.com/The-Pragmatic-Programmer-for-Machine-Learning-Engineering-Analytics-and/Scutari-Malvestio/p/book/9780429292835" target="_blank">Hardback and eBook</a>
    •
		<a href="https://ppml.dev" target="_blank">Bookdown HTML Version</a>
	</strong>
</p>

## Overview

This repository contains the code for the use case *Recommending Recommendations: A Recommender System Using Natural
Language Understanding* from the book **The Pragmatic Programmer for Machine Learning**, published by [Taylor &
Francis](https://www.taylorfrancis.com/books/mono/10.1201/9780429292835/pragmatic-programmer-machine-learning-marco-scutari-mauro-malvestio).

## Prerequisites

To use this repository, you will need to install the following software dependencies on your computer with your 
distribution's packet manager (on Linux), `brew` (on MacOS) or `Chocolately` (on Windows). These dependencies
are necessary for the ppml-rr software stack to function properly.

* Docker 20.10+ - [Docker documentation](https://docs.docker.com/get-docker/).
* Docker Compose 2.15+ - [Docker Compose documentation](https://docs.docker.com/compose/install/).
* Python 3.10+ - [Python documentation](https://www.python.org/downloads/).
* VirtualEnv 20.10+ - [VirtualEnv documentation](https://virtualenv.pypa.io/en/latest/installation.html).
* GNU Make 3.81+ - [GNU Make documentation](https://www.gnu.org/software/make/).
* PipEnv 2023.3.1+ - [PipEnv documentation](https://pipenv.pypa.io/en/latest/install/#installing-pipenv).
* Direnv 2.32+ - [Direnv documentation](https://direnv.net/docs/installation.html). 

To verify that you have the correct version of the software installed, run the following commands (for MacOS 
and GNU/Linux users):

```sh
make deps-check
Docker version 20.10.23 is installed.
Docker Compose version v2.15.1 is installed.
direnv version 2.32.2 is installed.
Python version 3.10.10 is installed.
Make version 3.81 is installed.
pipenv version 2023.3.20 is installed.
All required dependencies (Docker, docker-compose, DirEnv, Python, Make, pipenv) are installed correctly.
```

## First installation and basic usage

```sh
git clone https://github.com/pragprogml/ppml-rr # clone the repository
cd ppml-rr # go to the project directory
make venv # create a virtual environment
. ./.venv/bin/activate # activate the virtual environment
pipenv install -d  # install the python dependencies
make airflow-build # build the airflow container
make mlflow-build # build the mlflow container
```

## Environments

This project uses `direnv` to manage its environment variables. `direnv` is a tool that allows you to load and unload
environment variables based on your current working directory: it helps keep your shell environment clean and avoids
conflicts between different projects that may require different environment variables.

The `direnv` configuration file is located in the `.envrc` file. If you don't have `direnv` hooked inside your shell,
you can configure it following [this guide](https://direnv.net/docs/hook.html) or you can run the following command
to load the environment variables:

```sh
direnv allow 
```

## Development

### Resources and Project Structure

The project structure is the following:

```sh
├── airflow # Airflow DAGs
│   ├── dags
├── datasets # Datasets downloaded during the ingestion process
│   └── articles
├── docker # Dockerfiles
│   ├── airflow
│   ├── loki
│   ├── mlflow
│   └── ppml
├── docs # Sphinx auto-generated documentation
├── resources # Resources used by the project
│   ├── articles_list # List of articles to download
│   ├── benchmark # Benchmark files for testing
│   ├── corpus # Preprocessed corpus
│   └── keywords  # Keywords used to filter the articles (with and without bigrams)
├── scripts # Scripts used to run in development
├── src
│   ├── ingestion # Ingestion module
│   ├── preparation # Preparation module
│   └── training # Training module
└── tests
```

### Quickstart

```sh
docker network create ${PPML_RR_NETWORK} # create docker the network
make airflow-up # start Airflow
open http://localhost:8080/ # open Airflow UI
make mlflow-up # start MLflow
open http://localhost:8081/ # open MLflow UI
make loki-up # start Grafana Loki
open http://localhost:8090/ # open Grafana Loki UI

pipenv run python scripts/ingest_locally.py # ingest the data locally
pipenv run python scripts/train_locally.py # train the model locally

# import MLflow model inside BentoML
pipenv run python scripts/bento_import.py -b "ppml_rr" -s s3://mlflow/1/e9bd684976c648ed846b041c9fd5b788/artifacts/c3092b7a 

# run the BentoML service in development model
make bentoml-serve

# Build the BentoML service
make bentoml-build

# Build the BentoML container
make bentoml-containerize

# Run the BentoML container
make ppml-rr-up
make ppml-rr-down
```

## Known issues

Due the fact that we use "docker in docker" to build BentoML containers build inside the Airflow container, please
adjust the permssions of your docker socket to allow the `airflow` user to run docker commands. The docker socket 
is located in ```/var/run/docker.sock``` 

## Contact

Reach out to us via: [https://github.com/pragprogml](https://github.com/pragprogml) email. 

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Citing 
When citing PPML in academic papers and theses, please use this BibTeX entry:

```bibtex
@BOOK{ppml,
  author        = {M. Scutari and M. Malvestio},
  title         = {{The Pragmatic Programmer for Machine Learning: Engineering
                    Analytics and Data Science Solutions}},
  publisher     = {Chapman \& Hall},
  year          = {2023}
}
```
