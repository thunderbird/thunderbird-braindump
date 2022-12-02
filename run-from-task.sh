#!/bin/bash

set -e

TASKID="$1"

taskcluster task def "${TASKID}" > "${TASKID}"

MOZSRC="/home/rob/moz/unified"

IMAGE_TASKID=$(jq -r '.payload.image.taskId' < "$TASKID")

wget -O /tmp/image.tar.zst "https://firefox-ci-tc.services.mozilla.com/api/queue/v1/task/${IMAGE_TASKID}/artifacts/public/image.tar.zst"
tar xvf /tmp/image.tar.zst manifest.json

IMAGE_TAG=$(jq -r '.[].RepoTags[0]' manifest.json)
IMAGE_NAME=$(echo ${IMAGE_TAG} | sed -e 's%^.*/%%' -e 's%:latest$%%')
CONTAINER_NAME="container_$(echo "$IMAGE_NAME" | sed 's/^.*://')"

# ( cd "$MOZSRC"; ./mach -v taskcluster-load-image --task-id "$IMAGE_TASKID" )

zstdcat /tmp/image.tar.zst | docker image load
rm -f manifest.json /tmp/image.tar.zst

_exists=$(docker container ls -a -q -f name="${CONTAINER_NAME}")
if [[ -n "$_exists" ]]; then docker container rm "${_exists}"; fi

docker container create -ti --name "$CONTAINER_NAME" "$IMAGE_NAME" bash --login
docker cp /home/rob/moz/robtools/docker_run_local.py ${CONTAINER_NAME}:/builds/worker/docker_run_local.py
docker cp $TASKID ${CONTAINER_NAME}:/builds/worker

uxterm -e docker start -i -a "$CONTAINER_NAME" &

rm  "${TASKID}"
#sleep 5

docker exec -i "$CONTAINER_NAME" apt install vim
echo 'docker exec  -i "$CONTAINER_NAME"  /builds/worker/docker_run_local.py < "$TASKJSON"'
