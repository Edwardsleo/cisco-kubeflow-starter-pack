#!/bin/bash -e

set -x

while (($#)); do
   case $1 in
     "--data")
       shift
       DATA="$1"
       shift
       ;;
     "--config")
       shift
       CONFIG="$1"
       shift
       ;;
     "--domain")
       shift
       DOMAIN="$1"
       shift
       ;;
     "--out")
       shift
       MODEL="$1"
       shift
       ;;
     "--fixed-model-name")
       shift
       FIXED_MODEL_NAME="$1"
       shift
       ;;
     *)
       echo "Unknown argument: '$1'"
       exit 1
       ;;
   esac
done

cd /ml
rasa train --data ${DATA} --config ${CONFIG} --domain ${DOMAIN} --out ${MODEL} --fixed-model-name ${FIXED_MODEL_NAME} 2>&1 | tee out
accuracy=`grep acc out | tail -1 | awk '{print $(NF)}'`
echo "{\"metrics\": [{\"name\": \"core-accuracy\", \"numberValue\": ${accuracy}, \"format\": \"PERCENTAGE\"}]}" > /mlpipeline-metrics.json
