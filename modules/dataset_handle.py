import os
import pandas as pd
import numpy as np
import requests
import gdown

from sklearn.model_selection import train_test_split

from sklearn_pandas import DataFrameMapper

_val_idx = {"B": 1, "C": 2, "D": 3}


def cut_val_band(df, band, val):
  return df[df[band] <= val]

def cut_flag(df, attr, value):
  chunk_size = df[df[attr] == value].shape[0]
  print(f"{chunk_size} values cut off.")

  return df[df[attr] != value]

def cut_all_val_errs(df, dataset_name, val):
  if dataset_name == 'sdss':
    return  _cut_all_val_errs(df, val, s='err_')
  else:
    return _cut_all_val_errs(df, val, p='Err')


def _cut_all_val_errs(df, val, s='', p=''):
  df = df[df[f"{s}u{p}"] <= val]
  df = df[df[f"{s}g{p}"] <= val]
  df = df[df[f"{s}r{p}"] <= val]
  df = df[df[f"{s}i{p}"] <= val]
  df = df[df[f"{s}z{p}"] <= val]

  return df


def remove_col_df(dataframe, col_to_remove):
  for c in col_to_remove:
    if c in dataframe.columns:
      dataframe.drop(columns=[c], axis=1,inplace=True)


def ugriz_errs_split(x, chunks=2):
  dim = x.shape[1]
  pad = int(dim / chunks)
  if chunks == 2:
    return x.iloc[:, :pad], x.iloc[:, pad:pad*2], [[]], [[]]
  elif chunks == 3:
    return x.iloc[:, :pad], x.iloc[:, pad:pad*2], x.iloc[:, pad*2:pad*3], [[]]
  else:
    return x.iloc[:, :pad], x.iloc[:, pad:pad*2], x.iloc[:, pad*2:pad*3], x.iloc[:, pad*3:pad*4]


def filter_col(dataframe):
  #remove_col_df(dataframe, ('ID', '#ID', 'redshiftErr','objid', 'specobjid', 'class'))
  remove_col_df(dataframe, ('ID', '#ID', 'redshiftErr', 'specobjid', 'class', 'clean'))

  if 'objid' in dataframe.columns:
    objid = dataframe.pop('objid')
    size = len(dataframe.columns)
    dataframe.insert(size-1, 'objid', objid)

  return dataframe


def filter_negative_data(dataframe, dataset):
  if dataset == 'sdss':
    return _filter_negative_data(dataframe, s='err_')
  else:
    return _filter_negative_data(dataframe, p='Err')


def _filter_negative_data(dataframe, s='', p=''):
  orig = dataframe.shape[0]
  dataframe = dataframe[dataframe.u > 0]
  dataframe = dataframe[dataframe.g > 0]
  dataframe = dataframe[dataframe.r > 0]
  dataframe = dataframe[dataframe.i > 0]
  dataframe = dataframe[dataframe.z > 0]

  dataframe = dataframe[dataframe[f"{s}u{p}"] > 0]
  dataframe = dataframe[dataframe[f"{s}g{p}"] > 0]
  dataframe = dataframe[dataframe[f"{s}r{p}"] > 0]
  dataframe = dataframe[dataframe[f"{s}i{p}"] > 0]
  dataframe = dataframe[dataframe[f"{s}z{p}"] > 0]

  clean = dataframe.shape[0]
  print(f"Negative data removed: {orig-clean}.")

  return dataframe


