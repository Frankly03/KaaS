# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Best Practice: Copy only the requirements file first to leverage Docker's build cache.
COPY ./requirements.txt /app/requirements.txt

# Install production dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Now copy the rest of your application code
COPY ./app /app/app
COPY ./sample_data /app/sample_data

# EXPOSE is good for documentation
EXPOSE 8000

# --- THE FINAL FIX IS HERE ---
# Use the "shell form" for variable substitution.
# Add the --preload flag to load the model once, before workers start.
# Start with just one worker to be safe on the free tier.
CMD gunicorn -w 1 -k uvicorn.workers.UvicornWorker --preload app.main:app --bind 0.0.0.0:$PORT