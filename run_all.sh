#!/bin/bash

nohup python main.py -e 500 -dp none -sc StandardScaler -runs 10 -lr 0.001 -f 10 -dataset teddy > out_test_ss_teddy.txt ;
nohup python main.py -e 500 -dp none -sc StandardScaler -runs 10 -lr 0.001 -f 10 -dataset happy > out_test_ss_happy.txt ;
nohup python main.py -e 500 -dp none -sc StandardScaler -runs 10 -lr 0.001 -f 10 -dataset kaggle_bkp > out_test_ss_kaggle_bkp.txt;

nohup python main.py -e 500 -dp none -sc StandardScaler -runs 10 -lr 0.001 -f 10 -dataset teddy > out_test_ss_cdp_teddy.txt ;
nohup python main.py -e 500 -dp none -sc StandardScaler -runs 10 -lr 0.001 -f 10 -dataset happy > out_test_ss_cpd_happy.txt ;
nohup python main.py -e 500 -dp none -sc StandardScaler -runs 10 -lr 0.001 -f 10 -dataset kaggle_bkp > out_test_ss_cdp_kaggle_bkp.txt;

nohup python main.py -xgbr -e 500 -sc StandardScaler -lr 0.001 -f 10 -dataset teddy > out_test_ss_xgbr_teddy.txt;
nohup python main.py -xgbr -e 500 -sc StandardScaler -lr 0.001 -f 10 -dataset happy > out_test_ss_xgbr_happy.txt;
nohup python main.py -xgbr -e 500 -sc StandardScaler -lr 0.001 -f 10 -dataset kaggle_bkp  > out_test_ss_xgbr_kaggle.txt;
