.PHONY: up down logs update restart config

# Full rebuild — use when code or requirements.txt changed
up:
	DOCKER_BUILDKIT=1 docker compose up -d --build

# No image rebuild — use when you only changed env vars / compose config.
# Recreates the container in seconds instead of minutes.
config:
	docker compose up -d

# Restart the running container without rebuilding or recreating
restart:
	docker compose restart

down:
	docker compose down

logs:
	docker compose logs -f --tail=100

update:
	git pull
	DOCKER_BUILDKIT=1 docker compose up -d --build