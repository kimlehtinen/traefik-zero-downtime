ssh $SERVER_USER@$SERVER_IP sed -i "s/website:latest/website:$WEBSITE_VERSION_NAME/g" /home/deploy/website/docker-compose.yml