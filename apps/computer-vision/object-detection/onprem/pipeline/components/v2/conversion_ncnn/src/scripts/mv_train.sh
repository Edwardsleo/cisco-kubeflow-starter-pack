#!/bin/bash

dataset_dir=-
aws_profile=merakis3rw

function download_dataset() {
    ddir="$@"
    # clean tmp dir
    if [ -d "$ddir/tmp" ]; then
        rm -rf $ddir/tmp
    fi
    mkdir "$ddir/tmp"
    # load dataset conf file
    if [ ! -f "$ddir/dataset.txt" ]; then
        echo "$ddir/dataset.txt does not exists"
        exit 2
    fi
    while read url; do    
        echo "download $url"
        aws s3 cp --profile merakis3rw $url "$ddir/tmp/" 
        filename=$(basename -- "$url")
        extension="${filename##*.}"
        filename="${filename%.*}"
        echo "extract $filename.$extension file"
        case $extension in
            "xz")
                tar xvf "$ddir/tmp/$filename.$extension" -C $ddir/tmp/
                ;;
            "gz")
                tar xvf "$ddir/tmp/$filename.$extension" -C $ddir/tmp/
                ;;
            "zip")
                unzip "$ddir/tmp/$filename.$extension" -d $ddir/tmp/
                ;;
            *)
                echo "ERROR: unknown extension $extension"
                exit 3
                ;;
        esac
    done < $ddir/dataset.txt
    # rename tmp
    mv "$ddir/tmp" "$ddir/dataset"
}

print_usage() {
    echo "$0 <options> model_name"
    echo "-d | --dataset_dir : dataset directory (Default: Body)"
}


#------------------------------------------------------------------------------
# parse arguments
while [[ "$#" > 0 ]]; do 
    case $1 in
        --d|--ds_dir) 
            dataset_dir="$2"
            shift 2
            ;;
        -h|--help) 
            print_usage
            exit 0
            ;;
        *) 
            POSITIONAL+=("$1")
            shift
            ;;
    esac
done

set -- "${POSITIONAL[@]}" # restore positional parameters

if [[ $# -ne 1 ]]; then
    echo "ERROR: model name must be defined" >&2
    print_usage
    exit 3
fi

model=$1

# check if model config exists
if [ ! -f "models/$model/$model.cfg" ]; then
    echo "ERROR: model config file models/$model/$model.cfg does not exists"  >&2
    exit 2
fi


# check dataset dir
if [ $dataset_dir == "-" ]; then
    # check if dataset downloaded
    if [ ! -d "models/$model/dataset" ]; then
        download_dataset "models/$model"
    fi
fi

# check if darknet installed
if ! [ -x "$(command -v darknet)" ]; then
  echo 'ERROR: darknet is not installed.' >&2
  exit 2
fi

# start training
output_dir="backup/backup_$model"

echo "start darknet training..."
echo "    model:      $model"
echo "    dataset:    $dataset_dir"
echo "    output dir: $output_dir"

if [ ! -d $output_dir ]; then
    mkdir -p $output_dir
fi

echo "darknet detector train models/$model/$model.data models/$model/$model.cfg -gpus 0,1 —map dont_show"
darknet detector train models/$model/$model.data models/$model/$model.cfg -gpus 0,1 -map -dont_show
