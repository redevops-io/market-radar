.PHONY: install dev docs clean

# Install: start services using docker-compose
install:
	docker-compose up -d

# Dev: run agent locally for development
dev:
	@echo "Running agent in development mode..."
	./scripts/run-agent.sh

# Docs: serve documentation
docs:
	@echo "Serving documentation..."
	docker-compose up docs

# Clean: stop and remove all services
clean:
	docker-compose down -v --remove-orphans
