# 1. Use the official, lightweight Python 3.12 image
FROM python:3.12-slim

# 2. Set the default working directory inside the container
WORKDIR /app

# 3. Copy our requirements manifest first to optimize build cache
COPY requirements.txt .

# 4. Install all Python packages cleanly with no cache clutter
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy all your modular code files and assets into the app folder
COPY . .

# 6. Run the main entry point to start the continuous bot polling loop
CMD ["python", "app.py"]