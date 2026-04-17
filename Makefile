.PHONY: start generate pipeline clean run

start:
	docker compose up -d

generate:
	./message-generators/darwin

pipeline:
	python src/main.py

clean:
	docker compose down

run: start
	sleep 5
	make generate
	sleep 5
	make pipeline