
bentoml-build: ## Build a BentoML model
	bentoml build

bentoml-containerize: ## Build a container for serving
	bentoml containerize ${BENTO_MODEL} --image-tag=${BENTO_MODEL}

bentoml-serve: ## Serve the model in development
	bentoml serve service:svc --reload
