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
