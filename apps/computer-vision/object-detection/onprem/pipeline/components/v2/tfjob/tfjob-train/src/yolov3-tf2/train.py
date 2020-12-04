## Python script to train object detection model

#Import libraries
from absl import app, flags, logging
from absl.flags import FLAGS
import tensorflow as tf
import numpy as np
import cv2
import os
import json
from tensorflow.keras.callbacks import ModelCheckpoint
from yolov3_tf2.models import (
YoloV3, YoloV3Tiny, YoloLoss,
yolo_anchors, yolo_anchor_masks,
yolo_tiny_anchors, yolo_tiny_anchor_masks
)
from yolov3_tf2.utils import freeze_all
import yolov3_tf2.dataset as dataset

#Define Inputs
flags.DEFINE_string('dataset', './data/voc2012_train.tfrecord', 'path to dataset')
#flags.DEFINE_string('val_dataset', './data/voc2012_val.tfrecord', 'path to validation dataset')
flags.DEFINE_string('converted_weights', './checkpoints/yolov3_new.tf','path to weights file')
flags.DEFINE_string('classes_file', './data/voc.names', 'path to classes file')
flags.DEFINE_enum('transfer', 'fine_tune',
                                 ['none', 'fine_tune'],
                                  'none: Training from scratch, '
                                  'fine_tune: Transfer all and freeze darknet only')
flags.DEFINE_integer('input_size', 416, 'image size')
flags.DEFINE_integer('epochs', 3, 'number of epochs')
flags.DEFINE_integer('batch_size', 16, 'batch size')
flags.DEFINE_float('learning_rate', 1e-5, 'learning rate')
flags.DEFINE_integer('num_classes', 20, 'number of classes in the model')
flags.DEFINE_string('saved_model_dir', 'trained_model', 'path to saved model')
flags.DEFINE_integer('samples', 17125, 'No of samples')


# Define YOLO anchors & anchor masks
anchors = yolo_anchors
anchor_masks = yolo_anchor_masks

#Define function to load & batch dataset
def make_datasets_batched():

        
        if FLAGS.dataset:
                   train_dataset = dataset.load_tfrecord_dataset(
                                FLAGS.dataset, FLAGS.classes_file, FLAGS.input_size)
                   
        else:
                train_dataset = dataset.load_fake_dataset()
        train_dataset = train_dataset.shard(NUM_WORKERS, TASK_INDEX)
        train_dataset = train_dataset.batch(GLOBAL_BATCH_SIZE)

        train_dataset = train_dataset.map(lambda x, y: (dataset.transform_images(x, FLAGS.input_size),
            dataset.transform_targets(y, anchors, anchor_masks, FLAGS.input_size)))

        return train_dataset

#Define function to build & compile model
def build_and_compile_model():

        
        model = YoloV3(FLAGS.input_size, training=True, classes=FLAGS.num_classes)
                   
        # Configure the model for transfer learning
        if FLAGS.transfer == 'none':
            pass  # Nothing to do

        else:

            model.load_weights(FLAGS.converted_weights)
            if FLAGS.transfer == 'fine_tune':
                # freeze darknet and fine tune other layers
                darknet = model.get_layer('yolo_darknet')
                freeze_all(darknet)


        optimizer = tf.keras.optimizers.Adam(lr=FLAGS.learning_rate)
        loss = [YoloLoss(anchors[mask], classes=FLAGS.num_classes)
                                                for mask in anchor_masks]

        model.summary()

        model.compile(optimizer=optimizer, loss=loss, run_eagerly=0)


        return model

#Define main function for training model
def main(_argv):

        physical_devices = tf.config.experimental.list_physical_devices('GPU')
        for physical_device in physical_devices:
               tf.config.experimental.set_memory_growth(physical_device, True)

        strategy = tf.distribute.experimental.MultiWorkerMirroredStrategy()
        print('Number of devices: {}'.format(strategy.num_replicas_in_sync))

        global GLOBAL_BATCH_SIZE
        GLOBAL_BATCH_SIZE = FLAGS.batch_size * strategy.num_replicas_in_sync
        
        steps_per_epoch = FLAGS.samples // GLOBAL_BATCH_SIZE
        with strategy.scope():

               ds_train = make_datasets_batched().repeat()
               ds_train = ds_train.prefetch(
                          buffer_size=tf.data.experimental.AUTOTUNE)
                          
               options = tf.data.Options()
               options.experimental_distribute.auto_shard_policy = \
                                tf.data.experimental.AutoShardPolicy.DATA
                                
               ds_train = ds_train.with_options(options)
               
               multi_worker_model = build_and_compile_model()

        callbacks = [
                        ModelCheckpoint((FLAGS.saved_model_dir + '/yolov3_train_{epoch}.tf'),
                                                        verbose=1, save_weights_only=True),
                    ]

        multi_worker_model.fit(ds_train,
                            epochs=FLAGS.epochs,
                            steps_per_epoch=steps_per_epoch,
                            callbacks=callbacks,
                            verbose=1)



if __name__ == "__main__":

          #To decide if a worker is chief, get TASK_INDEX from TF_CONFIG
          tf_config = json.loads(os.environ.get('TF_CONFIG') or '{}')
          
          NUM_WORKERS = len(tf_config['cluster']['worker'])
          
          TASK_INDEX = tf_config['task']['index']
          
          try:
             app.run(main)
          except SystemExit:
             pass
