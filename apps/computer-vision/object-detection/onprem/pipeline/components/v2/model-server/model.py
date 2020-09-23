import os
import re
import time
import numpy as np
import argparse
import kfserving
import tensorflow as tf
from kfserving import storage
from tensorflow.python.saved_model import tag_constants

import logging
class KFServing(kfserving.KFModel):

    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.ready = False

        # Load model
        self.base_path="/mnt/models/"
        for tflite in os.listdir(os.path.join(self.base_path, FLAGS.out_dir)):
            if tflite.endswith(".tflite"):
                self.exported_path=os.path.join(self.base_path, FLAGS.out_dir,tflite)
                break
        else:
            raise Exception("Model path not found")

        self.interpreter = tf.lite.Interpreter(model_path=self.exported_path, num_threads=2)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def load(self):
        self.ready = True

    def predict(self, request):

        def inferencing():
            self.interpreter.set_tensor(self.input_details[0]['index'], np.expand_dims(np.asarray(request["instances"]).astype(np.float32), 0))
            self.interpreter.invoke()
            pred = [(self.interpreter.get_tensor(self.output_details[i]['index'])).tolist() for i in range(len(self.output_details))]
            return pred

        strategy = tf.distribute.MirroredStrategy(devices=['/gpu:0'])
        start_time = time.time()
        predictions=strategy.experimental_run_v2(inferencing)
        stop_time = time.time()
        logging.info('predict time: {:.3f}s'.format((stop_time - start_time)))
        return {"predictions": predictions}

    def postprocess(self, request):

        def handle_predictions(predictions, confidence=0.6, iou_threshold=0.5):
            predictions=np.asarray(predictions)
            boxes = predictions[:, :, :4]
            box_confidences = np.expand_dims(predictions[:, :, 4], -1)
            box_class_probs = predictions[:, :, 5:]

            box_scores = box_confidences * box_class_probs
            box_classes = np.argmax(box_scores, axis=-1)
            box_class_scores = np.max(box_scores, axis=-1)
            pos = np.where(box_class_scores >= confidence)

            boxes = boxes[pos]
            classes = box_classes[pos]
            scores = box_class_scores[pos]

            n_boxes, n_classes, n_scores = nms_boxes(boxes, classes, scores, iou_threshold)

            if n_boxes:
               boxes = np.concatenate(n_boxes)
               classes = np.concatenate(n_classes)
               scores = np.concatenate(n_scores)

               return boxes, classes, scores
            else:
               return None, None, None

        def nms_boxes(boxes, classes, scores, iou_threshold):

            nboxes, nclasses, nscores = [], [], []
            for c in set(classes):
                inds = np.where(classes == c)
                b = boxes[inds]
                c = classes[inds]
                s = scores[inds]

                x = b[:, 0]
                y = b[:, 1]
                w = b[:, 2]
                h = b[:, 3]

                areas = w * h
                order = s.argsort()[::-1]

                keep = []
                while order.size > 0:
                    i = order[0]
                    keep.append(i)

                    xx1 = np.maximum(x[i], x[order[1:]])
                    yy1 = np.maximum(y[i], y[order[1:]])
                    xx2 = np.minimum(x[i] + w[i], x[order[1:]] + w[order[1:]])
                    yy2 = np.minimum(y[i] + h[i], y[order[1:]] + h[order[1:]])
 
                    w1 = np.maximum(0.0, xx2 - xx1 + 1)
                    h1 = np.maximum(0.0, yy2 - yy1 + 1)

                    inter = w1 * h1
                    ovr = inter / (areas[i] + areas[order[1:]] - inter)
                    inds = np.where(ovr <= iou_threshold)[0]
                    order = order[inds + 1]

                keep = np.array(keep)

                nboxes.append(b[keep])
                nclasses.append(c[keep])
                nscores.append(s[keep])
            return nboxes, nclasses, nscores

        def load_classes_names(file_name):

            names = {}
            with open(file_name) as f:
                for id, name in enumerate(f):
                    names[id] = name
            return names

        start_time = time.time()
        boxes, classes, scores = handle_predictions(request["predictions"][0],confidence=0.3,iou_threshold=0.5)
        class_names = load_classes_names(os.path.join(self.base_path,"metadata", FLAGS.classes_file))
        classs=[]
        for key in classes:
            classs.append(class_names[key].strip())
        stop_time = time.time()
        logging.info('post process time: {:.3f}s'.format((stop_time - start_time)))
        return {"predictions": [boxes.tolist(), classs, scores.tolist()]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--http_port', default=8080, type=int,
                    help='The HTTP Port listened to by the model server.')
    parser.add_argument('--out_dir', default="model", help='out dir')
    parser.add_argument('--model-name', type=str, help='model name')
    parser.add_argument('--classes_file', default="voc.names", type=str, help='name of the class file')
    FLAGS, _ = parser.parse_known_args()
    model = KFServing(FLAGS.model_name)
    model.load()
    kfserving.KFServer(http_port=FLAGS.http_port).start([model])
