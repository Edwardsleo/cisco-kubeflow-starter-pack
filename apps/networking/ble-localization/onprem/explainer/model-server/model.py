import os
import re
import numpy as np
import argparse
import kfserving
import tensorflow as tf
from kfserving import storage

_GCS_PREFIX = "gs://"
_S3_PREFIX = "s3://"

class KFServing(kfserving.KFModel):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.ready = False

    def load(self):
        if args.storage_uri.startswith(_GCS_PREFIX) or args.storage_uri.startswith(_S3_PREFIX):
            obj=storage.Storage()
            obj.download(uri=args.storage_uri, out_dir=args.out_dir)
        self.ready = True

    def preprocess(self, request):

        return request['instances']

    def predict(self, request):

        for dir in os.listdir(args.out_dir):
            if re.match('[0-9]',dir):
                exported_path=os.path.join(args.out_dir,dir)
                break
        else:
            raise Exception("Model path not found")

        feature_cols=["b3001", "b3002","b3003","b3004","b3005","b3006","b3007","b3008","b3009","b3010","b3011","b3012","b3013"]
        input={'b3001': [], 'b3002': [], 'b3003': [], 'b3004': [], 'b3005': [], 'b3006': [], 'b3007': [], 'b3008': [], 'b3009': [], 'b3010': [], 'b3011': [], 'b3012': [], 'b3013': []}

        X=request
        if np.ndim(X) != 2:
            for i in range(len(X)):
                input[feature_cols[i]].append(X[i])
        else:
            for i in range(len(X)):
                for j in range(len(X[i])):
                    input[feature_cols[j]].append(X[i][j])

        # Open a Session to predict
        with tf.Session() as sess:
            tf.saved_model.loader.load(sess, [tf.saved_model.tag_constants.SERVING], exported_path)
            predictor= tf.contrib.predictor.from_saved_model(exported_path,signature_def_key='predict')
            output_dict= predictor(input)
        sess.close()
        class_ids=[]
        for id in output_dict["class_ids"]:
            class_ids.append(id[0])
        #return {"predictions":np.array(class_ids).tolist()}
        return {"predictions":output_dict["probabilities"].tolist()}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--http_port', default=8080, type=int,
                    help='The HTTP Port listened to by the model server.')
    parser.add_argument('--storage_uri', help='storage uri for your model')
    parser.add_argument('--out_dir', help='out dir')
    args, _ = parser.parse_known_args()
    model = KFServing("blerssi-model")
    model.load()
    kfserving.KFServer(http_port=args.http_port).start([model])
