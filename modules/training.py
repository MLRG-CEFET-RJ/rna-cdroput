import numpy as np
import pandas as pd
import os
import glob
import time
import datetime

from math import sqrt
from joblib import dump, load

from sklearn.isotonic import IsotonicRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
from sklearn import ensemble

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.callbacks import ModelCheckpoint

from modules.regularization import ErrorBasedDropoutIR
from modules.regularization import ErrorBasedDropoutDT
from modules.regularization import ErrorBasedDropoutZero
from modules.regularization import ErrorBasedInvertedDropout


_MAP_METHOD_NAMES = {
    None : 'RNA',
    'ErrorBasedDropoutIR': 'RNA-RI',
    'ErrorBasedDropoutDT': 'RNA-AD',
    'ErrorBasedInvertedDropout': 'RNA-'
}


def custom_layer_register():
    return {
        "ErrorBasedDropoutIR": ErrorBasedDropoutIR,
        "ErrorBasedDropoutDT": ErrorBasedDropoutDT,
        "ErrorBasedDropoutZero": ErrorBasedDropoutZero,
        "ErrorBasedInvertedDropout": ErrorBasedInvertedDropout
    }


def preds_filename(cfg):
    return f"real_x_pred_{model_name_nmnic(cfg)}_{cfg.args.sc}_{cfg.args.dataset}_epochs_{cfg.epochs}_units_{cfg.args.hl1}_{cfg.args.hl2}"


def hist_filename(cfg, run):
    return f"hist_{model_name_nmnic(cfg)}_{cfg.args.sc}_{cfg.args.dataset}_epochs_{cfg.epochs}_units_{cfg.args.hl1}_{cfg.args.hl2}_run_{run}"


def model_name_nmnic(cfg):
    modelname = _MAP_METHOD_NAMES[cfg.args.dp]
    if cfg.args.ir:
        modelname=f"{modelname}RI-Inv"
    if cfg.args.dt:
        modelname=f"{modelname}AD-Inv"
    if cfg.args.xgbr:
        modelname = 'XGB'
    if not cfg.args.dp:
        modelname = f"{modelname}{cfg.args.f:02d}"

    return modelname


def model_filename(cfg, run):
    modelname = model_name_nmnic(cfg)
    filename = f'model_{modelname}_{cfg.args.dataset}_{cfg.args.sc}_epochs_{cfg.epochs}_units_{cfg.args.hl1}_{cfg.args.hl2}'

    if run is not None:
        filename = f'{filename}_run_{run}'

    return filename


def clean_dir(cfg, run):
    model_file_mask = f"{model_filename(cfg, run)}*"
    model_files = glob.glob(model_file_mask)
    models = {}
    for mf in model_files:
        key = int(mf.split('_')[-1].split('.')[0])
        models[key] = mf

    models = {k: models[k] for k in sorted(models)}
    wrost_models_files = list(models)[:-1]

    for wmf in wrost_models_files:
        os.system(f"rm ./{models[wmf]}")


def serialize_results(real, pred, cfg, coin_val):
    data = np.array([real, pred], dtype='float32').T
    df = pd.DataFrame(data=data, columns=['Real', 'Pred'])
    dump_file = preds_filename(cfg)

    if coin_val:
        dump_file = f"{dump_file}_coin_valset_{coin_val}"

    df.to_csv(dump_file, index=False)
    print(f"Result[{dump_file}] dumped!")


def serialize(hist, cfg, i):
    dump_file = hist_filename(cfg, i)
    pd.DataFrame.from_dict(hist.history).to_csv(dump_file, index=False)
    print(f"Hist[{dump_file}] dumped!")


def get_best_model(data):
    data = sorted(data, key=lambda k: k['mse'])
    m = data[0]
    print(f'Best Model of all runs is: {m}')

    return m['model']


def load_xgbr_model_data(cfg):
    model_file_mask = f"{model_filename(cfg, None)}*"
    model_files = glob.glob(model_file_mask)
    model_files.sort()
    last_model_file = model_files[-1]

    print(f">>>  {last_model_file} Loaded !")
    return load(last_model_file)


def load_models_data(cfg):
    models = []
    model_file_mask = f"{model_filename(cfg, None)}*"
    model_files = glob.glob(model_file_mask)
    model_files.sort()

    for model_file in model_files:
        with keras.utils.custom_object_scope(custom_layer_register()):
            model = tf.keras.models.load_model(model_file)
            print(f">>>  {model_file} Loaded !")
            models.append(model)

    return models


def load_xgbr_models_data(cfg):
    models = []
    model_file_mask = f"{model_filename(cfg, None)}*"
    model_files = glob.glob(model_file_mask)
    model_files.sort()

    for i in range(0, cfg.num_runs):
        model_file = f"{model_files[0].split('.')[0][:-1]}{i}.joblib"

        if os.path.isfile(model_file):
            model = load(model_file)
            print(f">>>  {model_file} Loaded !")
            models.append(model)

    return models


