
VERSION=v9

docker build -t grimloc13/phyloflow-parsl:$VERSION -f ./parsl/docker/dockerfile .

docker run -d --name phyloflow-$VERSION -it grimloc13/phyloflow-parsl:$VERSION /bin/bash

docker start phyloflow-$VERSION

# docker exec -it phyloflow-$VERSION /bin/bash

docker exec -it phyloflow-$VERSION /bin/bash /phyloflow/parsl/docker/docker_entrypoint.sh

docker push grimloc13/phyloflow-parsl:$VERSION
