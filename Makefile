# =====================================================================================
#  HOW TO READ THIS FILE
#  "make NAME" runs the commands listed under NAME. A line like "up: ecr push-lambda"
#  means: before running "up", run "ecr" and "push-lambda" first.
#  Lines starting with # are only notes for humans. You never need to edit this file
#  to use it. Day-to-day you only need: login, plan, up, apply, down, audit.
# =====================================================================================

# Read AWS_ACCOUNT_ID from the .env file
include .env

# Settings used by the commands below
REGION        = eu-central-1
ECR_BASE      = $(AWS_ACCOUNT_ID).dkr.ecr.$(REGION).amazonaws.com/budget-manager-lambdas
LOGIN_PROFILE = tf-login
ROLE_PROFILE  = tf-deployer

# "WITH_ROLE" is a prefix that means: run the NEXT command wearing the terraform-deployer
# role's temporary 1-hour badge. Terraform cannot ask for your MFA code, so "make auth" asks
# for it first, and this prefix just picks up the badge that was already issued.
# Nothing is written to disk and the badge is only given to that one command.
WITH_ROLE = env $$(aws configure export-credentials --profile $(ROLE_PROFILE) --format env-no-export | xargs)

# ============================ 1. SIGNING IN ============================

# Once per working day (or when AWS says your session expired):
# opens the browser, you sign in as tvelev with password + MFA.
login:
	aws login --profile $(LOGIN_PROFILE)

# Once per hour: asks for your 6-digit MFA code and unlocks the terraform-deployer role.
# Every command below that talks to AWS runs this first, so you rarely type it yourself.
auth:
	@aws sts get-caller-identity --profile $(ROLE_PROFILE) --query Arn --output text

# ============================ 2. TERRAFORM ============================

# Downloads the AWS plugin Terraform needs into infra/.terraform. Safe to run any time.
# It does not touch your files, your state or anything in AWS.
init:
	cd infra && terraform init

# Shows what Terraform WOULD change. Changes nothing.
plan: auth
	cd infra && $(WITH_ROLE) terraform plan

# Applies your .tf changes to AWS. Terraform prints its plan and waits for you to type "yes".
apply: auth
	cd infra && $(WITH_ROLE) terraform apply

# Creates ONLY the ECR repository (the "shelf" for Docker images), so images can be uploaded
# before everything else is built. Used as the first step of "make up".
ecr: auth
	cd infra && $(WITH_ROLE) terraform apply -target=aws_ecr_repository.lambda_repo

# ============================ 3. DOCKER IMAGES ============================

# Logs Docker in to your ECR repository (the login lasts about 12 hours)
ecr-login: auth
	aws ecr get-login-password --region $(REGION) --profile $(ROLE_PROFILE) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(REGION).amazonaws.com

# Builds and uploads the Lambda image
push-lambda: ecr-login
	docker build --provenance=false -t $(ECR_BASE):master-latest -f lambda.Dockerfile .
	docker push $(ECR_BASE):master-latest

# Builds and uploads the dbt image
push-dbt: ecr-login
	docker build --provenance=false -t $(ECR_BASE):dbt-latest -f dbt-fargate.Dockerfile .
	docker push $(ECR_BASE):dbt-latest

# ============================ 4. EVERYDAY SHORTCUTS ============================

# You changed the Python/Lambda code: upload the new image, then apply
deploy-lambda: push-lambda
	cd infra && $(WITH_ROLE) terraform apply

# You changed the dbt project: upload the new image, then apply
deploy-dbt: push-dbt
	cd infra && $(WITH_ROLE) terraform apply

# BUILD EVERYTHING FROM NOTHING: ECR repository -> both images -> all the rest
up: ecr push-lambda push-dbt
	cd infra && $(WITH_ROLE) terraform apply

# TEAR EVERYTHING DOWN: destroys what Terraform built (the S3 data lake is NOT included,
# it stays), deletes the Lambda log groups Terraform did not know about, then runs "audit".
down: auth
	cd infra && $(WITH_ROLE) terraform destroy
	$(MAKE) clean-logs
	$(MAKE) audit

# ============================ 5. CLEAN-UP AND CHECKS ============================