def do_scoring(d, cfg, model):
    print(f'Using device: {cfg.device_name}')
    with tf.device(cfg.device_name):
        outputs = model.predict(d.x_test)
        mse = mean_squared_error(d.y_test, outputs)
        mae = mean_absolute_error(d.y_test, outputs)
        rmse = sqrt(mse)
        r2 = r2_score(d.y_test, outputs)

        print('================ ARGS USED ===================')
        print(cfg.args)

        print(f"Result [lr: {cfg.learning_rate}]")
        print(f"MSE  {mse:.4f}")
        print(f"MAE  {mae:.4f}")
        print(f"RMSE {rmse:.4f}")
        print(f"R2   {r2:.4f}")

def do_scoring_over(d, cfg, models):
    print(f'Using device: {cfg.device_name}')
    with tf.device(cfg.device_name):
        all_scores = np.empty(shape=(0,3))
        model_data = np.array([])
        mses = np.array([])
        maes = np.array([])
        rmses = np.array([])
        r2s = np.array([])
        i = 0

        for model in models:
            scores = model.evaluate(d.x_test, d.y_test, verbose=0)
            print('Scores (loss, mse, mae) for run %d: %s' % (i, scores))
            all_scores = np.vstack((all_scores, scores))

            outputs = model.predict(d.x_test)
            mse = mean_squared_error(d.y_test, outputs)
            mae = mean_absolute_error(d.y_test, outputs)
            rmse = sqrt(mse)
            r2 = r2_score(d.y_test, outputs)

            mses = np.append(mses, mse)
            maes = np.append(maes, mae)
            rmses = np.append(rmses, rmse)
            r2s = np.append(r2s, r2)
            i = i + 1

            model_record = {
                'model': model,
                'mse': mse, 'r2': r2
            }

            model_data = np.append(model_data, model_record)

        print('================ ARGS USED ===================')
        print(cfg.args)
        print('================ RESULTS ===================')
        runs = len(models)
        print('Average over %d runs:' % runs)
        print(np.mean(all_scores, axis=0))
        print('Std deviation over %d runs:' % runs)
        print(np.std(all_scores, axis=0))

        print_scores(runs, cfg.learning_rate, mses, maes, rmses, r2s)

        return model_data


def do_xgbr_scoring_over(d, cfg, models):
    print(f'Using device: {cfg.device_name}')
    with tf.device(cfg.device_name):
        print(f'Using device: {cfg.device_name}')
        with tf.device(cfg.device_name):
            mses = np.array([])
            maes = np.array([])
            rmses = np.array([])
            r2s = np.array([])

            for model in models:
                outputs = model.predict(d.x_test)

                mse = mean_squared_error(d.y_test, outputs)
                mae = mean_absolute_error(d.y_test, outputs)
                rmse = sqrt(mse)
                r2 = r2_score(d.y_test, outputs)

                mses = np.append(mses, mse)
                maes = np.append(maes, mae)
                rmses = np.append(rmses, rmse)
                r2s = np.append(r2s, r2)

            print('================ ARGS USED ===================')
            print(cfg.args)
            print('================ RESULTS ===================')
            print_scores(cfg.num_runs, cfg.learning_rate, mses, maes, rmses, r2s)


def callbacks(cfg, run):
    model_dir = '.'
    best_model_filename = model_filename(cfg, run) + '_from_epoch_{epoch}.hdf5'
    patience = int(0.2 * cfg.epochs)
    best_weights_filepath = os.path.join(model_dir, best_model_filename)
    early_stopping = EarlyStopping(monitor='val_loss', mode='min', patience=patience)

    mcp_save = ModelCheckpoint(
        monitor='val_loss', mode='min', filepath=best_weights_filepath, save_best_only=True
    )

    if cfg.no_early_stopping:
        print("early_stopping is disabled")
        callbacks = [mcp_save]
    else:
        callbacks = [early_stopping, mcp_save]

    return callbacks


def do_training_runs(d, cfg, verbose, customized_dropout):
    print(f'Using device: {cfg.device_name}')
    with tf.device(cfg.device_name):
        times = np.array([])

        for i in range(cfg.num_runs):
            print('***Run #%d***' % i)
            start = time.perf_counter()
            model = neural_network(cfg, customized_dropout)
            hist = model.fit(d.x_train, d.y_train,
                            validation_data = (d.x_val, d.y_val),
                            epochs = cfg.epochs,
                            verbose = verbose,
                            callbacks = callbacks(cfg, i))

            elapsed = time.perf_counter() - start
            times = np.append(times, elapsed)

            serialize(hist, cfg, i)
            clean_dir(cfg, i)

        print_times(times)

        return hist


def neural_network(cfg, dropout=None):
    model = keras.Sequential()

    if dropout:
        model.add(dropout)

    model.add(layers.Dense(cfg.l1_units, input_dim=cfg.D, kernel_initializer='normal', activation='relu'))
    model.add(layers.Dense(cfg.l2_units, kernel_initializer='normal', activation='relu'))
    model.add(layers.Dense(1))

    adam = tf.keras.optimizers.Adam(lr=cfg.learning_rate)
    model.compile(loss='mse',
                  optimizer=adam,
                  metrics=['mse', 'mae']
                  )

    return model


