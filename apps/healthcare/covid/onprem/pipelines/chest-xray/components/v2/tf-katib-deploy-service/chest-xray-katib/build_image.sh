#!/bin/bash -e
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

while getopts ":hu:t:i:l:" opt; do
  case "${opt}" in
    h)  echo "-t: tag name"
        echo "-u: user name"
        echo "-i: image name. If provided, project name and tag name are not necessary"
        echo "-l: local image name. Optional. Defaults to 'tf_model_train'"
        exit
      ;;
    u) USER_NAME=${OPTARG}
      ;;    
    t) TAG_NAME=${OPTARG}
      ;;
    i) IMAGE_NAME=${OPTARG}
      ;;
    l) LOCAL_IMAGE_NAME=${OPTARG}
      ;;
    \? ) echo "Usage: cmd [-t] tag [-i] image [-u] user name [l] local image"
      exit
      ;;
  esac
done

set -x
if [ -z "${LOCAL_IMAGE_NAME}" ]; then
  LOCAL_IMAGE_NAME=tf_model_train
fi

if [ -z "${USER_NAME}" ]; then
   echo "Provide Username "
   exit 1
fi

if [ -z "${TAG_NAME}" ]; then
  TAG_NAME=$(date +v%Y%m%d)-$(git describe --tags --always --dirty)-$(git diff | shasum -a256 | cut -c -6)
fi

docker build -t ${USER_NAME}/${LOCAL_IMAGE_NAME}:${TAG_NAME} .
if [ -z "${IMAGE_NAME}" ]; then
  cat ~/my_password.txt | docker login --username ${USER_NAME} --password-stdin
  docker push ${USER_NAME}/${LOCAL_IMAGE_NAME}:${TAG_NAME}
else
  cat ~/my_password.txt | docker login --username ${USER_NAME} --password-stdin	
  docker tag ${USER_NAME}/${LOCAL_IMAGE_NAME}:${TAG_NAME} ${USER_NAME}/${IMAGE_NAME}:${TAG_NAME}
  docker push ${USER_NAME}/${IMAGE_NAME}:${TAG_NAME}
fi