# Lambda creates its own log groups the first time it runs, so Terraform does not know
# about them and "destroy" leaves them behind. This deletes them.
clean-logs:
	@for p in /aws/lambda/extract_and_load_ /aws/lambda/reset_raw_notion_dates; do \
	  for g in $$(aws logs describe-log-groups --region $(REGION) --profile $(ROLE_PROFILE) --log-group-name-prefix $$p --query 'logGroups[].logGroupName' --output text); do \
	    echo "deleting log group $$g"; \
	    aws logs delete-log-group --region $(REGION) --profile $(ROLE_PROFILE) --log-group-name $$g; \
	  done; \
	done

# Read-only. Lists anything from this project that still exists in AWS (and could cost money).
# After "make down", every section below should print nothing. Uses your normal login.
# It deliberately ignores things that are not ours or are free and automatic: your Databricks
# Lambda functions and logs, the shared /aws-glue/crawlers log group, and the
# StepFunctionsGetEventsForECSTaskRule rule that Step Functions creates by itself (it is free).
audit:
	@echo "== Resources tagged Project=budget-manager"
	@aws resourcegroupstaggingapi get-resources --region $(REGION) --profile $(LOGIN_PROFILE) --tag-filters Key=Project,Values=budget-manager --query 'ResourceTagMappingList[].ResourceARN' --output text
	@echo "== RDS instances";       aws rds describe-db-instances --region $(REGION) --profile $(LOGIN_PROFILE) --query 'DBInstances[].DBInstanceIdentifier' --output text
	@echo "== ECS clusters";        aws ecs list-clusters --region $(REGION) --profile $(LOGIN_PROFILE) --query 'clusterArns' --output text
	@echo "== Lambda functions";    aws lambda list-functions --region $(REGION) --profile $(LOGIN_PROFILE) --query "Functions[?starts_with(FunctionName,'extract_and_load_') || FunctionName=='reset_raw_notion_dates'].FunctionName" --output text
	@echo "== Step Functions";      aws stepfunctions list-state-machines --region $(REGION) --profile $(LOGIN_PROFILE) --query 'stateMachines[].name' --output text
	@echo "== EventBridge rules";   aws events list-rules --region $(REGION) --profile $(LOGIN_PROFILE) --query "Rules[?Name!='StepFunctionsGetEventsForECSTaskRule'].Name" --output text
	@echo "== ECR repositories";    aws ecr describe-repositories --region $(REGION) --profile $(LOGIN_PROFILE) --query 'repositories[].repositoryName' --output text
	@echo "== Glue databases";      aws glue get-databases --region $(REGION) --profile $(LOGIN_PROFILE) --query 'DatabaseList[].Name' --output text
	@echo "== Glue crawlers";       aws glue get-crawlers --region $(REGION) --profile $(LOGIN_PROFILE) --query 'Crawlers[].Name' --output text
	@echo "== Log groups";          aws logs describe-log-groups --region $(REGION) --profile $(LOGIN_PROFILE) --query "logGroups[?starts_with(logGroupName,'/aws/lambda/extract_and_load_') || starts_with(logGroupName,'/aws/lambda/reset_raw_notion_dates') || starts_with(logGroupName,'/ecs/dbt-budget-manager')].logGroupName" --output text
	@echo "== Security groups (non-default)"; aws ec2 describe-security-groups --region $(REGION) --profile $(LOGIN_PROFILE) --query "SecurityGroups[?GroupName!='default'].GroupName" --output text
	@echo "== Elastic IPs";         aws ec2 describe-addresses --region $(REGION) --profile $(LOGIN_PROFILE) --query 'Addresses[].PublicIp' --output text
	@echo "== Project IAM roles (old and new names)"; aws iam list-roles --profile $(LOGIN_PROFILE) --query "Roles[?starts_with(RoleName,'budget-manager-') || RoleName=='dbt-ecs-execution-role' || RoleName=='eventbridge-invoke-sfn-role' || starts_with(RoleName,'AWSGlueServiceRole-Budget')].RoleName" --output text

.PHONY: login auth init plan apply ecr ecr-login push-lambda push-dbt deploy-lambda deploy-dbt up down clean-logs audit