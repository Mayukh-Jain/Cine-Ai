# 1. Use Python 3.9 image
FROM python:3.9

# 2. Set the working directory inside the container
WORKDIR /code

# 3. Copy requirements and install them
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 4. Copy the rest of the application code
COPY . /code

# 5. Create a non-root user (Security requirement for HF Spaces)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# 6. Set the working directory to the user's home
WORKDIR $HOME/app

# Copy code again to the user's directory specifically
COPY --chown=user . $HOME/app

# 7. Run the application
# IMPORTANT: Hugging Face expects the app to run on port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]