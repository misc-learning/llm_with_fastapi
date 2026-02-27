FROM python:3.10-slim

WORKDIR /app
#TODO change it for uv
COPY requirements.txt .
RUN pip install --nocache-dir -r requirements.txt

# copy all py files
COPY *.py .

# Copy static files and template
COPT static/ ./static/

RUN mkdir -p /app/data

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]