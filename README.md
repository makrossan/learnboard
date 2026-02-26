# Despliegue con Docker

cd ~/learnboard
docker build -t learnboard .
docker run -p 5000:5000 -v learnboard_data:/app/instance learnboard
