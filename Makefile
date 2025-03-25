# =========================
# ENVIRONMENT VARIABLES
# =========================
ENV ?= dev
REGION ?= us-west-2

# =========================
# INFRASTRUCTURE (Terraform)
# =========================
terraform-init:
	cd infra && terraform init

terraform-plan:
	cd infra && terraform plan -var="environment=$(ENV)" -var="aws_region=$(REGION)"

terraform-apply:
	cd infra && terraform apply -var="environment=$(ENV)" -var="aws_region=$(REGION)" -auto-approve

terraform-destroy:
	cd infra && terraform destroy -var="environment=$(ENV)" -var="aws_region=$(REGION)" -auto-approve

# =========================
# MONITORING (Docker Compose)
# =========================
monitoring-up:
	cd monitoring && docker-compose up -d --build

monitoring-down:
	cd monitoring && docker-compose down

monitoring-logs:
	cd monitoring && docker-compose logs -f

# =========================
# GRAFANA
# =========================
grafana-import-dashboards:
	curl -X POST http://localhost:3000/api/dashboards/db \
	 -H "Content-Type: application/json" \
	 -H "Authorization: Bearer admin" \
	 -d @monitoring/grafana/dashboards/summary_metrics.json

# =========================
# ELK
# =========================
elk-up:
	cd monitoring/elk && docker-compose up -d --build

elk-down:
	cd monitoring/elk && docker-compose down

elk-logs:
	cd monitoring/elk && docker-compose logs -f

# =========================
# ALL-IN-ONE
# =========================
start-all: terraform-apply monitoring-up elk-up

stop-all: monitoring-down elk-down terraform-destroy

rebuild-all: stop-all terraform-init terraform-apply monitoring-up elk-up

.PHONY: terraform-init terraform-plan terraform-apply terraform-destroy \
        monitoring-up monitoring-down monitoring-logs \
        grafana-import-dashboards \
        elk-up elk-down elk-logs \
        start-all stop-all rebuild-all

