# Copyright 2018 The Kubeflow Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM debian

RUN apt-get update -q && apt-get upgrade -y && \
    apt-get install -y -qq --no-install-recommends \
      apt-transport-https \
      ca-certificates \
      python3-dev python3-pip python3-setuptools python3-wheel \
      git \
      gnupg \
      lsb-release \
      unzip \
      wget && \
    apt-get update -q
RUN pip3 install minio kubernetes boto3
ADD minio_upload.py /opt 
ADD ./src/deploy.sh /bin/
RUN chmod +x /bin/deploy.sh
ENTRYPOINT ["/bin/deploy.sh"]
