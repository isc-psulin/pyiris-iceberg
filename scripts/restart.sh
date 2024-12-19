docker stop iris-ice && docker rm iris-ice
docker image rm iris-ice
rm -rf pyiris-iceberg/
git clone git@github.com:isc-patrick/pyiris-iceberg.git

docker build --tag iris-ice pyiris-iceberg/. --no-cache
docker compose -f pyiris-iceberg/docker-compose.yml up -d

docker exec -it iris-ice /bin/bash