
ppml_rr_airflow = docker/ppml/docker-compose.yaml

ppml-rr-up: ## Run the containerized model
	docker-compose -f ${ppml_rr_airflow} up -d

ppml-rr-down: ## Tear down the containerized model
	docker-compose -f ${ppml_rr_airflow} down --volumes
