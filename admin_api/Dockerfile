# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /admin_api

# Copy the requirements file into the container
COPY requirements.txt .

# Copy the current directory contents into the container
COPY . .

# Install the package in development mode
RUN pip install -e .

# Ensure the shared folder is accessible
ENV PYTHONPATH=/admin_api:/admin_api/shared

# Expose the port the app runs on
EXPOSE 8000

# Run the application
# use this for hot reload
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# use this for production
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]