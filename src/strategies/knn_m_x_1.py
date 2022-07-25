import argparse
import pandas as pd

from sklearn.neighbors import KNeighborsRegressor

def parser():
    parse = argparse.ArgumentParser(description='ANN Experiments. Script to add expected errors computed by decision tree in the dataset.')
    parse.add_argument('-dataset', metavar='DS', help='Dataset file to use.')
    #parse.add_argument('-objective', metavar='WE', help='choose weight')

    return parse


def apply_knn_for_band(df, bands, err_col):
    X = df[bands]
    y = df[[err_col]]
    knn = KNeighborsRegressor(n_neighbors=10, weights='uniform')
    y_expected = knn.fit(X, y)

    return knn, X, y, y_expected


def apply_knn(df):
    print('# process_knn in dataframe')
    df_err = df.copy(deep=True)

    idx = df_err.columns.get_loc('err_z') + 1

    bands = [letter for letter in 'ugriz']

    for b in bands:
        eb = f"err_{b}"
        dt, _, _, _ = apply_knn_for_band(df.copy(), bands, eb)
        pred = dt.predict(df_err[bands])
        df_err.insert(idx, f"err_{b}_exp", pred, allow_duplicates=True)
        idx = idx + 1

    return df_err


def add_expected_errors_data(dataset_name):
    data = pd.read_csv(dataset_name, comment='#')
    name, ext = dataset_name.split('.')

    data = apply_knn(data)

    data.to_csv(f"{name}_knn_experrs.{ext}", index=False)


if __name__ == '__main__':
    parser = parser()
    args = parser.parse_args()

    add_expected_errors_data(args.dataset)