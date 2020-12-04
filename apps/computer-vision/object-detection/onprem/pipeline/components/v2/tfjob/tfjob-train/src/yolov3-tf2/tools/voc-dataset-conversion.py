##Python script to convert dataset into tfrecords

#Import libraries
import time
import os
import hashlib
from absl import app, flags, logging
from absl.flags import FLAGS
import tensorflow as tf
import lxml.etree
import tqdm
import re
import shutil
import subprocess
import sys
import pascal_voc_io, yolo_io

#Define input/commandline arguments
flags.DEFINE_string('data_dir', './data/voc2012_raw/VOCdevkit/VOC2012/',
                    'path to raw PASCAL VOC dataset')
flags.DEFINE_string('image_list_file', 'train.txt', 'list of images names')
flags.DEFINE_string('dataset', './data/voc2012_train.tfrecord', 'output dataset')
flags.DEFINE_string('classes_file', './data/voc2012.names', 'classes file')

#Convert annotation to tensorflow examples
def build_example(annotation, class_map):
    img_path = os.path.join(
        FLAGS.data_dir, annotation['filename'])
    img_raw = open(img_path, 'rb').read()
    key = hashlib.sha256(img_raw).hexdigest()

    width = int(annotation['size']['width'])
    height = int(annotation['size']['height'])

    xmin = []
    ymin = []
    xmax = []
    ymax = []
    classes = []
    classes_text = []
    truncated = []
    views = []
    difficult_obj = []
    if 'object' in annotation:
        for obj in annotation['object']:
            difficult = bool(int(obj['difficult']))
            difficult_obj.append(int(difficult))

            xmin.append(float(obj['bndbox']['xmin']) / width)
            ymin.append(float(obj['bndbox']['ymin']) / height)
            xmax.append(float(obj['bndbox']['xmax']) / width)
            ymax.append(float(obj['bndbox']['ymax']) / height)
            classes_text.append(obj['name'].encode('utf8'))
            classes.append(class_map[obj['name']])
            truncated.append(int(obj['truncated']))
            views.append(obj['pose'].encode('utf8'))

    example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': tf.train.Feature(int64_list=tf.train.Int64List(value=[height])),
        'image/width': tf.train.Feature(int64_list=tf.train.Int64List(value=[width])),
        'image/filename': tf.train.Feature(bytes_list=tf.train.BytesList(value=[
            annotation['filename'].encode('utf8')])),
        'image/source_id': tf.train.Feature(bytes_list=tf.train.BytesList(value=[
            annotation['filename'].encode('utf8')])),
        'image/key/sha256': tf.train.Feature(bytes_list=tf.train.BytesList(value=[key.encode('utf8')])),
        'image/encoded': tf.train.Feature(bytes_list=tf.train.BytesList(value=[img_raw])),
        'image/format': tf.train.Feature(bytes_list=tf.train.BytesList(value=['jpeg'.encode('utf8')])),
        'image/object/bbox/xmin': tf.train.Feature(float_list=tf.train.FloatList(value=xmin)),
        'image/object/bbox/xmax': tf.train.Feature(float_list=tf.train.FloatList(value=xmax)),
        'image/object/bbox/ymin': tf.train.Feature(float_list=tf.train.FloatList(value=ymin)),
        'image/object/bbox/ymax': tf.train.Feature(float_list=tf.train.FloatList(value=ymax)),
        'image/object/class/text': tf.train.Feature(bytes_list=tf.train.BytesList(value=classes_text)),
        'image/object/class/label': tf.train.Feature(int64_list=tf.train.Int64List(value=classes)),
        'image/object/difficult': tf.train.Feature(int64_list=tf.train.Int64List(value=difficult_obj)),
        'image/object/truncated': tf.train.Feature(int64_list=tf.train.Int64List(value=truncated)),
        'image/object/view': tf.train.Feature(bytes_list=tf.train.BytesList(value=views)),
    }))
    return example

#Parse annotations in .xml format
#Convert annotations into .xml format & parse, if annotations are available in .txt format
def parse_xml(xml):
    if not len(xml):
        return {xml.tag: xml.text}
    result = {}
    for child in xml:
        child_result = parse_xml(child)
        if child.tag != 'object':
            result[child.tag] = child_result[child.tag]
        else:
            if child.tag not in result:
                result[child.tag] = []
            result[child.tag].append(child_result[child.tag])
    return {xml.tag: result}

#Define Main function
def main(_argv):
    class_map = {name: idx for idx, name in enumerate(
        open(FLAGS.classes_file).read().splitlines())}
    logging.info("Class mapping loaded: %s", class_map)

    writer = tf.io.TFRecordWriter(FLAGS.dataset)
    image_list = open(FLAGS.image_list_file).read().splitlines()
    logging.info("Image list loaded: %d", len(image_list))
    raw_names = []
    for name in tqdm.tqdm(image_list):
        name = re.findall(r'\d+[_-]?\d+',name)
        xml_file = os.path.join(FLAGS.data_dir,(name[0] + '.xml'))
        raw_names.append(name[0])
        if not os.path.exists(xml_file):
            process = subprocess.Popen(['python3', 'tools/yolo2voc.py', FLAGS.data_dir],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            print("Ran successfully")

            shutil.copy(FLAGS.classes_file, (FLAGS.data_dir + '/classes.txt'))

    for raw_name in raw_names:
        annotation_xml = os.path.join(
            FLAGS.data_dir, (raw_name + '.xml'))
        annotation_xml = lxml.etree.fromstring(open(annotation_xml).read())
        annotation = parse_xml(annotation_xml)['annotation']
        tf_example = build_example(annotation, class_map)
        writer.write(tf_example.SerializeToString())
    writer.close()
    logging.info("Done")


if __name__ == '__main__':
    app.run(main)

