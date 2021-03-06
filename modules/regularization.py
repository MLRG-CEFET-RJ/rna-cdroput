import random
import tensorflow as tf
from tensorflow.keras.layers import Layer

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler


def select_dropout(dropout_opt, include_errors):
    print(f"Selected Dropout: {dropout_opt}")
    if dropout_opt == 'none' or dropout_opt is None:
        return None
    if dropout_opt == 'ErrorBasedDropoutIR':
        return ErrorBasedDropoutIR(include_errors)
    if dropout_opt == 'ErrorBasedDropoutDT':
        return ErrorBasedDropoutDT(include_errors)
    if dropout_opt == 'ErrorBasedInvertedDropout':
        return ErrorBasedInvertedDropout(include_errors)
    if dropout_opt == 'ErrorBasedInvertedRandomDropout':
        return ErrorBasedInvertedRandomDropout(include_errors)


def select_scaler(scaler_opt):
    print(f"Selected Scaler: {scaler_opt}")
    if scaler_opt == 'none' or scaler_opt is None:
        return None
    if scaler_opt == 'StandardScaler':
        return StandardScaler()
    if scaler_opt == 'MinMaxScaler':
        return MinMaxScaler()


class ErrorBasedDropoutIR(Layer):
    def __init__(self, include_errors, **kwargs):
        super(ErrorBasedDropoutIR, self).__init__(**kwargs)
        print('ErrorBasedDropoutIR')
        self.include_errors = include_errors

    def get_config(self):
        return {"include_errors": self.include_errors}

    def call(self, inputs, training=None):
        NUM_BANDS = 5
        NUM_BANDS_N_ERRORS = 10
        ugriz = inputs[:,:NUM_BANDS]
        errs = inputs[:,NUM_BANDS:2*NUM_BANDS]
        expErrs = inputs[:,2*NUM_BANDS:]
        ugriz_n_errors = inputs[:, :NUM_BANDS_N_ERRORS]

        SBANDS = 5
        if self.include_errors:
            SBANDS = 10

        def droppedout_ugriz(ugriz, errs, expErrs):
          ones = tf.ones(shape=(1,SBANDS),dtype=tf.dtypes.float32)
          sfmax = tf.nn.softmax(tf.math.divide(tf.math.subtract(errs, expErrs), errs))
          if self.include_errors:
              sfmax = tf.concat([sfmax, sfmax], axis=1)

          keep_probs = tf.math.subtract(ones, sfmax[0])
          rnd_unif = tf.random.uniform(shape=(1,SBANDS), dtype=tf.dtypes.float32)
          mask = tf.math.greater(keep_probs, rnd_unif)
          casted_mask = tf.cast(mask, dtype=tf.dtypes.float32)
          masked_input = tf.math.multiply(ugriz, casted_mask)
          return masked_input

        if training:
          if self.include_errors:
              output = droppedout_ugriz(ugriz_n_errors, errs, expErrs)
          else:
              output = droppedout_ugriz(ugriz, errs, expErrs)
        else:
          output = ugriz
          if self.include_errors:
              output = ugriz_n_errors

        return output

class ErrorBasedDropoutDT(ErrorBasedDropoutIR):
    def __init__(self, include_errors, **kwargs):
        super(ErrorBasedDropoutDT, self).__init__(include_errors, **kwargs)
        print('ErrorBasedDropoutDT')


