import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

class Model:
    def __init__(self):
        self.ctr_predict_para = None
        self.impression_predict_para = None
        self.bid_price_para = None
        self.cls_impression_para = None

    def remove_isolation(self, arr):
        Percentile = np.percentile(arr,[0,25,50,75,100])
        IQR = Percentile[3] - Percentile[1]
        UpLimit = Percentile[3]+IQR*1.5
        DownLimit = Percentile[1]-IQR*1.5
        res = arr[np.logical_and(arr <= UpLimit, arr >= DownLimit)]
        return res, res.sum(), res.shape[0], res.mean()

    def ctr_predict_model(self, x):
    # using sigmoid d + (a-d) / (1+(x/c)**b)**m
        a, b, c, d, m = self.ctr_predict_para
        return d + (a-d) / (1+(x/c)**b)**m

    def impression_predict_model(self, x):
    # using sigmoid d + (a-d) / (1+(x/c)**b)
        a, b, c, d = self.impression_predict_para
        return d + (a-d) / (1+(x/c)**b)

    def bid_price_model(self, x):
    # using sigmoid d + (a-d) / (1+(x/c)**b)**m
        a, b, c, d, m = self.bid_price_para
        return d + (a-d) / (1+(x/c)**b)**m

    def cls_impression_co_model(self, x):
    # using sigmoid d + (a-d) / (1+(x/c)**b)
        a, b, c, d = self.cls_impression_para
        return d + (a-d) / (1+(x/c)**b)

    def ctr_co_curvefit(self):
        x = [0.001, 0.003, 0.008, 0.010, 0.05, 0.08, 0.11, 0.13, 0.18, 0.25, 0.35, 0.7, 0.9, 1.2, 1.8, 2.8, 3.8, 5.8, 8.8, 10, 12.0, 15, 18.0, 30.0, 50.0, 100, 150]
        y = [0.501, 0.508, 0.510, 0.515, 0.55, 0.56, 0.58, 0.59, 0.62, 0.66, 0.70, 0.85, 0.93, 1.04, 1.2, 1.4, 1.54, 1.7, 1.84, 1.95, 1.98, 2.05, 2.1, 2.24, 2.34, 2.45, 2.48]
        def func(x, a, b, c, d, m):
            return d + (a-d) / (1+(x/c)**b)**m
        popt, pcov = curve_fit(func, x, y)
        self.ctr_predict_para = popt
        # a, b, c, d, m = popt
        # yvals=func(x, a, b, c, d, m)
        # plot1=plt.plot(x, y, '*',label='original values')
        # plot2=plt.plot(x, yvals, 'r',label='curve_fit values')
        # plt.xlabel('x axis')
        # plt.ylabel('y axis')
        # plt.legend(loc=4)
        # plt.title('curve_fit')
        # plt.show()

    def impression_co_curvefit(self):
        x = [0.001, 0.003, 0.008, 0.010, 0.05, 0.08, 0.11, 0.13, 0.18, 0.25, 0.35, 0.7, 0.9, 1.2, 1.8, 2.8, 3.8, 5.8, 8.8, 10, 12.0, 15, 18.0, 30.0, 50.0, 100, 150, 300, 1000, 5000]
        y = [1.990, 1.950, 1.930, 1.900, 1.82, 1.75, 1.68, 1.66, 1.58, 1.48, 1.41, 1.15, 1.1, 0.9, 0.85, 0.83, 0.78, 0.62, 0.55, 0.52, 0.51, 0.48, 0.47, 0.46, 0.455, 0.451, 0.448, 0.446, 0.445, 0.442]
        def func(x, a, b, c, d):
            return d + (a-d) / (1+(x/c)**b)
        popt, pcov = curve_fit(func, x, y)
        self.impression_predict_para = popt
        # a, b, c, d = popt
        # yvals=func(x, a, b, c, d)
        # plot1=plt.plot(x, y, '*',label='original values')
        # plot2=plt.plot(x, yvals, 'r',label='curve_fit values')
        # plt.xlabel('x axis')
        # plt.ylabel('y axis')
        # plt.legend(loc=4)
        # plt.title('curve_fit')
        # plt.show()

    def bid_price_curvefit(self):
        x = [0.001, 0.003, 0.008, 0.010, 0.05, 0.08, 0.11, 0.13, 0.18, 0.25, 0.35, 0.7, 0.9, 1.2, 1.8, 2.8, 3.8, 5.8, 8.8, 10, 12.0, 15, 18.0, 30.0, 50.0, 100, 150]
        y = [0.020, 0.022, 0.030, 0.035, 0.05, 0.06, 0.08, 0.10, 0.12, 0.16, 0.21, 0.34, 0.42, 0.52, 0.7, 0.91, 1.1, 1.45, 1.68, 1.76, 1.84, 1.92, 1.95, 1.98, 1.98, 1.99, 1.99]
        y = [yy*1.5 for yy in y]
        def func(x, a, b, c, d, m):
            return d + (a-d) / (1+(x/c)**b)**m
        popt, pcov = curve_fit(func, x, y)
        self.bid_price_para = popt
        # a, b, c, d, m = popt
        # yvals=func(x, a, b, c, d, m)
        # plot1=plt.plot(x, y, '*',label='original values')
        # plot2=plt.plot(x, yvals, 'r',label='curve_fit values')
        # plt.xlabel('x axis')
        # plt.ylabel('y axis')
        # plt.xlim(0, 20)
        # plt.legend(loc=4)
        # plt.title('curve_fit')
        # plt.show()

    def cls_impression_curvefit(self):
        x = [2, 4, 5, 8, 10, 12, 20, 30, 50, 100, 200, 500, 1000, 2000, 5000]
        y = [1.2, 1.32, 1.38, 1.53, 1.6, 1.67, 1.78, 1.85, 1.89, 1.94, 1.96, 1.98, 1.99, 1.99, 1.99]
        y = [yy for yy in y]
        def func(x, a, b, c, d):
            return d + (a-d) / (1+(x/c)**b)
        popt, pcov = curve_fit(func, x, y)
        self.cls_impression_para = popt
        # a, b, c, d = popt
        # yvals=func(x, a, b, c, d)
        # plot1=plt.plot(x, y, '*',label='original values')
        # plot2=plt.plot(x, yvals, 'r',label='curve_fit values')
        # plt.xlabel('x axis')
        # plt.ylabel('y axis')
        # plt.legend(loc=4)
        # plt.xlim(0, 500)
        # plt.title('curve_fit')
        # plt.show()

if __name__ == "__main__":
    m = Model()
    m.cls_impression_curvefit()