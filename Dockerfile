# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy project files into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Waitress will run on
EXPOSE 8080

# Set the command to run your application with Waitress
CMD ["waitress-serve", "--port=8080", "run:app"]
