# Use the official AWS Lambda Python 3.12 base image
FROM public.ecr.aws/lambda/python:3.12

# Copy requirements file and install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# Copy ALL Python scripts into the Lambda Task Root
COPY src/*.py ${LAMBDA_TASK_ROOT}/

# Notice: REMOVED the CMD line! Terraform will dynamically pass the command.