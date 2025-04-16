
FROM python:3.13-alpine

WORKDIR /app

# Update and install necessary packages using apk
RUN apk update && apk add --no-cache \
    build-base \
    curl \
    git


# Clone the repository
RUN git clone https://github.com/tant/learn-deepface.git .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose the Streamlit port
EXPOSE 8501

# Add a healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Set the entrypoint to run the Streamlit app
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]