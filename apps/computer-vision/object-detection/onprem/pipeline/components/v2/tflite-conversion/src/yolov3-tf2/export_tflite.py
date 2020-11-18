##Convert into tflite model using trained weights

from absl import app, flags, logging
from absl.flags import FLAGS
import numpy as np
import tensorflow as tf
from yolov3_tf2.models import (
    YoloV3, YoloV3Tiny
)

flags.DEFINE_string('trained_weights', './new_checkpt_keras/yolov3_train_3.tf',
                    'path to weights file')
flags.DEFINE_string('tflite_model', './tflite/yolov3.tflite',
                    'path to saved_model')
flags.DEFINE_string('classes_file', './data/voc.names', 'path to classes file')
flags.DEFINE_integer('num_classes', 20, 'number of classes in the model')
flags.DEFINE_integer('input_size', 416, 'image size')

def main(_argv):
    
    yolo = YoloV3(size=FLAGS.input_size, classes=FLAGS.num_classes)

    yolo.load_weights(FLAGS.trained_weights).expect_partial()
    logging.info('weights loaded')

    converter = tf.lite.TFLiteConverter.from_keras_model(yolo)
    converter.target_spec.supported_ops = [
           tf.lite.OpsSet.TFLITE_BUILTINS, # enable TensorFlow Lite ops.
          tf.lite.OpsSet.SELECT_TF_OPS, # enable TensorFlow ops.
                                     ]
    converter.allow_custom_ops = True
    tflite_model = converter.convert()
    open(FLAGS.tflite_model, 'wb').write(tflite_model)
    logging.info("model saved to: {}".format(FLAGS.tflite_model))

    
if __name__ == '__main__':
    app.run(main)
