from __future__ import print_function
import numpy as np
import pymongo
from pymongo import MongoClient
import csv
from sklearn import linear_model
from sklearn import svm
from datetime import datetime,timedelta
import operator

# period: 'd', 'm', 'q'
# getting stock price data given a ticker symbol and date
def GetStockPrice(period, start_date, end_date, db, ticker):

	stockprice = [] # dictionary storing query result: given a ticker symbol of a stock and a date range, we output an nx5 array of stock data

	collection = db.DailyStockPrice

	result = collection.find({"TickerSymbol": "AAPL", "Date": {"$gt": start_date, "$lt": end_date}}, {"Date": 1, "High": 1, "Low": 1, "Close": 1, "Open": 1, "Volume": 1, "_id": 0})
	data = []
	for key in result: 
		data.append(key)

	# if we are getting stock prices on a daily base
	if period == 'd':
		for d in data:
			single_array = []
			for key in d:
				if (key == "Date"):
					single_array.append(d[key].strftime("%m/%d/%Y"))
					# single_array.append(d[key])
				else:
					single_array.append(str(d[key]))
			stockprice.append(single_array)

	# if we are getting stock prices on a weekly base
	elif period == 'm':

	# if period == 'd':
	# 	getDailyStockPrice(start_date, end_date, collection)


	# elif period == 'm':
	# 	print " "
	# print (stockprice)

	# stockprice array: Volume, High, Low, Date, Close, Open
	stockprice.sort(key=lambda x: datetime.strptime(x[3], "%m/%d/%Y"))

	return stockprice


# getting company information given a ticker symbol
def GetCompanyInfo (db, ticker):
	collection = db.CompanyProfile
	result = collection.find_one({"_id": ticker})

	stockdata = {} # dictionary where we are saving the company's information output to

	for key in result:
		str_key = str(key)
		stockdata[str_key] = str(result[key])

	print (stockdata)
	return stockdata


def getDailyStockPrice(start_date, end_date, collection):
	indexDay = start_date
	print ("1")
	for result in collection.find({"Ticker": "AAPL", "$and": [ { "Date": {"$gt": start_date} }, {"Date": {"$lt": end_date}}]}, {"High":1 }):#, "Low": 1, "Close": 1, "Open": 1, "Volume": 1, "_id": 0}):
		data = []
		for key in result: 
			print (key)
	# 		data.append(str(result[key]))
	# 	stockprice[indexDay] = data
	# 	indexDay = addOneDay(indexDay)
	# return stockprice

def formatDate(date):
	date = date.split("/")
	date_pair = (date[2], date[1], date[0])
	return date_pair

def addOneDay(date):
	mytime = datetime.strptime(date,"%m/%d/%Y")
	dt = timedelta(days=1)  # 1 day
	mytime+=dt
	time = mytime.strftime("%m/%d/%Y")
	return time

def Stock():
	## Import data
	CompanyProfile, DailyStockPrice = Read_Stock()
	## Connect to database
	client = MongoClient()

	if ('stock' in client.database_names()):
		return client, client.stock

	## Drop database if existing
	client.drop_database('stock')
	
	## Create database
	db = client.stock
	
	## Manipulate data

	 # Collection_1
	collectionname = CompanyProfile
	collection = db.CompanyProfile
	
	doc = []
	for i in range(0, np.shape(collectionname)[0]):
		idstring = '{0:02d}'.format(i)
		string = {"_id" : collectionname[i][0],
				  "Address": collectionname[i][1],
				  "Name": collectionname[i][2],
				  "City": collectionname[i][3],
				  "State": collectionname[i][4],
				  "Country": collectionname[i][5],
				  "Zip": collectionname[i][6],
				  "Phone": collectionname[i][7],
				  "Fax": collectionname[i][8],
				  "Website": collectionname[i][9],
				  "Sector": collectionname[i][10],
				  "Industry": collectionname[i][11],
				  "FullTimeEmployeesNumber": collectionname[i][12],
				  "EPS": collectionname[i][13],
				  "MarketCap": collectionname[i][14],
				  "CurrentStockPrice": collectionname[i][15],
				  }
		doc.append(string)
	collection.insert(doc)


	 # Collection_2
	collectionname = DailyStockPrice
	collection = db.DailyStockPrice

	doc = []
	for i in range(0, np.shape(collectionname)[0]):
		date_fields = collectionname[i][1].split('/')
		month = int(date_fields[0])
		day = int(date_fields[1])
		year = int(date_fields[2])
		idstring = '{0:04d}'.format(i)
		string = { "_id": idstring,
				"TickerSymbol": collectionname[i][0],
				"Date": datetime(year, month, day),
				"Open" : collectionname[i][2],
				"High" : collectionname[i][3],
				"Low" : collectionname[i][4],
				"Close" : collectionname[i][5],
				"Volume" : collectionname[i][6],
				}
		doc.append(string)

	collection.insert(doc)
	# print(collection.find_one({'TickerSymbol':'FB'}))

	period = 'd'
	start_date = 1
	end_date = 2
	# ReadFromDatabase(period, start_date, end_date, db.DailyStockPrice)
	print ("Done loading database")
	return client, db

def Read_Stock():
	# folderpath = 'C:/R/CS292/Data/'
	folderpath = 'C:/Users/zhangpn/Desktop/'
	# Read company profile
	filename = 'CompanyProfile.csv'
	CompanyProfile = Read_csv(folderpath + filename)
	
	# # Read stock profile
	# filename = 'StockProfile.csv'
	# StockProfile = Read_csv(folderpath + filename)
	
	# Read stock profile
	filename = 'dailystockprice.csv'
	Dailystockprice = Read_csv(folderpath + filename)

	return CompanyProfile, Dailystockprice

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

client, db = Stock()


start_date = datetime(2010, 2, 1)
end_date = datetime(2010, 2, 20)
ticker = "AAPL"
period = 'd'
# GetCompanyInfo(db, ticker)
GetStockPrice(period, start_date, end_date, db, ticker)