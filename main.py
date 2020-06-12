import math
import os
import argparse

from numpy.random import seed
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.callbacks import ModelCheckpoint

from modules import dataset_handle as dh
from modules import training as t
from modules import regularization as reg


def build_d(x_train, y_train, x_test, y_test, x_val, y_val, scaler):
    d = {}
    d.x_train = x_train
    d.y_train = y_train
    d.x_test = x_test
    d.y_test = y_test
    d.x_val = x_val
    d.y_val = y_val
    d.scaler = scaler

    return d


def build_cfg(D, neurons_0, neurons_1, learning_rate, epochs, num_runs):
    model_dir = '.'
    patience = int(0.2 * epochs)
    best_weights_filepath = os.path.join(model_dir, 'model_weights.hdf5')
    earlyStopping = EarlyStopping(monitor='val_loss', mode='min', patience=patience)

    mcp_save = ModelCheckpoint(
        monitor='val_loss', mode='min', filepath=best_weights_filepath, save_best_only=True
    )

    callbacks = [earlyStopping, mcp_save]
    device_name = tf.test.gpu_device_name()

    cfg = {}
    cfg.device_name = device_name
    cfg.callback = callbacks
    cfg.learning_rate = learning_rate
    cfg.epochs = epochs
    cfg.D = D
    cfg.l1_units = neurons_0
    cfg.l2_units = neurons_1
    cfg.num_runs = num_runs

    return cfg


def parser():
   parser = argparse.ArgumentParser(description='RNA Experiments')
   parser.add_argument('e', metavar='EPOCHS', help='Epochs.')
   parser.add_argument('dp', metavar='DROPOUT', help='Dropout class to use.')
   parser.add_argument('runs', metavar='RUNS', help='Total runs.')
   parser.add_argument('lr', metavar='LR', help='Learning rate.')
   parser.add_argument('f', metavar='NF', help='Number of features.')
   parser.add_argument('dataset', metavar='DS', help='Dataset to use [teddy|happy|kaggle|kaggle_bkp].')

   return parser



if __name__ == '__main__':
    parser = parser()
    args = parser.parse_args()

    dataset_name = args.dataset
    dropout_opt = args.dp
    num_runs = args.runs
    epochs = args.e
    learning_rate = args.lr
    num_features = args.f

    seed(42)
    tf.random.set_seed(42)

    dh.download_data(dataset_name)
    df = dh.load_dataframe(dataset_name)
    x_train, y_train, x_test, y_test, x_val, y_val, scaler = dh.build_dataset(df, num_features, norm=True)

    print('x_train.shape: ', x_train.shape)
    print('x_test.shape: ', x_test.shape)
    print('x_val.shape: ', x_val.shape)

    N = x_train.shape[0] # number of data points (train)
    D = x_train.shape[1]  # number of features

    neurons_0 = math.ceil(2*D/3)
    neurons_1 = math.ceil(D/2)

    print(f'dim: {D} for hl_0[{neurons_0}], hl_1[{neurons_1}]')

    d = build_d(x_train, y_train, x_test, y_test, x_val, y_val, scaler)
    cfg = build_cfg(D, neurons_0, neurons_1, learning_rate, epochs, num_runs)
    dropout = reg.select_dropout(dropout_opt)

    model, hist, all_scores = t.do_training_runs(d, cfg, dropout)

    outputs = model.predict(x_test)

    # epoch x loss (mse)
    plt.plot(
        [x for x in range(0, len(hist.history['mse']))],
        hist.history['mse'],
        hist.history['val_mse']
    )
    plt.legend(['train', 'val'])
    plt.show()
