FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# EXPOSE port 10000 (Render's default public web entry point)
EXPOSE 10000

# WEB ENTRYPOINT: Start uvicorn server on host 0.0.0.0 and port 10000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]