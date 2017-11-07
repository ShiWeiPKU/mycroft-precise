#!/usr/bin/env python3
#
# Attribution: This script was adapted from https://github.com/amir-abdi/keras_to_tensorflow
#
# Copyright (c) 2017 Mycroft AI Inc.

import sys
sys.path += ['.']

import argparse
import os
from os.path import split, isfile

from shutil import copyfile


def convert(model_path, out_file):
    """
    Converts an HD5F file from Keras to a .pb for use with TensorFlow

    Args:
        model_path (str): location of Keras model
          out_file (str): location to write protobuf
    """
    print('Converting', model_path, 'to', out_file, '...')

    import tensorflow as tf
    from keras.models import load_model
    from keras import backend as K

    out_dir, filename = split(out_file)
    out_dir = out_dir or '.'
    os.makedirs(out_dir, exist_ok=True)

    K.set_learning_phase(0)
    model = load_model(model_path)

    out_name = 'net_output'
    tf.identity(model.output, name=out_name)
    print('Output node name:', out_name)
    print('Output folder:', out_dir)

    sess = K.get_session()

    # Write the graph in human readable
    tf.train.write_graph(sess.graph.as_graph_def(), out_dir, filename + 'txt', as_text=True)
    print('Saved readable graph to:', filename + 'txt')

    # Write the graph in binary .pb file
    from tensorflow.python.framework import graph_util
    from tensorflow.python.framework import graph_io

    cgraph = graph_util.convert_variables_to_constants(sess, sess.graph.as_graph_def(), [out_name])
    graph_io.write_graph(cgraph, out_dir, filename, as_text=False)

    if isfile(model_path + '.params'):
        copyfile(model_path + '.params', out_file + '.params')

    print('Saved graph to:', filename)

    del sess

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert keyword model from Keras to TensorFlow')
    parser.add_argument('--model','-m', default='keyword.net', help='Input Keras model', type=argparse.FileType())
    parser.add_argument('--out', '-o', default='keyword.pb', help='Output TensorFlow protobuf')
    args = parser.parse_args()

    convert(args.model.name, args.out)