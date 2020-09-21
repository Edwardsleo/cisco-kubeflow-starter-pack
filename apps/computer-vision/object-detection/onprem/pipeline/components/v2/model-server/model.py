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
from tensorflow.python.saved_model import tag_constants


class KFServing(kfserving.KFModel):

    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.ready = False

    def load(self):
        self.ready = True

    def predict(self, request):

        self.base_path="/mnt/models/"
        for tflite in os.listdir(os.path.join(self.base_path, FLAGS.out_dir)):
            if tflite.endswith(".tflite"):
                exported_path=os.path.join(self.base_path, FLAGS.out_dir,tflite)
                break
        else:
            raise Exception("Model path not found")

        interpreter = tf.lite.Interpreter(model_path=exported_path)
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        interpreter.set_tensor(input_details[0]['index'], np.expand_dims(np.asarray(request["instances"]).astype(np.float32), 0))
        interpreter.invoke()
        predictions = [(interpreter.get_tensor(output_details[i]['index'])).tolist() for i in range(len(output_details))]

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

        boxes, classes, scores = handle_predictions(request["predictions"][0],confidence=0.3,iou_threshold=0.5)
        class_names = load_classes_names(os.path.join(self.base_path,"metadata", FLAGS.classes_file))
        classs=[]
        for key in classes:
            classs.append(class_names[key].strip())
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
