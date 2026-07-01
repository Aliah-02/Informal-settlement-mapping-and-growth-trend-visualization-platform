# Render Dockerfile — use when Root Directory is the repository root (empty)
# Builds the FastAPI backend from Dar-informal-settlements-webGIS/backend/

FROM python:3.12-slim

WORKDIR /app

ARG APP_REVISION=2026-07-01-v4-root
RUN echo "Build revision: ${APP_REVISION}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV GDAL_CONFIG=/usr/bin/gdal-config
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY Dar-informal-settlements-webGIS/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Dar-informal-settlements-webGIS/backend/ .
RUN chmod +x start.sh

EXPOSE 10000

CMD ["bash", "/app/start.sh"]
