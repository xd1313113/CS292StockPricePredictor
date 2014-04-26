from __future__ import print_function
import numpy as np
import pymongo
from pymongo import MongoClient
import csv
from sklearn import linear_model
from sklearn import svm
from datetime import datetime,timedelta
import operator



def Read_csv(filename):
	data = []
	with open(filename, 'rb') as csvfile:
		content = csv.reader(csvfile)
		for row in content:
			data.append(row)
	return data


def JSON_converter():
	filename = 'DailyStockPrice.json'
	# folderpath = 'C:/R/CS292/Project/Data/'
	folderpath = 'C:/Users/zhangpn/Desktop/'
	f = open(folderpath + filename, 'r') # Open file
	data = []
	for line in f.readlines():
		y = [value for value in line.split()]
		data.append(y) # Get original data
	f.close()
	
	filename = 'DailyStockPrice_Converted.json'
	f = open(folderpath + filename, 'w')

	print(data.shape()[0])
	
	for i in range(np.shape(data)[0]):
		for j in range(np.shape(data[0])[0]):
			print(data[i][j], end = ' ', file = f)
		print(',', file = f)
	f.close()

def Regression():

	linear_coef, linear_inter = Linear_Regression()
	Kernel_Regression()
	print(linear_coef, linear_inter)

def Linear_Regression():
	clf = linear_model.LinearRegression()
	clf.fit ([[0, 0], [1, 1], [2, 2]], [1, 2, 4])	
	print(clf.predict([[0.2, 0.3], [0.4, 0.5]]))
	return clf.coef_, clf.intercept_

def Kernel_Regression():
	clf = svm.SVR()
	clf.fit ([[0, 0, 0], [1, 1, 0], [2, 2, 0]], [1, 2, 4])	
	print(clf.predict([[0.2, 0.3, 0], [0.4, 0.5, 0]]))	
