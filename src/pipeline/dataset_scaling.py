import argparse
import pandas as pd

from src.modules import utils

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler

def parser():
    parse = argparse.ArgumentParser(description='ANN Experiments. Script for dataset scaling.')
    parse.add_argument('-scaler', metavar='SCALER', help='Scaler classname to use.')
    parse.add_argument('-datafiles', nargs='+', metavar='DATAFILES', help='Train dataset file must be the first. Fit and transform the first, and only transform the others.')

    return parse


def scale_data(datafile_names, scaler_opt):
    train_data = pd.read_csv(f"./src/data/{datafile_names[0]}", comment='#')

    scaler = scaler_of(scaler_opt)
    ugriz = ['u','g','r','i','z']

    train_data[ugriz] = scaler.fit_transform(train_data[ugriz])

    name, ext = datafile_names[0].split('.')
    train_data.to_csv(f"./src/data/{name}_scaled.{ext}", index=False)

    if len(datafile_names) > 1:
        for df_name in datafile_names[1:]:
            test_data = pd.read_csv(f"./src/data/{df_name}", comment='#')
            test_data[ugriz] = scaler.transform(test_data[ugriz])

            name, ext = df_name.split('.')
            test_data.to_csv(f"./src/data/{name}_scaled.{ext}", index=False)


def scaler_of(scaler_opt):
    if scaler_opt == 'StandardScaler':
        return StandardScaler()
    if scaler_opt == 'MinMaxScaler':
        return MinMaxScaler()

    return None


if __name__ == '__main__':
    parser = parser()
    args = parser.parse_args()

    utils.rna_cdrpout_print(f"Stage 04: Scaling {len(args.datafiles)} datafiles")
    scale_data(args.datafiles, args.scaler)
