import random
import tensorflow as tf
from tensorflow.keras.layers import Layer

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler


class ErrorBasedInvertedDropoutV2(Layer):
    def __init__(self, **kwargs):
        super(ErrorBasedInvertedDropoutV2, self).__init__(**kwargs)
        print('ErrorBasedInvertedDropoutV2')

    def call(self, inputs, training=None):
        #input is Tensor
        print(inputs)
        n_bands = 5

        feats = inputs[:, :2 * n_bands]
        errs = inputs[:, n_bands:2 * n_bands]
        exp_errs = inputs[:, 2 * n_bands:]

        SBANDS = 10

        def droppedout_ugriz(feats, errs, exp_errs):
            ones = tf.ones(shape=(1, SBANDS), dtype=tf.dtypes.float32)
            sfmax = tf.nn.softmax(tf.math.divide(tf.math.subtract(errs, exp_errs), errs))
            sfmax = tf.concat([sfmax, sfmax], axis=1)

            keep_probs = tf.math.subtract(ones, sfmax[0])
            rnd_unif = tf.random.uniform(shape=(1, SBANDS), dtype=tf.dtypes.float32)
            mask = tf.math.greater(keep_probs, rnd_unif)
            casted_mask = tf.cast(mask, dtype=tf.dtypes.float32)

            masked_input = tf.math.multiply(feats, casted_mask)
            keep_probs_mean = tf.math.reduce_mean(keep_probs)
            masked_input = tf.math.divide(masked_input, keep_probs_mean)

            return masked_input

        if training:
            output = droppedout_ugriz(feats, errs, exp_errs)
        else:
            output = feats

        return output


###############################
#######    OLD STUFF   ########
###############################


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
    if dropout_opt == 'EBasedInvDynamicDp':
        return EBasedInvDynamicDp(include_errors)
    if dropout_opt == 'ErrorOnlyDropout':
        return ErrorOnlyDropout()


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


class ErrorBasedInvertedDropout(Layer):
    #def __init__(self, **kwargs):
    #    super(ErrorBasedInvertedDropout, self).__init__(**kwargs)
    #    print('ErrorBasedInvertedDropout')
    #    self.include_errors = False

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

        def droppedout_ugriz(ugriz, errs, expErrs):
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
                output = droppedout_ugriz(ugriz_n_errors, errs, expErrs)
            else:
                output = droppedout_ugriz(ugriz, errs, expErrs)
        else:
            output = ugriz
            if self.include_errors:
                output = ugriz_n_errors

        return output


class ErrorBasedInvertedRandomDropout(Layer):
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
            # contar os 1s ou 0s do mask
            # disc pra ugriz: acumula 0s em cada banda

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
                    if output != ugriz:
                        print('#dropout_used')
                else:
                    output = droppedout_ugriz(ugriz, errs)
                    nonzero = tf.math.count_nonzero(output - ugriz)
                    tf.keras.backend.print_tensor(nonzero)

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


class EBasedInvDynamicDp(Layer):
    def __init__(self, include_errors, **kwargs):
        super(EBasedInvDynamicDp, self).__init__(**kwargs)
        print('EBasedInvDynamicDp')
        self.include_errors = include_errors

    def get_config(self):
        return {'include_errors': self.include_errors}

    def call(self, inputs, training=None):
        NUM_BANDS = 5
        NUM_BANDS_N_ERRORS = 10
        ugriz = inputs[:, :NUM_BANDS]
        errs = inputs[:, NUM_BANDS:2 * NUM_BANDS]
        exp_ugriz = inputs[:, 3 * NUM_BANDS:]
        exp_errs = inputs[:, 2*NUM_BANDS:3 * NUM_BANDS]
        ugriz_n_errors = inputs[:, :NUM_BANDS_N_ERRORS]
        exp_ugriz_n_errors = tf.concat([exp_ugriz, exp_errs], axis=1)

        SBANDS = 5
        if self.include_errors:
            SBANDS = 10

        def droppedout_ugriz(ugriz, errs):
            ones = tf.ones(shape=(1, SBANDS), dtype=tf.dtypes.float32)
            sfmax = tf.nn.softmax(tf.math.divide(tf.math.subtract(errs, exp_errs), errs))
            if self.include_errors:
                sfmax = tf.concat([sfmax, sfmax], axis=1)

            # -- mascarando os erros ---
            keep_probs = tf.math.subtract(ones, sfmax[0])
            rnd_unif = tf.random.uniform(shape=(1, SBANDS), dtype=tf.dtypes.float32)
            mask = tf.math.greater(keep_probs, rnd_unif)
            casted_mask = tf.cast(mask, dtype=tf.dtypes.float32)
            if self.include_errors:
                masked_input_err = tf.math.multiply(ugriz_n_errors, casted_mask)
            else:
                masked_input_err = tf.math.multiply(ugriz, casted_mask)

            # -- mascarando os ugriz ---
            zeros = tf.zeros(shape=(1, SBANDS), dtype=tf.dtypes.float32)
            casted_mask_mag = tf.where(casted_mask == 1.0, zeros , ones)
            if self.include_errors:
                masked_input_mag = tf.math.multiply(exp_ugriz_n_errors, casted_mask_mag)
            else:
                masked_input_mag = tf.math.multiply(exp_ugriz, casted_mask_mag)

            # -- juntando ---
            masked_input = tf.math.add(masked_input_err, masked_input_mag)

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


