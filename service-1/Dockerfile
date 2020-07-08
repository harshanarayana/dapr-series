FROM harshanarayana/dapr-series-python-base:latest as base

COPY app.py /app.py
RUN chmod 755 /app.py

ENTRYPOINT ["python", "/app.py"]

