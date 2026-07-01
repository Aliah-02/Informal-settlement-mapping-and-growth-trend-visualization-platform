.PHONY: help clone setup up down logs import test-api shell-db shell-api

help:
	@echo "DarInformal — available commands:"
	@echo "  make setup     Copy .env and build images"
	@echo "  make up        Start full stack (PostGIS + import + API + GeoServer + Nginx)"
	@echo "  make down      Stop all services"
	@echo "  make logs      Tail all container logs"
	@echo "  make import    Re-import GeoJSON into PostGIS"
	@echo "  make test-api  Curl health endpoint"
	@echo "  make shell-db  Open psql shell"

setup:
	cp -n .env.example .env 2>/dev/null || true
	docker compose build

up:
	docker compose up -d
	@echo ""
	@echo "DarInformal is starting..."
	@echo "  Web app:    http://localhost"
	@echo "  API docs:   http://localhost:8000/docs"
	@echo "  GeoServer:  http://localhost:8080/geoserver"
	@echo ""
	@echo "First run imports GeoJSON → PostGIS and configures GeoServer (~2 min)."

down:
	docker compose down

logs:
	docker compose logs -f

import:
	docker compose run --rm data-import

test-api:
	curl -s http://localhost:8000/api/health | python3 -m json.tool

shell-db:
	docker compose exec postgis psql -U darinformal -d darinformal

shell-api:
	docker compose exec api bash