class ErrorBasedInvertedDropout(tf.keras.layers.Layer):
    def __init__(self, include_errors, **kwargs):
        super(ErrorBasedInvertedDropout, self).__init__(**kwargs)
        print('ErrorBasedInvertedDropout')
        self.include_errors = include_errors

    def get_config(self):
        return {"include_errors": self.include_errors}

    def call(self, inputs, training=None):
        NUM_BANDS = 5
        NUM_BANDS_N_ERRORS = 10
        ugriz = inputs[:, :NUM_BANDS]
        errs = inputs[:, NUM_BANDS:2 * NUM_BANDS]
        expErrs = inputs[:, 2 * NUM_BANDS:]
        ugriz_n_errors = inputs[:, :NUM_BANDS_N_ERRORS]

        SBANDS = 5
        if self.include_errors:
            SBANDS = 10

        def droppedout_ugriz(ugriz, errs):
            ones = tf.ones(shape=(1, SBANDS), dtype=tf.dtypes.float32)
            sfmax = tf.nn.softmax(tf.math.divide(tf.math.subtract(errs, expErrs), errs))
            if self.include_errors:
                sfmax = tf.concat([sfmax, sfmax], axis=1)

            keep_probs = tf.math.subtract(ones, sfmax[0])
            rnd_unif = tf.random.uniform(shape=(1, SBANDS), dtype=tf.dtypes.float32)
            mask = tf.math.greater(keep_probs, rnd_unif)
            casted_mask = tf.cast(mask, dtype=tf.dtypes.float32)

            masked_input = tf.math.multiply(ugriz, casted_mask)
            keep_probs_mean = tf.math.reduce_mean(keep_probs)
            masked_input = tf.math.divide(masked_input, keep_probs_mean)

            return masked_input

        if training:
            if self.include_errors:
                output = droppedout_ugriz(ugriz_n_errors, errs)
            else:
                output = droppedout_ugriz(ugriz, errs)
        else:
            output = ugriz
            if self.include_errors:
                output = ugriz_n_errors

        return output


class ErrorBasedInvertedRandomDropout(tf.keras.layers.Layer):
    def __init__(self, include_errors, **kwargs):
        super(ErrorBasedInvertedRandomDropout, self).__init__(**kwargs)
        print('ErrorBasedInvertedRandomDropout')
        self.include_errors = include_errors

    def get_config(self):
        return {'include_errors': self.include_errors}

    def call(self, inputs, training=None):
        NUM_BANDS = 5
        NUM_BANDS_N_ERRORS = 10
        ugriz = inputs[:, :NUM_BANDS]
        errs = inputs[:, NUM_BANDS:2 * NUM_BANDS]
        expErrs = inputs[:, 2 * NUM_BANDS:]
        ugriz_n_errors = inputs[:, :NUM_BANDS_N_ERRORS]

        SBANDS = 5
        if self.include_errors:
            SBANDS = 10

        def droppedout_ugriz(ugriz, errs):
            ones = tf.ones(shape=(1, SBANDS), dtype=tf.dtypes.float32)
            sfmax = tf.nn.softmax(tf.math.divide(tf.math.subtract(errs, expErrs), errs))
            if self.include_errors:
                sfmax = tf.concat([sfmax, sfmax], axis=1)

            keep_probs = tf.math.subtract(ones, sfmax[0])
            rnd_unif = tf.random.uniform(shape=(1, SBANDS), dtype=tf.dtypes.float32)
            mask = tf.math.greater(keep_probs, rnd_unif)
            casted_mask = tf.cast(mask, dtype=tf.dtypes.float32)
            masked_input = tf.math.multiply(ugriz, casted_mask)
            keep_probs_mean = tf.math.reduce_mean(keep_probs)
            masked_input = tf.math.divide(masked_input, keep_probs_mean)

            return masked_input

        if training:
            n = random.randint(1, 11)  # sorteia um inteiro entre 1 e 10
            even = n % 2 == 0  # checa se e par

            if even:
                print('Using Custom Dropout')
                if self.include_errors:
                    output = droppedout_ugriz(ugriz_n_errors, errs)
                else:
                    output = droppedout_ugriz(ugriz, errs)

            else:
                print('Dropout off')
                output = ugriz
                if self.include_errors:
                    output = ugriz_n_errors

        else:
            output = ugriz
            if self.include_errors:
                output = ugriz_n_errors

        return output
