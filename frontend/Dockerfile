FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY .streamlit .streamlit
# COPY auth.yaml auth.yaml
COPY static static
# COPY .env .env
COPY run_streamlit.py run_streamlit.py
COPY src src

# Define the basic ENTRYPOINT, without specific arguments
ENTRYPOINT ["streamlit", "run", "run_streamlit.py"]

# Optionally, we can define a default CMD as fallback for flexibility
CMD ["--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]


HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
