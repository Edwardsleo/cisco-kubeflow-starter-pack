#!/bin/bash -e
  
set -x

while (($#)); do
   case $1 in
     "--model")
       shift
       MODEL="$1"
       shift
       ;;
     "--stories")
       shift
       STORIES="$1"
       shift
       ;;
     "--out")
       shift
       RESULTS="$1"
       shift
       ;;
     *)
       echo "Unknown argument: '$1'"
       exit 1
       ;;
   esac
done

cd /ml
rasa test --model ${MODEL}  --stories ${STORIES} --out ${RESULTS} 2>&1 | tee out
f1_score=`grep F1-Score out | tail -1 | awk '{print $(NF)}'`
precision=`grep Precision out | tail -1 | awk '{print $(NF)}'`
echo "{\"metrics\": [{\"name\": \"f1-score\", \"numberValue\": ${f1_score}, \"format\": \"PERCENTAGE\"}]}" > /mlpipeline-metrics.json
