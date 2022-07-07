python ./dataset_download.py -dataset teddy
python ./dataset_download.py -dataset happy

python ./random_forest_one_to_one.py -dataset teddy_data.csv
python ./random_forest_one_to_one.py -dataset happy_data.csv

python ./dataset_split.py -dataset teddy_data_rf_experrs.csv -p 60:20:20
python ./dataset_split.py -dataset happy_data_rf_experrs.csv -p 60:20:20

python ./dataset_scaling.py -datafiles teddy_data_rf_experrs_train.csv teddy_data_rf_experrs_val.csv teddy_data_rf_experrs_test.csv -scaler StandardScaler
python ./dataset_scaling.py -datafiles happy_data_rf_experrs_train.csv happy_data_rf_experrs_val.csv happy_data_rf_experrs_test.csv -scaler StandardScaler

python ./training.py -n teddy_experimento_one_to_one -e 10 -dp ErrorBasedInvertedRandomDropout -runs 1 -trainset teddy_data_rf_experrs_train_scaled.csv -valset teddy_data_rf_experrs_val_scaled.csv
python ./training.py -n happy_experimento_one_to_one -e 10 -dp ErrorBasedInvertedRandomDropout -runs 1 -trainset happy_data_rf_experrs_train_scaled.csv -valset happy_data_rf_experrs_val_scaled.csv
