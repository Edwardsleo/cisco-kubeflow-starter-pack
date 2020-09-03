import os
import re
import numpy as np
import argparse
import kfserving
import tensorflow as tf
from kfserving import storage

physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
import logging
from tensorflow.python.saved_model import tag_constants


class KFServing(kfserving.KFModel):

    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.ready = False

    def load(self):
        self.ready = True

    def predict(self, request):

        for dir in os.listdir(FLAGS.out_dir):
            if re.match('[0-9]',dir):
                for tflite in (os.listdir(os.path.join(FLAGS.out_dir,dir))):
                    logging.info(tflite)
                    if tflite.endswith(".tflite"):
                        exported_path=os.path.join(FLAGS.out_dir,dir,tflite)
                        break
                break
        else:
            raise Exception("Model path not found")

        interpreter = tf.lite.Interpreter(model_path=exported_path)
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        interpreter.set_tensor(input_details[0]['index'], np.asarray(request["instances"]).astype(np.float32))
        interpreter.invoke()
        pred = [(interpreter.get_tensor(output_details[i]['index'])).tolist() for i in range(len(output_details))]
        return {"predictions": pred}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--http_port', default=8080, type=int,
                    help='The HTTP Port listened to by the model server.')
    parser.add_argument('--out_dir', default="/mnt/models/", help='out dir')
    parser.add_argument('--model-name', type=str, help='model name')
    FLAGS, _ = parser.parse_known_args()
    model = KFServing(FLAGS.model_name)
    model.load()
    kfserving.KFServer(http_port=FLAGS.http_port).start([model])
