# Basis-Image: Python 3.11 schlank
FROM python:3.11-slim

# Arbeitsverzeichnis im Container
WORKDIR /app

# System-Updates und Tools (z. B. für curl-basierte Healthchecks)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Requirements installieren
COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY app/mcp_server.py .

# Port für Uvicorn öffnen
EXPOSE 8000

# Healthcheck: prüft, ob App antwortet
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# 🧠 Starte direkt den FastAPI-Server über uvicorn
CMD ["uvicorn", "mcp_server:app", "--host", "0.0.0.0", "--port", "8000"]
