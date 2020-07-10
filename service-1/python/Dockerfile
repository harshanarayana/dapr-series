FROM harshanarayana/dapr-series-python-base:latest as base

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY app.py /app.py
RUN chmod 755 /app.py

ENTRYPOINT ["python", "/app.py"]

