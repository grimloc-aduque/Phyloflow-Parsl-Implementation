
VERSION=v7

docker build -t grimloc13/phyloflow-parsl:$VERSION -f ./parsl/dockerfile .

docker run -d --name phyloflow-$VERSION -it grimloc13/phyloflow-parsl:$VERSION /bin/bash

docker exec -it phyloflow-$VERSION /bin/bash

docker exec -it phyloflow-$VERSION /bin/bash /phyloflow/parsl/entrypoint.sh

