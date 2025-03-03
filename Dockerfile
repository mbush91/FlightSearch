FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH="/app"

COPY requirements.txt  .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY templates ./templates

COPY app.py .
COPY flightsearch.py .
# COPY .env .

EXPOSE 5000

# Run the client
CMD ["gunicorn", "-w", "4", "app:app", "-b", "0.0.0.0:5000"]
