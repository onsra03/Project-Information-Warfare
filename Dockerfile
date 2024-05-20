FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

RUN chmod 755 /app

# RUN groupadd -r onsra -g 433 && \
#     useradd -u 431 -r -g onsra -s /sbin/nologin -c "Docker image user" onsra
# USER onsra

CMD ["python", "app.py"]