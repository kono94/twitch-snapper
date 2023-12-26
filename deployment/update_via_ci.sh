#/bin/bash

# Store the current script path
SCRIPT_PATH="$(dirname "$0")/$(basename "$0")"
# Calculate the hash of the current script
current_hash=$(sha256sum "$SCRIPT_PATH" | cut -d ' ' -f 1)

cd "$(dirname "$0")"

# Check if the VERSION argument is provided
if [ -z "$1" ]; then
    echo "Error: VERSION argument not provided."
    echo "Usage: $0 VERSION"
    exit 1
fi

VERSION_TAG=$1

# Fetch tags and checkout the specified version
git fetch --tags
git checkout tags/$VERSION_TAG

# Calculate the hash of the script after checkout
new_hash=$(sha256sum "$SCRIPT_PATH" | cut -d ' ' -f 1)

# Compare the hashes
if [ "$current_hash" != "$new_hash" ]; then
    echo "Script has changed, aborting and calling the new version."
    exec $SCRIPT_PATH "$@"
fi



echo "Provided version is: $VERSION_TAG; Building container..."
docker build -t snapper:$VERSION_TAG ../.

echo "Decypting secrets"
cat .env.compose.encrypted | base64 -d | age --decrypt -i key.txt > .env.compose
cat docker.env.encrypted | base64 -d | age --decrypt -i key.txt > docker.env

echo "Re-starting docker compose"
docker compose up -d
