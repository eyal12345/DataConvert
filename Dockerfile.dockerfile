FROM python:3.11

WORKDIR /app

COPY main.py .
COPY src/ ./src
COPY logo.ico .
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
