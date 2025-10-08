# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the production requirements file into the container at /app
COPY ./requirements.prod.txt /app/requirements.txt

# Install production dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code. These paths are relative to the 'backend' directory.
COPY ./app /app/app
COPY ./sample_data /app/sample_data

# EXPOSE is now more of a documentation step; the critical part is the CMD.
EXPOSE 8000

# Run the app with Gunicorn, using the $PORT variable provided by Render.
CMD ["gunicorn", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:$PORT"]

