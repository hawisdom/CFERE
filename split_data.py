import csv
import ast
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

def read_data(data_file):
    with open(data_file,'r',encoding='utf-8-sig') as file_open:
        csv_reader = csv.reader(file_open)
        X_list = []
        Y_list = []
        for line in csv_reader:
            X_list.append(line[0])
            Y_list.append(line[1])

    print(len(X_list))
    print(len(Y_list))
    return X_list,Y_list

def get_split_data(X_list,Y_list):

    X_train, X_test, Y_train, Y_test = train_test_split(X_list, Y_list,test_size=0.30,stratify=Y_list)
    print(len(X_train))
    print(len(X_test))

    train_file = './data/trainData.csv'
    test_file = './data/devData.csv'
    #生成训练文件
    with open(train_file,'w',encoding='utf-8-sig',newline='') as file_open:
        csv_writer = csv.writer(file_open)
        line = []
        for i in range(len(X_train)):
            line.append(X_train[i])
            line.append(Y_train[i])
            csv_writer.writerow(line)
            line.clear()

    # 生成测试文件
    with open(test_file,'w',encoding='utf-8-sig',newline='') as file_open:
        csv_writer = csv.writer(file_open)
        line = []
        for i in range(len(X_test)):
            line.append(X_test[i])
            line.append(Y_test[i])
            csv_writer.writerow(line)
            line.clear()


def main_data():
    data_file = './data/experimental_data.csv'
    X_list, Y_list = read_data(data_file)
    get_split_data(X_list, Y_list)

