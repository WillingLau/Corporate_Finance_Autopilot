FROM python:3.10-slim

WORKDIR /workspace

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -U ddgs

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "frontend/ui.py", "--server.port=8501", "--server.address=0.0.0.0"]