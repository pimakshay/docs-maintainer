# Deployment and Scaling

This guide provides instructions for deploying and scaling the Documentation Maintainer application using Docker and Docker Compose.

## Prerequisites

Before you begin, ensure you have the following installed on your system:
- Docker
- Docker Compose

## Deployment with Docker

1. Build the Docker Image
`docker build -t fastapi-backend .`

2. Run the container
`docker run -p 8000:8000 fastapi-backend`

## Scalling
Use `docker-compose.yml` to host a multi-container setup where fastapi backend, postgres, and other dbs or frameworks can run.