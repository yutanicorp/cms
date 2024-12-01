# Content Moderation System

This project provides a system that processes and scores messages to identify users who post offensive comments. 
It generates a report with each user's offensive score.

## Installation

### Docker

Ensure Docker is correctly installed by running:

```bash
docker --version
docker run hello-world
```

## Preparation

Place the input CSV file in the `input-files` folder, naming it `input.csv`.

## Execution

Navigate to the directory containing the `docker-compose` file, located in the project's root:

```bash
docker compose up --build
```

This command will launch three services: a scoring service, a translation service, and the user flag application. 
It will generate a report, stored in the `output-files` folder, displaying each user's offensive score

## Test Changes

To ensure the integrity of new changes in the repository, you can utilize the `pytest` framework within Docker containers. 
Ensure the Docker containers are running by starting them as needed.

### Run Tests

#### User Flag App Service

To execute tests for the User Flag App service, use the following command:

```bash
docker exec -it user-flag-app-service pytest
```

#### API Scoring Service

To run tests for the API Scoring service:

```bash
docker exec -it api-scoring-service pytest
```

#### API Translation Service

To conduct tests for the API Translation service:

```bash
docker exec -it api-translation-service pytest
```

