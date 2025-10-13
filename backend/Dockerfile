# Use the official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Create a non-root user for security best practices
RUN useradd -ms /bin/bash streamlit
USER streamlit

# Copy the requirements file and install dependencies as the non-root user
COPY --chown=streamlit:streamlit requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy the rest of the application files
COPY --chown=streamlit:streamlit . .

# Expose the port that Streamlit runs on
EXPOSE 8501

# The command to run the Streamlit app
# The --server.runOnSave=true flag is helpful for development
CMD ["python", "-m", "streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
