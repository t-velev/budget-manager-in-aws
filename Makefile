# Load environment variables from the .env file
include .env

REGION = eu-central-1
ECR_BASE = $(AWS_ACCOUNT).dkr.ecr.$(REGION).amazonaws.com/budget-manager-lambdas

deploy-lambda:
	docker build --provenance=false -t $(ECR_BASE):master-latest -f lambda.Dockerfile .
	docker push $(ECR_BASE):master-latest
	cd infra && terraform apply

deploy-dbt:
	docker build --provenance=false -t $(ECR_BASE):dbt-latest -f dbt-fargate.Dockerfile .
	docker push $(ECR_BASE):dbt-latest
	cd infra && terraform apply

get_ecr_tmp_pass:
	aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.eu-central-1.amazonaws.com