def build_dataset(dataframe, num_features, scaler, include_id=False):
  x = dataframe.iloc[:, :-1]
  y = dataframe[['redshift']]

  x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
  x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.2, random_state=42)

  if include_id:
    x_train = x_train.iloc[:, :-1]
    x_val = x_val.iloc[:, :-1]
    x_test_ids = x_test.iloc[:, -1]

  chunks = 2
  if num_features > 10:
    chunks = num_features / 5

  if 5 < num_features < 16:
    x_train_ugriz, x_train_errs, x_train_experrs, _ = ugriz_errs_split(x_train, chunks)
    x_val_ugriz, x_val_errs, x_val_experrs, _ = ugriz_errs_split(x_val, chunks)
    x_test_ugriz, x_test_errs, x_test_experrs, _ = ugriz_errs_split(x_test, chunks)

    if scaler != None:
      mapper = DataFrameMapper([(x_train_ugriz.columns, scaler)])
      x_train_ugriz_s = mapper.fit_transform(x_train_ugriz)
      x_train_ugriz = pd.DataFrame(x_train_ugriz_s, index=x_train_ugriz.index, columns=x_train_ugriz.columns)

      x_val_ugriz_s = mapper.transform(x_val_ugriz)
      x_val_ugriz = pd.DataFrame(x_val_ugriz_s, index=x_val_ugriz.index, columns=x_val_ugriz.columns)

      x_test_ugriz_s = mapper.transform(x_test_ugriz)
      x_test_ugriz = pd.DataFrame(x_test_ugriz_s, index=x_test_ugriz.index, columns=x_test_ugriz.columns)


      if chunks == 2:
        x_train = pd.concat([x_train_ugriz, x_train_errs], axis=1)
        x_val = pd.concat([x_val_ugriz, x_val_errs], axis=1)
        x_test = pd.concat([x_test_ugriz, x_test_errs], axis=1)
      else:
        x_train = pd.concat([x_train_ugriz, x_train_errs, x_train_experrs], axis=1)
        x_val = pd.concat([x_val_ugriz, x_val_errs, x_val_experrs], axis=1)
        x_test = pd.concat([x_test_ugriz, x_test_errs, x_test_experrs], axis=1)

  elif num_features > 15:
    x_train_ugriz, x_train_errs, x_train_experrs, x_train_expmags = ugriz_errs_split(x_train, chunks)
    x_val_ugriz, x_val_errs, x_val_experrs, x_val_expmags = ugriz_errs_split(x_val, chunks)
    x_test_ugriz, x_test_errs, x_test_experrs, x_test_expmags = ugriz_errs_split(x_test, chunks)

    if scaler != None:
      mapper = DataFrameMapper([(x_train_ugriz.columns, scaler)])
      x_train_ugriz_s = mapper.fit_transform(x_train_ugriz)
      x_train_ugriz = pd.DataFrame(x_train_ugriz_s, index=x_train_ugriz.index, columns=x_train_ugriz.columns)

      x_val_ugriz_s = mapper.transform(x_val_ugriz)
      x_val_ugriz = pd.DataFrame(x_val_ugriz_s, index=x_val_ugriz.index, columns=x_val_ugriz.columns)

      x_test_ugriz_s = mapper.transform(x_test_ugriz)
      x_test_ugriz = pd.DataFrame(x_test_ugriz_s, index=x_test_ugriz.index, columns=x_test_ugriz.columns)

      x_train = pd.concat([x_train_ugriz, x_train_errs, x_train_experrs, x_train_expmags], axis=1)
      x_val = pd.concat([x_val_ugriz, x_val_errs, x_val_experrs, x_val_expmags], axis=1)
      x_test = pd.concat([x_test_ugriz, x_test_errs, x_test_experrs, x_test_expmags], axis=1)

  else:
    if scaler != None:
      mapper = DataFrameMapper([(x_train.columns, scaler)])
      x_train_s = mapper.fit_transform(x_train)
      x_train = pd.DataFrame(x_train_s, index=x_train.index, columns=x_train.columns)

      x_val_s = mapper.transform(x_val)
      x_val = pd.DataFrame(x_val_s, index=x_val.index, columns=x_val.columns)

      x_test_s = mapper.transform(x_test)
      x_test = pd.DataFrame(x_test_s, index=x_test.index, columns=x_test.columns)

  if include_id:
    x_test = pd.concat([x_test, x_test_ids], axis=1)

  return x_train, y_train, x_test, y_test, x_val, y_val, scaler


