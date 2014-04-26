'''
Created on Apr 14, 2014

@author: di
'''
import web
from web.contrib.template import render_jinja
import pymongo
import numpy as np
import json
from sklearn import linear_model
from sklearn import svm

from datetime import datetime

        
urls = (
    '/', 'Index',
    '/analyzer', 'StockAnalyzer',
    '/(script|css|images)/(.*)', 'static', 
)

app = web.application(urls, globals())

ratiodict = {'5':"50%",'6':'60%','7':"70%",'8':'80%','9':"90%"}
intervaldict = {'1':'Daily','2':'Weekly','3':'Monthly','4':'Quarterly',}

def Regression(data, ratio):
    ratio = ratio * 0.1
    data = np.asarray(data)
    input_data = data[:, :4]
    output_data = data[:, 4]
    input_data = input_data.tolist()
    output_data = output_data.tolist()
     
    pp1, pp2, pp3, pp4 = Poly_regression(input_data, 1) 
    input_data = np.asarray(input_data)
    n_total = np.shape(input_data)[0]
     
    t = range(n_total)
    #f = plt.figure()
    input_predict_1 = pp1(t)
    input_predict_2 = pp2(t)
    input_predict_3 = pp3(t)
    input_predict_4 = pp4(t)
    input_data_predict = np.asarray([input_predict_1, input_predict_2, input_predict_3, input_predict_4]).T
  
    output_total_linear = Linear_Regression(input_data_predict, output_data, ratio)
    output_total_kernel = Kernel_Regression(input_data_predict, output_data, ratio)
    return output_total_linear, output_total_kernel
  
def Linear_Regression(input_data, output_data, ratio):
    n_train = int(np.shape(input_data)[0]*ratio)
    clf = linear_model.LinearRegression()
    clf.fit(input_data[:][:n_train], output_data[:n_train])    
    output_predict = clf.predict(input_data[n_train:]).tolist()
    output_total = output_data[:n_train] + output_predict
    return output_total
  
def Kernel_Regression(input_data, output_data, ratio):
    n_train = int(np.shape(input_data)[0]*ratio)
    output_predict = []
    clf = svm.SVR(degree=100)
    for i in range(np.shape(input_data)[0] - n_train):
        clf.fit(input_data[:][:n_train + i], output_data[:n_train + i])    
        output_predict.append(clf.predict(input_data[n_train + i]).tolist()[0])
    output_total = output_data[:n_train] + output_predict
    return output_total
 
def Poly_regression(input_data, ratio):
    input_data = np.asarray(input_data)
    n_train = int(np.shape(input_data)[0]*ratio)
    t = range(n_train)
    pp1 = np.poly1d(np.polyfit(t, input_data[:n_train, 0], 10))
    pp2 = np.poly1d(np.polyfit(t, input_data[:n_train, 1], 10))
    pp3 = np.poly1d(np.polyfit(t, input_data[:n_train, 2], 10))
    pp4 = np.poly1d(np.polyfit(t, input_data[:n_train, 3], 10))
    return pp1, pp2, pp3, pp4

# def Regression(data, ratio):
#     ratio = ratio * 0.1
#     data = np.asarray(data)
#     input_data = data[:, :4]
#     output_data = data[:, 4]
#     input_data = input_data.tolist()
#     output_data = output_data.tolist()
#   
#     output_total_linear = Linear_Regression(input_data, output_data, ratio)
#     output_total_kernel = Kernel_Regression(input_data, output_data, ratio)
#     return output_total_linear, output_total_kernel
#   
# def Linear_Regression(input_data, output_data, ratio):
#     n_train = int(np.shape(input_data)[0]*ratio)
#     clf = linear_model.LinearRegression()
#     clf.fit(input_data[:][:n_train], output_data[:n_train])    
#     output_predict = clf.predict(input_data[n_train:]).tolist()
#     output_total = output_data[:n_train] + output_predict
#     return output_total
#   
# def Kernel_Regression(input_data, output_data, ratio):
#     n_train = int(np.shape(input_data)[0]*ratio)
#     output_predict = []
#     clf = svm.SVR()
#     for i in range(np.shape(input_data)[0] - n_train):
#         clf.fit(input_data[:][:n_train + i], output_data[:n_train + i])    
#         output_predict.append(clf.predict(input_data[n_train + i]).tolist()[0])
#     output_total = output_data[:n_train] + output_predict
#     return output_total

# ### Templates
render = render_jinja('./templates', encoding = 'utf-8')

class Stock:
    name = ""
    interval = ""
    ratio = ""
    start = ""
    end = ""
     
    def __init__(self, symbol):
        self.symbol = symbol
    def analyze(self, interval,ratio,start,end):
        self.interval = intervaldict[str(interval)]
        self.ratio = ratiodict[ratio]
        self.start = start
        self.end = end
        
        conn = pymongo.MongoClient()
        db = conn.stock
        start_dt = datetime(int(start[6:]),int(start[:2]),int(start[3:5]))
        end_dt = datetime(int(end[6:]),int(end[:2]),int(end[3:5]))
        cursor = db.DailyStockPrice.find({"TickerSymbol": self.symbol, 
                                          "$and": [ { "Date": {"$gte": start_dt} }, {"Date": {"$lte": end_dt}}]},
                                          {"Date":1, "High":1, "Low": 1, "Close": 1, "Open": 1, "Volume": 1, "_id": 0})
#        cursor = db.DailyStockPrice.find()
        priceList = list()
        priceList_for_cal = list()
        for data in cursor:
            priceList.append([data['Date'].strftime("%m/%d/%y")])
            priceList_for_cal.append([float(data['Volume']),float(data['High']),float(data['Low']),float(data['Open']),float(data['Close'])])
#             mid = data['_id']
#             m,d,y = data['Date'].split('/')
#             m_date = datetime(int(y),int(m),int(d))
#             db.DailyStockPrice.update({"_id": mid}, {"$set": {"Date": m_date}})
        print priceList_for_cal
        print priceList
        linear, kernel = Regression(priceList_for_cal, int(ratio))
        print linear
        print kernel
        dimension = len(priceList)
        if len(linear) == dimension and len(kernel) == dimension:
            for i in range(0,dimension):
                priceList[i].append(priceList_for_cal[i][4])
                priceList[i].append(linear[i])
                priceList[i].append(kernel[i])
        
        return priceList
        
    def retrieveInfo(self):
        conn = pymongo.MongoClient()
        db = conn.stock
        stock = db.CompanyProfile.find_one({'TickerSymbol':self.symbol})
        self.name = stock['Name']
        self.city = stock['City']
        self.sector = stock['Sector']
        self.industry = stock['Industry']
        self.currentPrice = stock['CurrentStockPrice']
        
        conn.close()

class Index:
    def GET(self):
        return render.index()
    
class StockAnalyzer:
    def POST(self):
        userdata = web.input()
        stocksymbol = userdata.stocksymbol
        interval = userdata.interval
        ratio = userdata.ratio
        start = userdata.start
        end = userdata.end
        
        stock = Stock(stocksymbol)
        
        if stocksymbol:
            stock.retrieveInfo()
        result = stock.analyze(interval, ratio, start, end)

        return render.analyzer(stock=stock,rawdata = json.dumps(result))
    
class static:
    def GET(self, media, file):
        try:
            f = open(media+'/'+file, 'r')
            return f.read()
        except:
            return '' # you can send an 404 error here if you want
if __name__ == "__main__":
    app.run()
