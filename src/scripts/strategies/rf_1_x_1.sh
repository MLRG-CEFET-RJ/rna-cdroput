# TEDDY
python -m src.strategies.rf_1_x_1 -dataset teddy_data.csv

python -m src.pipeline.dataset_split -dataset teddy_data_rf_1_x_1_experrs.csv -p 60:20:20

python -m src.pipeline.dataset_scaling -datafiles teddy_data_rf_1_x_1_experrs_train.csv teddy_data_rf_1_x_1_experrs_val.csv teddy_data_rf_1_x_1_experrs_test.csv -scaler StandardScaler

python -m src.training -n teddy_training_rf_1_x_1 -e 10 -dp ErrorBasedInvertedRandomDropout -runs 1 -trainset teddy_data_rf_1_x_1_experrs_train_scaled.csv -valset teddy_data_dt_1_x_1_experrs_val_scaled.csv

# HAPPY
python -m src.strategies.rf_1_x_1 -dataset happy_data.csv

python -m src.pipeline.dataset_split -dataset happy_data_rf_1_x_1_experrs.csv -p 60:20:20

python -m src.pipeline.dataset_scaling -datafiles happy_data_rf_1_x_1_experrs_train.csv happy_data_rf_1_x_1_experrs_val.csv happy_data_rf_1_x_1_experrs_test.csv -scaler StandardScaler

python -m src.training -n happy_training_rf_1_x_1 -e 10 -dp ErrorBasedInvertedRandomDropout -runs 1 -trainset happy_data_rf_1_x_1_experrs_train_scaled.csv -valset happy_data_dt_1_x_1_experrs_val_scaled.csv

# SDSS 
python -m src.strategies.rf_1_x_1 -dataset sdss_data_clean.csv

python -m src.pipeline.dataset_split -dataset sdss_data_clean_rf_1_x_1_experrs.csv -p 60:20:20

python -m src.pipeline.dataset_scaling -datafiles sdss_data_clean_rf_1_x_1_experrs_train.csv sdss_data_clean_rf_1_x_1_experrs_val.csv sdss_data_clean_rf_1_x_1_experrs_test.csv -scaler StandardScaler

python -m src.training -n sdss_training_rf_1_x_1 -e 10 -dp ErrorBasedInvertedRandomDropout -runs 1 -trainset sdss_data_clean_rf_1_x_1_experrs_train_scaled.csv -valset sdss_data_clean_dt_1_x_1_experrs_val_scaled.csv