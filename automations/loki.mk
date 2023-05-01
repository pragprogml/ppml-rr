
compose_loki = docker/loki/docker-compose.yaml

loki-up: ## Run the Grafana Loki stack
	docker compose -f ${compose_loki} up -d

loki-down: ## Shutdown the Grafana Loki stack
	docker compose -f ${compose_loki} down --volumes
