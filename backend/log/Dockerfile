FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt requirements.txt

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy the source code to the container
COPY . .

# Expose the port the app runs on
EXPOSE 5002

# Run the application
CMD ["python", "app.py"]