def build_dataset_coin_data(df_train, df_val, num_features, scaler, transform_test):
  all_train_data = df_train.to_numpy()
  x = all_train_data[:,0:(num_features)]
  y = all_train_data[:,-1]

  all_val_data = df_val.to_numpy()

  x_test = all_val_data[:, :-1]
  y_test = all_val_data[:, -1]

  x_train, x_val, y_train, y_val = train_test_split(x, y, test_size=0.2, random_state=42)
  x_test_experrs = None

  chunks = 2
  if num_features > 10:
    chunks = num_features / 5

  if 5 < num_features < 16:
    x_train_ugriz, x_train_errs, x_train_experrs, _ = ugriz_errs_split(x_train, chunks)
    x_val_ugriz, x_val_errs, x_val_experrs, _ = ugriz_errs_split(x_val, chunks)
    if transform_test:
      x_test_ugriz, x_test_errs, x_test_experrs, _ = ugriz_errs_split(x_test, chunks)
    else:
      x_test_ugriz, x_test_errs, _, _ = ugriz_errs_split(x_test, 2)

    if scaler != None:
      x_train_ugriz = scaler.fit_transform(x_train_ugriz)
      x_val_ugriz = scaler.transform(x_val_ugriz)
      x_test_ugriz = scaler.transform(x_test_ugriz)

      if chunks == 2:
        x_train = np.hstack((x_train_ugriz, x_train_errs))
        x_val = np.hstack((x_val_ugriz, x_val_errs))
        x_test = np.hstack((x_test_ugriz, x_test_errs))
      else:
        x_train = np.hstack((x_train_ugriz, x_train_errs, x_train_experrs))
        x_val = np.hstack((x_val_ugriz, x_val_errs, x_val_experrs))
        if transform_test:
          x_test = np.hstack((x_test_ugriz, x_test_errs, x_test_experrs))
        else:
          x_test = np.hstack((x_test_ugriz, x_test_errs))

  elif num_features > 15:
    x_train_ugriz, x_train_errs, x_train_experrs, x_train_expmags = ugriz_errs_split(x_train, chunks)
    x_val_ugriz, x_val_errs, x_val_experrs, x_val_expmags = ugriz_errs_split(x_val, chunks)
    x_test_ugriz, x_test_errs, _, _ = ugriz_errs_split(x_test, 2)

    if scaler != None:
      x_train_ugriz = scaler.fit_transform(x_train_ugriz)
      x_val_ugriz = scaler.transform(x_val_ugriz)
      x_test_ugriz = scaler.transform(x_test_ugriz)

      x_train = np.hstack((x_train_ugriz, x_train_errs, x_train_experrs, x_train_expmags))
      x_val = np.hstack((x_val_ugriz, x_val_errs, x_val_experrs, x_val_expmags))
      x_test = np.hstack((x_test_ugriz, x_test_errs))

  else:
    if scaler != None:
      x_train = scaler.fit_transform(x_train)
      x_val = scaler.transform(x_val)
      x_test = scaler.transform(x_test)

  return x_train, y_train, x_test, y_test, x_val, y_val, scaler


def load_dataframe(dataset_name, coin_val):
  pd.set_option("max_columns", None)
  if dataset_name == 'teddy' or dataset_name == 'happy':
    if coin_val:
      train = pd.read_csv(f"{dataset_name}_train_data", comment='#', delim_whitespace=True, names=['ID', 'u', 'g', 'r', 'i', 'z', 'uErr', 'gErr', 'rErr', 'iErr', 'zErr', 'redshift', 'redshiftErr'])
      test  = pd.read_csv(f"{dataset_name}_val_data_{_val_idx[coin_val]}", comment='#', delim_whitespace=True, names=['ID', 'u', 'g', 'r', 'i', 'z', 'uErr', 'gErr', 'rErr', 'iErr', 'zErr', 'redshift', 'redshiftErr'])
      return train, test
    else:
      data = pd.read_csv(f"{dataset_name}_train_data", comment='#', delim_whitespace=True, names=['ID','u','g','r','i','z','uErr','gErr','rErr','iErr','zErr','redshift','redshiftErr'])
      return data, None

  if dataset_name == 'kaggle' or dataset_name == 'kaggle_bkp':
    return pd.read_csv('kaggle_train_data.csv'), None

  if dataset_name == 'sdss':
    return pd.read_csv('sdss_train_data.csv', comment="#"), None

  return None, None


def download_data(dataset_name, coin_val):
  if dataset_name == 'teddy':
    if coin_val:
      download_teddy(data_chunk=coin_val)
    else:
      download_teddy()

  if dataset_name == 'happy':
    if coin_val:
      download_happy(data_chunk=coin_val)
    else:
      download_happy()

  if dataset_name == 'kaggle':
    if os.path.isfile('kaggle_train_data.csv'):
      print("Dataset Found!")
    else:
      download_kaggle()

  if dataset_name == 'kaggle_bkp':
    if os.path.isfile('kaggle_train_data.csv'):
      print("Dataset Found!")
    else:
      download_kaggle_alternative()

  if dataset_name == 'sdss':
    if os.path.isfile('sdss_train_data.csv'):
      print("Dataset Found!")
    else:
      download_sdss()


