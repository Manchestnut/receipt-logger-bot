# 1. Use an official, lightweight Python runtime
FROM python:3.12-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy our requirements manifest first to optimize Docker build speed
COPY requirements.txt .

# 4. Install all packages cleanly with no cache clutter
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy all files (app.py, modules, and subfolders) into the container
COPY . .

# 6. Run the main entry point to launch the bot loop
CMD ["python", "app.py"]