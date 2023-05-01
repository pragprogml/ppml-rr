
compose_airflow = docker/airflow/docker-compose.yaml

airflow-build: ## Build the Airflow image with software dependencies
	docker compose -f ${compose_airflow} build

airflow-up: ## Run the Airflow stack
	docker compose -f ${compose_airflow} up -d

airflow-down: ## Shutdown the Airflow stack
	docker compose -f ${compose_airflow} down --volumes

airflow-status: ## Check the Airflow stack status
	docker compose -f ${compose_airflow} ps

airflow-info: ## Get info about the Airflow stack
	docker compose -f ${compose_airflow} exec airflow-worker airflow info

airflow-dags-test: ## Run the main.py DAG
	docker compose -f ${compose_airflow} exec airflow-worker airflow dags test ppml_rr_main

airflow-dags-list: ## List dags
	docker compose -f ${compose_airflow} exec airflow-worker airflow dags list

airflow-shell: ## Run a shell inside the Airflow container
	docker compose -f ${compose_airflow} exec -it airflow-worker bash
