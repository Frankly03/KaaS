# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the production requirements file into the container at /app
# This version is leaner and optimized for production deployment.
COPY ./requirements.prod.txt /app/requirements.txt

# Install production dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code. These paths are now relative to the 'backend' directory.
COPY ./app /app/app
COPY ./sample_data /app/sample_data

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the app with Gunicorn, a production-ready server.
# Render will automatically map its external port to the one we expose.
CMD ["gunicorn", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000"]

