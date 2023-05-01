include automations/airflow.mk
include automations/mlflow.mk
include automations/loki.mk
include automations/bento.mk
include automations/ppml-rr.mk
include automations/main.mk

.DEFAULT_GOAL := help

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
