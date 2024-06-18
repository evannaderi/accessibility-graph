#!/bin/bash

# Variables
IMAGE_NAME="accessibility_graph-web"
DOCKERHUB_USERNAME="evanvnaderi"
TAG="latest"

git add .
git commit -m "$1"
git push origin master  # or your current branch

docker-compose build

IMAGE_ID=$(docker images -q ${IMAGE_NAME}_web:latest)

docker tag $IMAGE_ID $DOCKERHUB_USERNAME/$IMAGE_NAME:$TAG

docker login

docker push $DOCKERHUB_USERNAME/$IMAGE_NAME:$TAG
