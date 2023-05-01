compose_mlflow = docker/mlflow/docker-compose.yaml

mlflow-build: ## Build the mlflow image with software dependencies
	docker compose -f ${compose_mlflow} build

mlflow-up: ## Run the mlflow stack
	docker compose -f ${compose_mlflow} up -d

mlflow-down: ## Shutdown the mlflow stack
	docker compose -f ${compose_mlflow} down --volumes
