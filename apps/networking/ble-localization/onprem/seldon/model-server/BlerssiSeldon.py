import numpy as np
import seldon_core
from seldon_core.user_model import SeldonComponent
from typing import Dict, List, Union, Iterable
import tensorflow as tf
import os
import re
import logging
import argparse


class BlerssiSeldon(SeldonComponent):
    def __init__(self, model_uri: str = None):
        super().__init__()
        self.model_uri = model_uri
        self.ready = False
        logging.info("Model uri: %s"%self.model_uri)
        self.load()

    def load(self):
        logging.info("load")
        model_file = seldon_core.Storage.download(self.model_uri)
        logging.info("model file: %s"%model_file)
        self.ready = True

    def predict(self, X, feature_names=None):

        for dir in os.listdir("/mnt/models"):
            if re.match('[0-9]',dir):
                exported_path=os.path.join("/mnt/models",dir)
                break
        else:
            raise Exception("Model path not found")

        feature_cols=["b3001", "b3002","b3003","b3004","b3005","b3006","b3007","b3008","b3009","b3010","b3011","b3012","b3013"]
        input={'b3001': [], 'b3002': [], 'b3003': [], 'b3004': [], 'b3005': [], 'b3006': [], 'b3007': [], 'b3008': [], 'b3009': [], 'b3010': [], 'b3011': [], 'b3012': [], 'b3013': []}

        try:
            if not self.ready:
                self.load()
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
            output={}
            output["predictions"]={"probabilities":output_dict["probabilities"].tolist()}
            return np.asarray(output['predictions']["probabilities"])

        except Exception as ex:
            logging.exception("Exception during predict: %s"%ex)
