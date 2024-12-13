# Use the official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app


# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt


# Add wait-for-it.sh script
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Copy the application code
COPY . /app/

# Expose the port the app runs on
EXPOSE 5000


# Run the application with seeding
CMD ["/wait-for-it.sh", "timescaledb:5432", "--", "sh", "-c", "python app/database/seed.py && python app/app.py"]