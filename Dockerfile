# 1. Use the official Python 3.13 computer environment
FROM python:3.13-slim

# 2. Set the folder inside the container where our code will live
WORKDIR /app

# 3. Copy your project files from your Windows computer into the container
COPY . .

# 4. Upgrade pip and install packages with a longer timeout to stop internet drops
RUN pip install --upgrade pip
RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt

# 5. Open port 8000 so we can access our web interface
EXPOSE 8000

# 6. The exact command to turn on your FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
