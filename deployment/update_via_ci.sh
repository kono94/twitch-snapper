#/bin/bash

cd "$(dirname "$0")"

# Check if the VERSION argument is provided
if [ -z "$1" ]; then
    echo "Error: VERSION argument not provided."
    echo "Usage: $0 VERSION"
    exit 1
fi

VERSION_TAG=$1

git fetch --tags
git checkout tags/$VERSION_TAG

echo "Provided version is: $VERSION_TAG; Building container..."
docker build -t snapper:$VERSION_TAG ../.

echo "Decypting secrets"
cat .env.compose.encrypted | base64 -d | age --decrypt -i key.txt > .env.compose
cat .docker.env.encrypted | base64 -d | age --decrypt -i key.txt > .docker.env

echo "Re-starting docker compose"
docker compose up -d
