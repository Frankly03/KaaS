# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Best Practice: Copy only the requirements file first to leverage Docker's build cache.
# This prevents re-installing dependencies every time you change your code.
COPY ./requirements.txt /app/requirements.txt

# Install production dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Now copy the rest of your application code
COPY ./app /app/app
COPY ./sample_data /app/sample_data

# EXPOSE is good for documentation but doesn't affect Render's port mapping
EXPOSE 8000

# --- THE FIX IS HERE ---
# Use the "shell form" (no brackets) to enable shell processing for the $PORT variable.
CMD gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT
