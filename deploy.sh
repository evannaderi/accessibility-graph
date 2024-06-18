#!/bin/bash

# Variables
IMAGE_NAME="chart_app"
DOCKERHUB_USERNAME="your_dockerhub_username"
TAG="latest"

git add .
git commit -m "$1"
git push origin main  # or your current branch

docker-compose build

IMAGE_ID=$(docker images -q ${IMAGE_NAME}_web:latest)

docker tag $IMAGE_ID $DOCKERHUB_USERNAME/$IMAGE_NAME:$TAG

docker login

docker push $DOCKERHUB_USERNAME/$IMAGE_NAME:$TAG
