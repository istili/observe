help:
	@echo "$(GREEN)Batch Pipeline Monitoring System$(NC)"
	@echo ""
	@echo "Commands:"
	@echo "  make up      - Start all services"
	@echo "  make down    - Stop all services"
	@echo "  make status  - Check running status"
	@echo "  make trigger - Manually run pipeline"
	@echo "  make clean   - Reset everything"
	@echo ""
	@echo "After 'make up':"
	@echo "  1. Open http://localhost:3000 (admin/admin)"
	@echo "  2. Import dashboard-export.json"
	@echo "  3. Run 'make trigger'"

up:
	@echo "$(GREEN)Starting all services...$(NC)"
	@docker compose up -d
	@echo "$(GREEN)Waiting 30 seconds...$(NC)"
	@until docker exec airflow-webserver airflow db check >/dev/null 2>&1; do sleep 3; done
	@echo "$(GREEN)Unpausing DAG...$(NC)"
	@WEBSERVER=$$(docker ps --filter "name=^airflow-webserver$$" --format '{{.ID}}'); \
	if [ -n "$$WEBSERVER" ]; then docker exec "$$WEBSERVER" airflow dags unpause batch_pipeline; fi
	@echo "$(GREEN)Done!$(NC)"
	@echo ""
	@echo "📊 Grafana: http://localhost:3000 (admin/admin)"
	@echo "📋 Airflow: http://localhost:8080 (airflow/airflow)"
	@echo ""
	@echo "$(GREEN)--> Next: Import dashboard-export.json into Grafana$(NC)"

down:
	@echo "$(RED)Stopping...$(NC)"
	docker compose down

status:
	@echo "$(GREEN)Status:$(NC)"
	@docker ps --format "table {{.Names}}\t{{.Status}}" | head -10

trigger:
	@echo "$(GREEN)Triggering pipeline...$(NC)"
	@SCHEDULER=$$(docker ps --filter "name=^airflow-scheduler$$" --format '{{.ID}}'); \
	if [ -z "$$SCHEDULER" ]; then echo "$(RED)Scheduler not found. Run: make up$(NC)"; exit 1; fi; \
	docker exec "$$SCHEDULER" airflow dags trigger batch_pipeline
	@echo "✅ Triggered! Check Grafana in 15 seconds"

clean:
	@echo "$(RED)Reset everything? (y/N)$(NC)"
	@read ans; \
	if [ "$$ans" = "y" ]; then \
		docker compose down -v; \
		echo "$(GREEN)Cleaned!$(NC)"; \
	fi

.PHONY: help up down status trigger clean

GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m