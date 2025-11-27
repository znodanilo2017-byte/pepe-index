# Use AWS Lambda Python runtime base image
# This makes deployment to AWS 10x easier than standard python images
FROM public.ecr.aws/lambda/python:3.11

# Copy requirements file
COPY requirements-lambda.txt ${LAMBDA_TASK_ROOT}

# Install packages
RUN pip install -r requirements-lambda.txt

# Copy function code
COPY main.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "main.handler" ]