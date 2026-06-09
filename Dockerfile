# 1. Use the lightweight Python 3.12 image
FROM python:3.12-slim

# 2. Hugging Face Security Gate: Create a non-root system user named 'user'
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# 3. Set up the working directory inside the home folder of our new user
WORKDIR /home/user/app

# 4. Copy and install our actual requirements manifest
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 5. Copy all your modular python files over with correct user ownerships
COPY --chown=user . .

# 6. Crucial Hugging Face Check: Inform the server we are assigning port 7860
EXPOSE 7860

# 7. Run the main entry point to launch your Telegram listener loop
CMD ["python", "app.py"]