class ErrorOnlyDropout(Layer):
    def __init__(self, **kwargs):
        super(ErrorOnlyDropout, self).__init__(**kwargs)
        print('ErrorOnlyDropout')

    def call(self, inputs, training=None):
        dim = tf.shape(inputs)[0]
        NUM_BANDS = 5
        NUM_BANDS_N_ERRORS = 10
        errs = inputs[:, NUM_BANDS:2 * NUM_BANDS]
        exp_errs = inputs[:, 2 * NUM_BANDS:3 * NUM_BANDS]
        ugriz_n_errors = inputs[:, :NUM_BANDS_N_ERRORS]
        ids = tf.cast(inputs[:, -1], tf.int64)

        def droppedout_errs(ugriz, errs):
            ones = tf.ones(shape=(dim, 5), dtype=tf.dtypes.float32)
            sfmax = tf.nn.softmax(tf.math.divide(tf.math.subtract(errs, exp_errs), errs))

            # -- mascarando os erros ---
            keep_probs = tf.math.subtract(ones, sfmax[0])
            #rnd_unif = tf.random.uniform(shape=(dim, 5), dtype=tf.dtypes.float32)
            rnd_unif = tf.random.normal(shape=(dim, 5), dtype=tf.dtypes.float32)
            mask = tf.math.greater(keep_probs, rnd_unif)
            #mask = tf.math.less_equal(keep_probs, rnd_unif)
            casted_mask = tf.cast(mask, dtype=tf.dtypes.float32)

            # -- preservando ugriz --
            casted_mask = tf.concat([ones, casted_mask], axis=1)
            masked_input_err = tf.math.multiply(ugriz, casted_mask)

            # -- trocando pelos erros exp
            zeros10 = tf.zeros(shape=(dim, 10), dtype=tf.dtypes.float32)
            ones10 = tf.ones(shape=(dim, 10), dtype=tf.dtypes.float32)
            casted_mask_err_exp = tf.where(casted_mask == 1.0, zeros10, ones10)

            ugriz_only = inputs[:, :NUM_BANDS]
            ugriz_n_exp_errs = tf.concat([ugriz_only, exp_errs], axis=1)
            masked_err_exp = tf.math.multiply(ugriz_n_exp_errs, casted_mask_err_exp)

            # -- juntando ---
            masked_input = tf.math.add(masked_input_err, masked_err_exp)

            # print ids
            ids10= tf.repeat(tf.reshape(ids, [dim, 1]), 10, axis=1)
            id_masks = tf.where(casted_mask == 0, ids10, 0)

            # print changed
            #changed_val = tf.add(tf.add(
            #    tf.strings.as_string(masked_input_err),
            #    ' -> '),
            #    tf.strings.as_string(masked_err_exp),
            #)
            #changed_val_log = tf.where(casted_mask == 0, changed_val, 'NA')

            return masked_input, id_masks#, changed_val_log

        if training:
            output, _ = droppedout_errs(ugriz_n_errors, errs)
        else:
            if inputs.shape[1] == 16 :
                tf.print('[Prediction Outliers]', output_stream='file://pred_id.log')
                output, id_masks = droppedout_errs(ugriz_n_errors, errs)

                tf.print(tf.strings.format("id: {}", (id_masks), summarize=-1),
                         summarize=-1,
                         output_stream='file://pred_id.log'
                )

                #tf.print(tf.strings.format("changes: {}", (change_log), summarize=-1),
                #         summarize=-1,
                #         output_stream='file://changes.log'
                #)

            else:
                output, _ = droppedout_errs(ugriz_n_errors, errs)

        return output

