# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install FFmpeg
RUN apt update && apt install -y ffmpeg && apt clean

# Copy requirements and install dependencies
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY ./backend /app

# Expose the Flask port
EXPOSE 5000

# Run the backend server
CMD ["python", "run.py"]
