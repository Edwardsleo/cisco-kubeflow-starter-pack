## Object detect the input image based on trained Keras weights

#Import libaries
import time
from absl import app, flags, logging
from absl.flags import FLAGS
import cv2
import numpy as np
import tensorflow as tf
from yolov3_tf2.models import (
    YoloV3, YoloV3Tiny
)
from yolov3_tf2.dataset import transform_images, load_tfrecord_dataset
from yolov3_tf2.utils import draw_outputs

#Define inputs
flags.DEFINE_string('classes_file', '/mnt/metadata/voc.names', 'path to classes file')
flags.DEFINE_string('trained_weights', './checkpoints/yolov3_new.tf',
                    'path to weights file')
flags.DEFINE_integer('input_size', 416, 'resize images to')
flags.DEFINE_string('input_image', './data/dog.jpg', 'path to input image')
flags.DEFINE_string('tfrecord', 'None', 'tfrecord instead of image')
flags.DEFINE_string('output_image', './output1.jpg','path to output image')
flags.DEFINE_integer('num_classes', 20, 'number of classes in the model')


#Define main function for inferencing
def main(_argv):
    physical_devices = tf.config.experimental.list_physical_devices('GPU')
    for physical_device in physical_devices:
        tf.config.experimental.set_memory_growth(physical_device, True)

    yolo = YoloV3(classes=FLAGS.num_classes)

    yolo.load_weights(FLAGS.trained_weights).expect_partial()
    logging.info('weights loaded')

    class_names = [c.strip() for c in open(FLAGS.classes_file).readlines()]
    logging.info('classes loaded')

    if FLAGS.tfrecord!='None':
        dataset = load_tfrecord_dataset(
            FLAGS.tfrecord, FLAGS.classes_file, FLAGS.input_size)
        dataset = dataset.shuffle(512)
        img_raw, _label = next(iter(dataset.take(1)))
    else:
        img_raw = tf.image.decode_image(
            open(FLAGS.input_image, 'rb').read(), channels=3)

    img = tf.expand_dims(img_raw, 0)
    img = transform_images(img, FLAGS.input_size)

    t1 = time.time()
    boxes, scores, classes, nums = yolo(img)
    t2 = time.time()
    logging.info('time: {}'.format(t2 - t1))

    logging.info('detections:')
    for i in range(nums[0]):
        logging.info('\t{}, {}, {}'.format(class_names[int(classes[0][i])],
                                           np.array(scores[0][i]),
                                           np.array(boxes[0][i])))

    img = cv2.cvtColor(img_raw.numpy(), cv2.COLOR_RGB2BGR)
    img = draw_outputs(img, (boxes, scores, classes, nums), class_names)
    cv2.imwrite(FLAGS.output_image, img)
    logging.info('output saved to: {}'.format(FLAGS.output_image))


if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass
