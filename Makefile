SHELL := /bin/bash
DOCKER_IMAGE=cynnexis/commity

.PHONY: all help test clean

all:
	$(MAKE) help; \
	exit 1

help:
	@echo "Commity Makefile"
	@echo ''
	@echo "This Makefile helps you build and run Commity."
	@echo ''
	@echo "  run                 - Run the script in the current directory. The current branch will be used."
	@echo "  test                - Run the tests."
	@echo "  lint                - Run YAPF to check if the Python scripts are syntaxically correct."
	@echo "  fix-lint            - Run YAPF to fix the lint in the Python files."
	@echo "  clean               - Clean the projects."
	@echo "  docker-build        - Build the Docker image given by the Dockerfile."
	@echo "  docker-down         - Down docker-compose."
	@echo "  docker-test-up      - Use docker-compose to launch the tests."
	@echo "  docker-test-restart - Use docker-compose to restart the tests."
	@echo "  docker-kill         - Stop and remove all containers, dangling images and unused networks and volumes. Be careful when executing this command!"

run:
	@./docker-entrypoint.sh run

test: export TEST_REPO=../git-test-repo
test:
	@./docker-entrypoint.sh test

lint:
	@./docker-entrypoint.sh lint

fix-lint:
	@./docker-entrypoint.sh fix-lint

clean:
	rm -f *.ignore.* o.txt output.txt

docker-build:
	docker build -t $(DOCKER_IMAGE) .

docker-down:
	docker-compose down --remove-orphans --volumes

docker-test-up:
	docker-compose up -d --remove-orphans test lint

docker-test-restart: docker-down
	$(MAKE) docker-test-up

docker-kill:
	docker rm -f $$(docker ps -aq) || docker rmi -f $$(docker images -f "dangling=true" -q) || docker system prune -f
