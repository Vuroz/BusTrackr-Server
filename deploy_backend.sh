# Remove the current folder.
rm -rf /var/www/BusTrackr-Server

# Start the SSH agent
eval "$(ssh-agent -s)"

# Add your deploy key
ssh-add ~/.ssh/github_deployment_key

# Stop the container.
docker stop bustracker-io-backend

# Remove the container.
docker rm bustracker-io-backend

# Remove the docker image.
docker rmi bustracker-io-backend

# Clone the current repo.
git clone git@github.com:Vuroz/BusTrackr-Server.git /var/www/BusTrackr-Server

# Check if the .env file exists
if [ -f /etc/bustrackr-backend/.env ]; then
    echo "Environment (.env) file already exists."
else
    # Prompt the user to create a new .env file
    echo "Environment (.env) file does not exist. Creating one now..."
    
    # Copy .env.structure to /etc/bustrackr-backend/.env
    cp /var/www/BusTrackr-Server/.env.structure /etc/bustrackr-backend/.env

    # Set permissions for the .env file
    chmod 600 /etc/bustrackr-backend/.env

    # Replace occurrences of {REPLACE_*} in the .env file
    while grep -q "{REPLACE_" /etc/bustrackr-backend/.env; do
        # Extract the first occurrence of {REPLACE_*}
        placeholder=$(grep -o "{REPLACE_[^}]*}" /etc/bustrackr-backend/.env | head -n 1)
        
        # Prompt the user for the replacement value
        echo -n "Enter value for $placeholder: "
        read -s value

        # Escape forward slashes in the user input
        value=$(echo "$value" | sed 's/\//\\\//g')
        
        # Replace the placeholder with the user-provided value
        sed -i "s/$placeholder/$value/g" /etc/bustrackr-backend/.env
    done
fi

# Build and start Docker container.
docker compose -f /var/www/BusTrackr-Server/docker-compose.yml up -d --build