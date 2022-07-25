python ./dataset_download.py -dataset teddy
python ./dataset_download.py -dataset happy

python ./isotonic_regression_many_to_many.py -dataset teddy_data.csv
python ./isotonic_regression_many_to_many.py -dataset happy_data.csv

python ./dataset_split.py -dataset teddy_data_ir_experrs.csv -p 60:20:20
python ./dataset_split.py -dataset happy_data_ir_experrs.csv -p 60:20:20

python ./dataset_scaling.py -datafiles teddy_data_ir_experrs_train.csv teddy_data_ir_experrs_val.csv teddy_data_ir_experrs_test.csv -scaler StandardScaler
python ./dataset_scaling.py -datafiles happy_data_ir_experrs_train.csv happy_data_ir_experrs_val.csv happy_data_ir_experrs_test.csv -scaler StandardScaler

python ./training.py -n teddy_experimento_many_to_many -e 10 -dp ErrorBasedInvertedRandomDropout -runs 1 -trainset teddy_data_ir_experrs_train_scaled.csv -valset teddy_data_ir_experrs_val_scaled.csv
python ./training.py -n happy_experimento_many_to_many -e 10 -dp ErrorBasedInvertedRandomDropout -runs 1 -trainset happy_data_ir_experrs_train_scaled.csv -valset happy_data_ir_experrs_val_scaled.csv

python ./dataset_download.py -dataset sdss
python ./dataset_clean.py -dataset sdss_data.csv
python ./isotonic_regression_many_to_many.py -dataset sdss_data_clean.csv
python ./dataset_split.py -dataset sdss_data_clean_mlp_experrs.csv -p 60:20:20
python ./dataset_scaling.py -datafiles sdss_data_clean_mlp_experrs_train.csv sdss_data_clean_mlp_experrs_val.csv sdss_data_clean_mlp_experrs_test.csv -scaler StandardScaler
python ./training.py -n sdss_experimento_many_to_many -e 10 -dp ErrorBasedInvertedRandomDropout -runs 1 -trainset sdss_data_clean_mlp_experrs_train_scaled.csv -valset sdss_data_clean_mlp_experrs_val_scaled.csv