def download_teddy(data_chunk='A'):
  data_file = 'teddy_train_data'
  if data_chunk != 'A':
    data_file = f"teddy_val_data_{_val_idx[data_chunk]}"

  if os.path.isfile(data_file):
    print("Dataset Found!")
  else:
    os.system(f"wget https://raw.githubusercontent.com/COINtoolbox/photoz_catalogues/master/Teddy/forTemplateBased/teddyT_{data_chunk}.cat")
    if data_chunk == 'A':
      os.system(f"mv teddyT_{data_chunk}.cat teddy_train_data")
    else:
      os.system(f"mv teddyT_{data_chunk}.cat teddy_val_data_{_val_idx[data_chunk]}")


def download_happy(data_chunk='A'):
  data_file = 'happy_train_data'
  if data_chunk != 'A':
    data_file = f"happy_val_data_{_val_idx[data_chunk]}"

  if os.path.isfile(data_file):
    print("Dataset Found!")
  else:
    os.system(f"wget https://raw.githubusercontent.com/COINtoolbox/photoz_catalogues/master/Happy/forTemplateBased/happyT_{data_chunk}")
    if data_chunk == 'A':
      os.system(f"mv happyT_{data_chunk} happy_train_data")
    else:
      os.system(f"mv happyT_{data_chunk} happy_val_data_{_val_idx[data_chunk]}")


def download_kaggle():
  os.system('wget -O archieve.zip "https://storage.googleapis.com/kaggle-competitions-data/kaggle-v2/3617/105309/bundle/archive.zip?GoogleAccessId=web-data@kaggle-161607.iam.gserviceaccount.com&Expires=1589667788&Signature=PqUjFhjNMhS9DEBnk3Yxzo%2BXnKS9c3v1XbmW%2F2dVcromNwDnELmnVSAtGD%2BFi%2FiNay801TWg84P0N6qCq8D5P%2BcOj92zcBB0%2BjPX8yIKvvwud3mA%2FCW%2FLAXTCbgGHrNKUUSIAMhkwro41Nzi%2F4lP0pIpCugQr44bWnCmh57zmt5CNJDb63ZS7CiZyZGsNg6YebXTAzR3yuNbdtMd3pvmQJwv%2FPedtyoR4PhloelwqE3fxVx2pt9AdZzE%2FU%2BRVyoFCnj1EiQBq8oDES2TEoJde9rTCIMWM6OtFPa%2Bq3e%2BqDC9lzgkywTPJ4hjmRA4VmFgPWb57uOX7T2QZuHnnIG87g%3D%3D&response-content-disposition=attachment%3B+filename%3Dphotometric-redshift-estimation-2013.zip"')
  os.system('unzip -u archieve.zip')
  os.system('unzip -u train.zip')
  os.system('mv train.csv kaggle_train_data.csv')


def download_sdss_alternative():
  id = '1i5fFrVlVkfRvFMBYzYbE_whLfSTz5fYe'
  url = f"https://drive.google.com/uc?id={id}"
  output = 'sdss_train_data.csv'
  gdown.download(url, output, quiet=False)

def download_sdss():
  url = f"https://zenodo.org/record/4752020/files/sdss_train_data.csv?download=1"
  output = 'sdss_train_data.csv'
  gdown.download(url, output, quiet=False)

def download_kaggle_alternative():
  def download_file_from_google_drive(id):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params={'id': id}, stream=True)
    token = get_confirm_token(response)

    if token:
      params = {'id': id, 'confirm': token}
      response = session.get(URL, params=params, stream=True)

    save_response_content(response)


  def get_confirm_token(response):
    for key, value in response.cookies.items():
      if key.startswith('download_warning'):
        return value

    return None


  def save_response_content(response):
    CHUNK_SIZE = 32768

    with open("kaggle_train_data.csv", "wb") as f:
      for chunk in response.iter_content(CHUNK_SIZE):
        if chunk:  # filter out keep-alive new chunks
          f.write(chunk)


  download_file_from_google_drive('1xCQzmusNSt65zQnjsrnddLhuCB5WdYcl')


def dump_test_set(x_test, y_test):
  df_test = pd.concat([x_test, y_test], axis=1).reindex(x_test.index)
  df_test.to_csv('test_dataset.csv')


def load_test_dataframe(dataset):
  return pd.read_csv(dataset)


def empty():
  return pd.DataFrame()