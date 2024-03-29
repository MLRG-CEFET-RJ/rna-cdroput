import argparse
import os
import gdown
import requests
import pandas as pd


def parser():
    parse = argparse.ArgumentParser(description='ANN Experiments. Script for dataset downloads. Formats all data to csv.')
    parse.add_argument('-dataset', metavar='DS', help='Dataset to download [teddy|happy|sdss|all].')

    return parse


def download_teddy():
    for data_chunk in 'ABCD':
        temp_file = f"teddyT_{data_chunk}.cat"
        url = f"https://raw.githubusercontent.com/COINtoolbox/photoz_catalogues/master/Teddy/forTemplateBased/{temp_file}"
        resp = requests.get(url)
        open(temp_file, "wb").write(resp.content)

        data = pd.read_csv(temp_file, comment='#',
                           delim_whitespace=True,
                           names=[
                               'objid', 'u', 'g', 'r', 'i', 'z',
                               'err_u', 'err_g', 'err_r', 'err_i', 'err_z',
                               'redshift', 'err_redshift'
                           ])

        if data_chunk == 'A':
            data.to_csv('teddy_data.csv', index=False)
        else:
            data.drop(columns=['err_redshift'], axis=1, inplace=True)
            data.to_csv(f"teddy_test_data_{data_chunk}.csv", index=False)

        os.remove(temp_file)


def download_happy():
    for data_chunk in 'ABCD':
        temp_file = f"happyT_{data_chunk}"
        url = f"https://raw.githubusercontent.com/COINtoolbox/photoz_catalogues/master/Happy/forTemplateBased/{temp_file}"
        resp = requests.get(url)
        open(temp_file, "wb").write(resp.content)

        data = pd.read_csv(temp_file, comment='#',
                           delim_whitespace=True,
                           names=[
                               'objid', 'u', 'g', 'r', 'i', 'z',
                               'err_u', 'err_g', 'err_r', 'err_i', 'err_z',
                               'redshift', 'err_redshift'
                           ])

        if data_chunk == 'A':
            data.to_csv('happy_data.csv', index=False)
        else:
            data.drop(columns=['err_redshift'], axis=1, inplace=True)
            data.to_csv(f"happy_test_data_{data_chunk}.csv", index=False)

        os.remove(temp_file)


def download_sdss():
    url = f"https://zenodo.org/record/4752020/files/sdss_train_data.csv?download=1"
    output = 'sdss_data.csv'
    gdown.download(url, output, quiet=False)


def download_data(dataset_name):
    if dataset_name == 'teddy':
        download_teddy()

    if dataset_name == 'happy':
        download_happy()

    if dataset_name == 'sdss':
        download_sdss()

    if dataset_name == 'all' or dataset_name is None:
        download_teddy()
        download_happy()
        download_sdss()


if __name__ == '__main__':
    parser = parser()
    args = parser.parse_args()

    dataset_name = args.dataset

    download_data(dataset_name)
