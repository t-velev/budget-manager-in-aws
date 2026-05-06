# Use the official AWS Lambda Python 3.12 base image
FROM public.ecr.aws/lambda/python:3.12

# Copy requirements file and install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python scripts into the Lambda Task Root
COPY src/extract_and_load_account.py ${LAMBDA_TASK_ROOT}
COPY src/ntn_utils.py ${LAMBDA_TASK_ROOT}

# Tell Lambda which function to trigger when it wakes up
# Format: filename.function_name
CMD [ "extract_and_load_account.lambda_handler" ]