def print_times(times):
    print('--------------- Timing ----------------')
    mt = datetime.timedelta(seconds=(times.mean()*1000))
    stdt = datetime.timedelta(seconds=(times.std()*1000))
    tm = f"{mt}±{stdt}"
    print(f"Done in {tm} min.")
    print(f"[CSV_t] {tm}")

    return tm


def print_scores(runs, lr, mses, maes, rmses, r2s):
    p = '2f'
    m = 100
    print(f"Results after {runs} [lr: {lr}] x10¯²")
    print(f"MSE  {mses.mean()*m:.{p}}±{mses.std()*m:.{p}}")
    print(f"MAE  {maes.mean()*m:.{p}}±{maes.std()*m:.{p}}")
    print(f"RMSE {rmses.mean()*m:.{p}}±{rmses.std()*m:.{p}}")
    print(f"R2   {r2s.mean():.4f}±{r2s.std():.4f}")
    print('--------------------------------------------------------')
    print(f"[CSV] {mses.mean() * m:.{p}}±{mses.std() * m:.{p}},{maes.mean() * m:.{p}}±{maes.std() * m:.{p}},{rmses.mean() * m:.{p}}±{rmses.std() * m:.{p}},{r2s.mean():.4f}±{r2s.std():.4f}")


def do_xgbr_training_runs(d, cfg, params):
    print(f'Using device: {cfg.device_name}')
    with tf.device(cfg.device_name):
        mses = np.array([])
        maes = np.array([])
        rmses = np.array([])
        r2s = np.array([])
        times = np.array([])

        for i in range(cfg.num_runs):
            print('***Run #%d***' % i)
            start = time.perf_counter()

            model = ensemble.GradientBoostingRegressor(**params)
            model.fit(d.x_train, d.y_train)

            trace_model_filename = f'{model_filename(cfg, i)}.joblib'
            dump(model, trace_model_filename)
            print(f"#### dump model [{trace_model_filename}]")

            outputs = model.predict(d.x_test)

            mse = mean_squared_error(d.y_test, outputs)
            mae = mean_absolute_error(d.y_test, outputs)
            rmse = sqrt(mse)
            r2 = r2_score(d.y_test, outputs)

            mses = np.append(mses, mse)
            maes = np.append(maes, mae)
            rmses = np.append(rmses, rmse)
            r2s = np.append(r2s, r2)

            elapsed = time.perf_counter() - start
            times = np.append(times, elapsed)

        print('================ ARGS USED ===================')
        print(cfg.args)
        print('================ RESULTS ===================')
        print_scores(cfg.num_runs, cfg.learning_rate, mses, maes, rmses, r2s)
        print_times(times)

        return model


def apply_isotonic_regression(df, dataset_name):
    print('# process_isotonic_regression in dataframe')
    if dataset_name == 'kaggle_bkp':
        df = _process_isotonic_regression(df, '', 'modelmagerr_')
    elif dataset_name == 'sdss':
        df = _process_isotonic_regression(df, '', 'err_')
    else:
        df = _process_isotonic_regression(df, 'Err', '')

    return df


def _process_isotonic_regression(df, e_sufix = '', e_prefix = ''):
    df_ir_err = df.copy(deep=True)
    idx = 10
    for b in 'ugriz':
        ir, _, _, _ = _apply_isotonic_regression(df.copy(), b, e_prefix + b + e_sufix)
        pred = ir.predict(df_ir_err[b])
        df_ir_err.insert(idx, f"{b}ErrExp", pred, allow_duplicates=True)
        idx = idx + 1

    return df_ir_err


def _apply_isotonic_regression(df, mag, magErr):
  df.sort_values(by=[mag], inplace=True)
  df = df.reset_index(drop=True)
  x = df[mag]
  y = df[magErr]
  ir = IsotonicRegression()
  y_expected = ir.fit_transform(x, y)

  return ir, x, y, y_expected


def apply_decision_tree_regression(df, dataset_name):
    print('# process_decision_tree_regression in dataframe')
    if dataset_name == 'kaggle_bkp':
        df = _process_decision_tree_regression(df, '', 'modelmagerr_')
    elif dataset_name == 'sdss':
        df = _process_decision_tree_regression(df, '', 'err_')
    else:
        df = _process_decision_tree_regression(df, 'Err', '')

    return df


def _process_decision_tree_regression(df, e_sufix = '', e_prefix = ''):
    df_dt_err = df.copy()
    idx = 10
    for b in 'ugriz':
        ir, _, _, y_ = _apply_decision_tree_regression(df_dt_err, b, e_prefix + b + e_sufix)
        df_dt_err.insert(idx, f"{b}ErrExp", y_, allow_duplicates=True)
        idx = idx + 1

    return df_dt_err


def _apply_decision_tree_regression(df, magCol, errCol, max_depth=5):
    X = df[[magCol]]
    y = df[[errCol]]
    regressor = DecisionTreeRegressor(random_state=0, max_depth = max_depth)
    regressor.fit(X, y)
    y_expected = regressor.predict(X)

    return regressor, X, y, y_expected
