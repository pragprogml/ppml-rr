
SHELL := /bin/zsh

.PHONY: venv-on
venv: ## Create a python virtual environment under .venv
	python -m virtualenv -p python3 .venv

.PHONY: venv-rm
venv-rm: ## Delete the python virtual environment under .venv
	rm -rf .venv

.PHONY: docs
docs: ## Update documentation
	sphinx-apidoc --doc-project=Modules -o ./docs/source ./src  -f
	$(MAKE) -C ./docs/ clean
	$(MAKE) -C ./docs/ html

.PHONY: deps-check
deps-check: ## Check dependencies
	@./scripts/check-deps.sh
