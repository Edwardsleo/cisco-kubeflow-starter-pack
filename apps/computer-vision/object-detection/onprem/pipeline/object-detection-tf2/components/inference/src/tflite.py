import tensorflow as tf
from absl import app
from absl import flags
FLAGS = flags.FLAGS

flags.DEFINE_string(
    'saved_model_path', None,
    'Path to saved model')

def main(argv):

    saved_model_dir = FLAGS.saved_model_path
    print(saved_model_dir)

    # Convert the model
    converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir+"saved_model") # path to the SavedModel directory
    tflite_model = converter.convert()

    # Save the model.
    with open(saved_model_dir+'model.tflite', 'wb') as f:
        f.write(tflite_model)

if __name__ == '__main__':
  app.run(main)
