.PHONY: up down logs update

up:
	DOCKER_BUILDKIT=1 docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=100

update:
	git pull
	DOCKER_BUILDKIT=1 docker compose up -d --buil