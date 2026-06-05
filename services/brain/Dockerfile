FROM python:3.12-slim

WORKDIR /opt/jarvis

COPY services/brain/requirements.txt services/brain/requirements.txt
RUN pip install --no-cache-dir -r services/brain/requirements.txt

COPY services/brain/app services/brain/app
COPY contracts contracts
COPY runtime runtime

WORKDIR /opt/jarvis/services/brain

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
