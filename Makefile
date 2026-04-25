help:
	@echo "$(GREEN)Batch Pipeline Monitoring System$(NC)"
	@echo ""
	@echo "Commands:"
	@echo "  make bootstrap - First-time setup: pull images, init DB, start all services"
	@echo "  make up        - Start all services (subsequent runs)"
	@echo "  make down      - Stop all services"
	@echo "  make pull      - Pull all Docker images"
	@echo "  make init      - Run Airflow DB migrations and create admin user"
	@echo "  make status    - Check running status"
	@echo "  make logs      - View all logs"
	@echo "  make trigger   - Manually run pipeline"
	@echo "  make clean     - Reset everything (with volumes)"
	@echo ""
	@echo "After 'make up':"
	@echo "  📊 Grafana: http://localhost:3000 (admin/admin)"
	@echo "  📋 Airflow: http://localhost:8080 (airflow/airflow)"
	@echo "  📈 Prometheus: http://localhost:9090"

pull:
	@echo "$(GREEN)Pulling all Docker images...$(NC)"
	@docker compose pull
	@echo "$(GREEN)All images pulled!$(NC)"

init:
	@echo "$(GREEN)Running Airflow initialization (DB migrations + admin user)...$(NC)"
	@docker compose up airflow-init
	@echo "$(GREEN)Airflow initialization complete!$(NC)"

bootstrap: pull init up
	@echo "$(GREEN)Bootstrap complete! All services are up.$(NC)"
	@echo ""
	@echo "📊 Grafana: http://localhost:3000 (admin/admin)"
	@echo "📋 Airflow: http://localhost:8080 (airflow/airflow)"
	@echo "📈 Prometheus: http://localhost:9090"

up:
	@echo "$(GREEN)Starting all services...$(NC)"
	@docker compose up -d
	@echo "$(GREEN)All services started!$(NC)"
	@echo ""
	@echo "📊 Grafana: http://localhost:3000 (admin/admin)"
	@echo "📋 Airflow: http://localhost:8080 (airflow/airflow)"

down:
	@echo "$(RED)Stopping services...$(NC)"
	@docker compose down

status:
	@echo "$(GREEN)Service Status:$(NC)"
	@docker compose ps

logs:
	@docker compose logs -f

trigger:
	@echo "$(GREEN)Triggering pipeline...$(NC)"
	@docker exec airflow-scheduler airflow dags trigger batch_pipeline
	@echo "✅ Triggered! Check in 15 seconds"

clean:
	@echo "$(RED)⚠️  This will delete all data! Type 'yes' to continue:$(NC)"
	@read ans; \
	if [ "$$ans" = "yes" ]; then \
		docker compose down -v; \
		echo "$(GREEN)✓ All containers and volumes removed$(NC)"; \
	else \
		echo "$(RED)Cancelled$(NC)"; \
	fi

.PHONY: help pull init bootstrap up down status logs trigger clean

GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m