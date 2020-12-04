##Inference using tflite mode

from absl import app, flags, logging
from absl.flags import FLAGS
import tensorflow as tf
from yolov3_tf2.dataset import transform_images


flags.DEFINE_string('tflite_model', './tflite/yolov3.tflite',
                    'path to saved_model')
flags.DEFINE_string('classes_file', './data/voc.names', 'path to classes file')
flags.DEFINE_string('input_image', './data/street.jpg', 'path to input image')

def main(_argv):
    
    interpreter = tf.lite.Interpreter(model_path=FLAGS.tflite_model)
    interpreter.allocate_tensors()
    logging.info('tflite model loaded')

    input_details = interpreter.get_input_details()

    output_details = interpreter.get_output_details()

    class_names = [c.strip() for c in open(FLAGS.classes_file).readlines()]
    logging.info('classes loaded')

    img = tf.image.decode_image(open(FLAGS.input_image, 'rb').read(), channels=3) 
    img = tf.expand_dims(img, 0)
    img = transform_images(img, 416)
    
    outputs = interpreter.tensor(interpreter.set_tensor(input_details[0]['index'], img))

    interpreter.invoke()

    output_data = interpreter.get_tensor(output_details[0]['index'])
    print("Inferenced output as numpy array\n",output_data)

if __name__ == '__main__':
    app.run(main)
