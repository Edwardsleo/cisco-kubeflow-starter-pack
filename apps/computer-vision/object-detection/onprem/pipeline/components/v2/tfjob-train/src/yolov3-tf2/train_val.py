## Train the object detection model ( .tf format)

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
flags.DEFINE_string('val_dataset', './data/voc2012_val.tfrecord', 'path to validation dataset')
flags.DEFINE_boolean('tiny', False, 'yolov3 or yolov3-tiny')
flags.DEFINE_string('weights', './checkpoints/yolov3_new.tf','path to weights file')
flags.DEFINE_string('classes', './data/voc.names', 'path to classes file')
flags.DEFINE_enum('mode', 'fit', ['fit', 'eager_fit', 'eager_tf'],
                                  'fit: model.fit, '
                                  'eager_fit: model.fit(run_eagerly=True), '
                                  'eager_tf: custom GradientTape')
flags.DEFINE_enum('transfer', 'fine_tune',
                                  ['none', 'darknet', 'no_output', 'frozen', 'fine_tune'],
                                  'none: Training from scratch, '
                                  'darknet: Transfer darknet, '
                                  'no_output: Transfer all but output, '
                                  'frozen: Transfer and freeze all, '
                                  'fine_tune: Transfer all and freeze darknet only')
flags.DEFINE_integer('size', 416, 'image size')
flags.DEFINE_integer('epochs', 3, 'number of epochs')
flags.DEFINE_integer('batch_size', 32, 'batch size')
flags.DEFINE_float('learning_rate', 1e-5, 'learning rate')
flags.DEFINE_integer('num_classes', 20, 'number of classes in the model')
flags.DEFINE_integer('weights_num_classes', None, 'specify num class for `weights` file if different, '
                                         'useful in transfer learning with different number of classes')
flags.DEFINE_string('saved_model_dir', 'trained_model', 'path to saved model')
flags.DEFINE_integer('samples', 17125, 'No of samples')


# Define YOLO anchors & anchor masks
anchors = yolo_anchors
anchor_masks = yolo_anchor_masks

#Define function to load & batch dataset
def make_datasets_batched():

        

        if FLAGS.dataset:
                   train_dataset = dataset.load_tfrecord_dataset(
                                FLAGS.dataset, FLAGS.classes, FLAGS.size)
                   
        else:
                train_dataset = dataset.load_fake_dataset()
        #train_dataset = train_dataset.shuffle(buffer_size=512)
        train_dataset = train_dataset.shard(NUM_WORKERS, TASK_INDEX)
        #train_dataset = train_dataset.cache()
        train_dataset = train_dataset.batch(GLOBAL_BATCH_SIZE)

        train_dataset = train_dataset.map(lambda x, y: (dataset.transform_images(x, FLAGS.size),
            dataset.transform_targets(y, anchors, anchor_masks, FLAGS.size)))
            
        if FLAGS.val_dataset:
                   val_dataset = dataset.load_tfrecord_dataset(
                             FLAGS.val_dataset, FLAGS.classes, FLAGS.size)
        else:
            val_dataset = dataset.load_fake_dataset()
        val_dataset = val_dataset.shard(NUM_WORKERS, TASK_INDEX)
        val_dataset = val_dataset.batch(FLAGS.batch_size)
        val_dataset = val_dataset.map(lambda x, y: (
        dataset.transform_images(x, FLAGS.size),
        dataset.transform_targets(y, anchors, anchor_masks, FLAGS.size)))


        return train_dataset, val_dataset

#Define function to build & compile model
def build_and_compile_model():

        
        if FLAGS.tiny:
                   model = YoloV3Tiny(FLAGS.size, training=True,
                                   classes=FLAGS.num_classes)
                         
        else:
                   model = YoloV3(FLAGS.size, training=True, classes=FLAGS.num_classes)
                   
        # Configure the model for transfer learning
        if FLAGS.transfer == 'none':
            pass  # Nothing to do

        else:
            # All other transfer require matching classes
            model.load_weights(FLAGS.weights)
            if FLAGS.transfer == 'fine_tune':
                # freeze darknet and fine tune other layers
                darknet = model.get_layer('yolo_darknet')
                freeze_all(darknet)
            elif FLAGS.transfer == 'frozen':
                # freeze everything
                freeze_all(model)


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

               ds_train = make_datasets_batched()[0].repeat()
               ds_train = ds_train.prefetch(
                          buffer_size=tf.data.experimental.AUTOTUNE)
                          
               options_train = tf.data.Options()
               options_train.experimental_distribute.auto_shard_policy = \
                                tf.data.experimental.AutoShardPolicy.DATA
                                
               ds_train = ds_train.with_options(options_train)
               
               ds_val = make_datasets_batched()[1].repeat()
               ds_val = ds_train.prefetch(
                          buffer_size=tf.data.experimental.AUTOTUNE)
                          
               options_val = tf.data.Options()
               options_val.experimental_distribute.auto_shard_policy = \
                                tf.data.experimental.AutoShardPolicy.DATA
                                
               ds_val = ds_val.with_options(options_val)

               
               multi_worker_model = build_and_compile_model()

        callbacks = [
                        ModelCheckpoint('checkpoints_keras/yolov3_train_{epoch}.tf',
                                                        verbose=1, save_weights_only=True),
                    ]

        multi_worker_model.fit(ds_train,
                            epochs=FLAGS.epochs,
                            steps_per_epoch=steps_per_epoch,
                            callbacks=callbacks,
                            verbose=1,
                            validation_data=ds_val)

        def is_chief():
              return TASK_INDEX == 0

        if is_chief():
               model_path = FLAGS.saved_model_dir

        else:
              # Save to a path that is unique across workers.
              model_path = FLAGS.saved_model_dir + '/worker_tmp_' + str(TASK_INDEX)

        multi_worker_model.save(model_path)

if __name__ == "__main__":

          #To decide if a worker is chief, get TASK_INDEX from TF_CONFIG
          tf_config = json.loads(os.environ.get('TF_CONFIG') or '{}')
          
          NUM_WORKERS = len(tf_config['cluster']['worker'])
          
          TASK_INDEX = tf_config['task']['index']
          
          try:
             app.run(main)
          except SystemExit:
             pass
