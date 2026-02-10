FROM python:3.11

WORKDIR /app

RUN apt-get update && \
    apt-get install -y python3-tk xvfb && \
    rm -rf /var/lib/apt/lists/*

COPY main.py .
COPY src/ ./src
COPY logo.ico .
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["xvfb-run", "python", "main.py"]
