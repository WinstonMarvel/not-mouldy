.PHONY: up down logs update

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=100

update:
	git pull
	docker compose up -d --build
