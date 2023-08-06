# ELASTICSEARCH_CREDS="elastic:changeme"
# KIBANA_HOST="http://localhost:5601"
# Input arguments
KIBANA_HOST=$1
ELASTICSEARCH_CREDS=$2

# *********** Helk log tagging variables ***************

TAG_NAME="SETUP-INDEX_PATTERNS"
HELK_INFO_TAG="HELK-KIBANA-DOCKER-$TAG_NAME-INFO:"
HELK_ERROR_TAG="HELK-KIBANA-DOCKER-$TAG_NAME-ERROR:"

# *********** Variables ***************
TIME_FIELD="@timestamp"
# DEFAULT_INDEX_PATTERN="logs-endpoint-winevent-sysmon-*"
declare -a index_patterns=(
  "logs-*"
  "mitre-attack-*"
)

echo "$HELK_INFO_TAG Creating Kibana index patterns.."
for index_pattern in "${index_patterns[@]}"; do
  while true; do
    echo "$HELK_INFO_TAG Creating index pattern ${index_pattern}.."
    ES_STATUS_CODE="$(
      curl -X POST -s -r -o /dev/null -w "%{http_code}" -u "${ELASTICSEARCH_CREDS}" "$KIBANA_HOST/api/saved_objects/index-pattern/${index_pattern}?overwrite=true" \
        -H 'Content-Type: application/json' \
        -H 'kbn-xsrf: true' \
        -d"{\"attributes\":{\"title\":\"${index_pattern}\",\"timeFieldName\":\"$TIME_FIELD\"}}"
    )"
    if [ "$ES_STATUS_CODE" -eq 200 ]; then
      break
    else
      echo "$HELK_ERROR_TAG Error HTTP code ${ES_STATUS_CODE} while attempting creation of index pattern ${index_pattern}..."
      sleep 2
    fi
  done
done

#!/bin/bash

# HELK script: kibana-import-objects.sh
# HELK script description: Imports all the saved objects back to Kibana.
# HELK build stage: Alpha
# Author: Thomas Castronovo (@troplolBE), Nate Guagenti (@neu5ron)
# License: GPL-3.0

# DIR=./objects
#  location of this script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)/objects"
ARRAY=()

created=0
failed=0

#Function to import files to Kibana
#Argument 1 = File to import
#Argument 2 = Retry of import

function importFile {
  local file=${1}
  local retry=${2}

  response=$(
    curl -sk -XPOST -u "${ELASTICSEARCH_CREDS}" \
      "${KIBANA_HOST}/api/saved_objects/_import?overwrite=true" \
      -H "kbn-xsrf: true" \
      --form file=@"${file}"
  )
  result=$(echo "${response}" | grep -w "success" | cut -d ',' -f 2 | cut -d ':' -f 2 | sed -E 's/[^-[:alnum:]]//g')
  if [[ "${result}" == "true" ]]; then
    created=$((created + 1))
    echo "Successfuly imported ${item} named ${file}"
  else
    if [[ $retry -ne 1 ]]; then
      fail="${DIR}/${item}/${file}"
      ARRAY+=($fail)
    else
      failed=$((failed + 1))
    fi
    echo -e "Failed to import ${item} named ${file}: \n ${response}\n"
  fi
}

echo "Please be patient as we import custom dashboards, visualizations, and searches..."
#Go to the right directory to find objects
cd $DIR

for item in config map canvas-workpad canvas-element lens query index-pattern search visualization dashboard url; do
  cd ${item} 2>/dev/null || continue

  for file in *.ndjson; do
    echo "$file"
    importFile $file 0
  done
  cd ..
done

echo -e "Files that failed:\n${ARRAY[@]}"
echo "Re-trying to import the failed files..."

echo "length of array is ${#ARRAY[@]}"
if [[ "${#ARRAY[@]}" -ne "0" ]]; then
  for file in "${ARRAY[@]}"; do
    echo "${file}"
    importFile $file 1
  done
fi

echo "Created: ${created}"
echo "Failed: ${failed}"
