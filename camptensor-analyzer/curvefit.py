import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np

def curvefunc(x, a, b, c, d, m):
    return d + (a-d) / (1+(x/c)**b)**m

def curvefit(x, y, func, xlim, ylim, show=False):
    popt, pcov = curve_fit(func, x, y, maxfev=500000)
    if not show: return popt
    plt.switch_backend('agg')
    a, b, c, d, m = popt
    yvals=func(x, a, b, c, d, m)
    plot1=plt.plot(x, y, '*',label='original values')
    plot2=plt.plot(x, yvals, 'r',label='curve_fit values')
    plt.xlabel('x axis')
    plt.ylabel('y axis')
    plt.xlim(0, xlim)
    plt.ylim(0, ylim)
    plt.legend(loc=4)
    plt.title('curve_fit')
    plt.savefig("curve_fit.jpg")
    return None

if __name__ == '__main__':
    # impression layer
    # x = [0.01, 0.10, 0.15, 0.20, 0.25, 0.35, 0.45, 0.58, 0.70, 0.85, 1.0, 1.20, 1.5, 1.8, 2.5, 3.0, 3.5, 5.0, 8.0, 10,  12,  15,  18,  25,  50,  100,  150,  300, 1000, 5000]
    # y = [0.50, 0.52, 0.55, 0.58, 0.62, 0.68, 0.73, 0.76, 0.80, 0.92, 1.1, 1.15, 1.2, 1.35, 1.45, 1.58, 1.68, 1.75, 1.86, 1.92, 1.95, 1.96, 1.97, 1.98, 1.99, 1.99, 1.99, 1.99, 1.99, 1.99]
    # IMPRESSION_LAYER = curvefit(x, y, curvefunc, 50, 5, False)
    # print(IMPRESSION_LAYER)

    # roi layer
    # x = [0.01, 0.10, 0.15, 0.20, 0.25, 0.35, 0.45, 0.58, 0.70, 0.85, 1.0, 1.20, 1.5, 1.8, 2.5, 3.0, 3.5, 5.0, 8.0, 10,  12,  15,  18,  25,  50,  100,  150,  300, 1000, 5000]
    # y = [0.25, 0.26, 0.28, 0.3, 0.32, 0.42, 0.52, 0.62, 0.76, 0.92, 1.1, 1.25, 1.53, 1.88, 2.18, 2.28, 2.38, 2.48, 2.62, 2.69, 2.74, 2.76, 2.81, 2.85, 2.89, 2.92, 2.94, 2.96, 2.98, 2.99]
    # ROI_LAYER = curvefit(x, y, curvefunc, 5, 5, False)
    # print(ROI_LAYER)

    # cvr layer
    # x = [0.01, 0.10, 0.15, 0.20, 0.25, 0.35, 0.45, 0.58, 0.70, 0.85, 1.0, 1.20, 1.5, 1.8, 2.5, 3.0, 3.5, 5.0, 8.0, 10,  12,  15,  18,  25,  50,  100,  150,  300, 1000, 5000]
    # y = [0.25, 0.26, 0.28, 0.3, 0.32, 0.42, 0.52, 0.62, 0.76, 0.92, 1.1, 1.25, 1.53, 1.88, 2.18, 2.28, 2.38, 2.48, 2.62, 2.69, 2.74, 2.76, 2.81, 2.85, 2.89, 2.92, 2.94, 2.96, 2.98, 2.99]
    # CVR_LAYER = curvefit(x, y, curvefunc, 2, 2, True)
    # print(CVR_LAYER)

    # ctr layer
    # x = [0.01, 0.10, 0.15, 0.20, 0.25, 0.35, 0.45, 0.58, 0.70, 0.85, 1, 1.20,  1.5,  1.8, 2.5, 3.0, 3.5, 5.0, 8.0,  10] #,  12,  15,  18,  25,  50,  100,  150,  300, 1000, 5000]
    # y = [0.05, 0.08, 0.12, 0.18, 0.23, 0.34, 0.46, 0.59, 0.68, 0.82, 1, 1.11, 1.12, 1.29, 1.4, 1.6, 1.7, 1.9, 2.3, 2.4] #, 3.2, 3.5, 3.6, 3.8, 3.9, 3.92, 3.94, 3.96, 3.98, 3.99]
    # CTR_LAYER = curvefit(x, y, curvefunc, 1, 1, False)
    # print(CTR_LAYER)

    # head layer
    # x = [0.01, 0.10, 0.15, 0.20, 0.25, 0.35, 0.45, 0.58, 0.70, 0.85, 1, 1.20,  1.5, 1.8, 2.5, 3.0, 3.5,   5, 8.0, 10, 12,  15,  18,  25,  50,  100,  150,  300]
    # y = [0.30, 0.32, 0.35, 0.37, 0.45, 0.52, 0.62, 0.72, 0.81, 0.91, 1, 1.08, 1.12, 1.18, 1.28, 1.32, 1.39, 1.48, 1.56, 1.6, 1.65, 1.69, 1.72, 1.78, 1.86, 1.92, 1.94, 1.96]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 300, 2, False)
    # print(HEAD_LAYER)


    # budget optimization
    # x = [0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.2, 1.5, 1.8, 2, 2.2, 2.5, 2.8, 3, 5, 7, 10]
    # y = [0.8, 0.81, 0.83, 0.85, 0.86, 0.88, 0.92, 0.93, 0.98, 1.1, 1.2, 1.32, 1.48, 1.62, 1.71, 1.84, 1.92, 2, 2.1, 2.4, 2.45, 2.5]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 2, 3, True)
    # HEAD_LAYER = curvefit(x, y, curvefunc, 2, 3, False)
    # print(HEAD_LAYER)

    # bid prediction
    # x = [0, 0.1, 0.2, 0.4, 0.6, 0.8, 0.9, 1, 1.1, 1.2, 1.5, 1.8, 2, 2.5, 3, 4, 6, 10, 20]
    # y = [0.3, 0.35, 0.45, 0.55, 0.7, 0.9, 0.95, 1, 1.1, 1.18, 1.57, 1.82, 1.91, 2.13, 2.4, 2.6, 2.88, 2.95, 2.99]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 4, 3, False)
    # print(HEAD_LAYER)

    # classify ctr
    # x = [0, 0.1, 0.5, 0.8, 1, 1.2, 1.5, 2, 3, 10, 50]
    # y = [0.6, 0.62, 0.75, 0.9, 1, 1.12, 1.15, 1.2, 1.23, 1.27, 1.299]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 2, 2, True)
    # HEAD_LAYER = curvefit(x, y, curvefunc, 5, 1.3, False)
    # print(HEAD_LAYER)

    # classify cvr
    # x = [0, 0.1, 0.5, 0.8, 1, 1.2, 1.5, 2, 3, 10, 50]
    # y = [0, 0.1, 0.6, 0.9, 1, 1.1, 1.2, 1.3, 1.38, 1.63, 1.69]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 20, 3, True)
    # HEAD_LAYER = curvefit(x, y, curvefunc, 2, 3, False)
    # print(HEAD_LAYER)

    # classify acos
    # x = [0, 0.1, 0.2, 0.3, 0.5, 0.8, 1, 1.5, 2, 3, 5, 10, 20, 50]
    # y = [1.5, 1.4, 1.35, 1.3, 1.2, 1.1, 1, 0.8, 0.65, 0.55, 0.52, 0.51, 0.5, 0.5]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 2, 3, True)
    # HEAD_LAYER = curvefit(x, y, curvefunc, 10, 3, False)
    # print(HEAD_LAYER)

    # daily bid ctr
    # x = [0, 0.1, 0.2, 0.3, 0.5, 0.8, 1, 1.5, 2, 3, 5, 10, 20, 50]
    # y = [1.2, 1.18, 1.15, 1.13, 1.1, 1.05, 1, 0.96, 0.93, 0.9, 0.88, 0.86, 0.86, 0.85]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 4, 2, False)
    # print(HEAD_LAYER)

    # daily bid cvr
    # x = [0, 0.1, 0.2, 0.3, 0.5, 0.8, 1, 1.5, 2, 3, 5, 10, 20, 50]
    # y = [0.9, 0.9, 0.91, 0.92, 0.93, 0.95, 1, 1.05, 1.15, 1.22, 1.35, 1.45, 1.48, 1.5]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 2, 2, False)
    # print(HEAD_LAYER)

    # daily acos
    # x = [0, 0.1, 0.2, 0.3, 0.5, 0.8, 1, 1.2, 2, 3, 5, 10, 20, 50]
    # y = [1.5, 1.45, 1.42, 1.35, 1.2, 1.05, 1, 0.97, 0.96, 0.95, 0.93, 0.91, 0.9, 0.9]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 10, 2, False)
    # print(HEAD_LAYER)

    # bidopt ctr
    # x = [0, 0.1, 0.2, 0.3, 0.5, 0.8, 1, 1.5, 2, 3, 5, 10, 20, 50]
    # y = [0.9, 0.91, 0.92, 0.93, 0.95, 0.98, 1, 1.05, 1.1, 1.12, 1.14, 1.18, 1.19, 1.2]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 100, 2, True)
    # HEAD_LAYER = curvefit(x, y, curvefunc, 4, 2, False)
    # print(HEAD_LAYER)

    # # bidopt cvr
    # x = [0, 0.1, 0.2, 0.3, 0.5, 0.8, 1, 1.5, 2, 3, 5, 10, 20, 50]
    # y = [0.7, 0.73, 0.78, 0.81, 0.85, 0.98, 1, 1.1, 1.2, 1.3, 1.5, 1.57, 1.59, 1.6]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 3, 2, True)
    # HEAD_LAYER = curvefit(x, y, curvefunc, 4, 2, False)
    # print(HEAD_LAYER)

    # bidopt acos
    # x = [0, 0.1, 0.2, 0.3, 0.5, 0.8, 1, 1.5, 2, 3, 5, 10, 20, 50]
    # y = [1.5, 1.45, 1.4, 1.32, 1.2, 1.1, 1, 0.95, 0.9, 0.83, 0.8, 0.75, 0.72, 0.7]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 3, 2, True)
    # HEAD_LAYER = curvefit(x, y, curvefunc, 4, 2, False)
    # print(HEAD_LAYER)

    # click negative acos
    # x = [0, 0.1, 0.2, 0.3, 0.5, 0.8, 1, 1.5, 2, 3, 5, 10, 20, 50]
    # y = [0.8, 0.81, 0.82, 0.83, 0.84, 0.88, 1, 1.1, 1.15, 1.2, 1.3, 1.42, 1.46, 1.5]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 3, 3, True)
    # HEAD_LAYER = curvefit(x, y, curvefunc, 4, 2, False)
    # print(HEAD_LAYER)

    # max bid layer
    # x = [0,   0.5,  0.8,    1, 2,   4, 6, 10, 20,  30,   50,    80, 150]
    # y = [0.5, 0.54, 0.6, 0.76, 1, 1.5, 2, 2.5, 3.6, 4.2, 4.8,  4.9, 4.99]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 5, 7, True)
    # HEAD_LAYER = curvefit(x, y, curvefunc, 4, 2, False)
    # print(HEAD_LAYER)

    # max bid ctr
    # x = [0, 0.001, 0.002, 0.003, 0.005, 0.008, 0.01, 0.012, 0.015, 0.02, 0.05, 0.1, 0.3, 0.5, 2]
    # y = [1.2, 1.19, 1.17, 1.1, 1, 0.95, 0.9, 0.87, 0.85, 0.81, 0.8, 0.8, 0.8, 0.8, 0.8]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 2, 1.5, True)
    # HEAD_LAYER = curvefit(x, y, curvefunc, 4, 2, False)
    # print(HEAD_LAYER)

    # max bid cvr
    # x = [0, 0.01, 0.02, 0.03, 0.05, 0.08, 0.1, 0.12, 0.15, 0.2, 0.3, 0.5, 0.8, 1, 2]
    # y = [0.8, 0.81, 0.85, 0.88, 0.92, 0.98, 1.05, 1.1, 1.2, 1.3, 1.38, 1.46, 1.48, 1.49, 1.5]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 0.9, 1.5, True)
    # HEAD_LAYER = curvefit(x, y, curvefunc, 4, 2, False)
    # print(HEAD_LAYER)

    # word point layer
    # x = [0, 0.5, 0.8, 1, 2, 4, 6, 10, 20, 30, 50, 80, 150]
    # y = [1, 1.3, 1.8, 2, 2.3, 3, 3.4, 3.9, 3.95, 3.98, 3.99, 3.99, 4]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 50, 7, True)
    # HEAD_LAYER = curvefit(x, y, curvefunc, 4, 2, False)
    # print(HEAD_LAYER)

    # word point head
    # x = [0,1,2,5,8,12,20,30,50,60]
    # y = [0.5,1,1.6,2,2.236,2.4,2.7,2.93,3.1,3.162]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 10, 7, True)
    # HEAD_LAYER = curvefit(x, y, curvefunc, 4, 2, False)
    # print(HEAD_LAYER)

    # front end ctr point
    # x = np.array([0, 0.001, 0.002, 0.003, 0.004, 0.008, 0.01, 0.012, 0.015, 0.02, 0.05, 0.1, 0.3, 0.5, 2])
    # y = np.array([0, 10, 25, 35, 50, 60, 70, 75, 79, 83, 90, 95, 99, 99, 99])
    # HEAD_LAYER = curvefit(x, y, curvefunc, 0.1, 100, True)
    # HEAD_LAYER = curvefit(x, y, curvefunc, 4, 2, False)
    # print(HEAD_LAYER)

    # front end cvr point
    # x = [0, 0.01, 0.02, 0.03, 0.05, 0.08, 0.1, 0.12, 0.15, 0.2, 0.3, 0.5, 0.8, 1, 2]
    # y = [0, 4, 10, 15, 30, 40, 55, 60, 70, 75, 85, 95, 99, 99, 99]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 0.5, 100, True)
    # HEAD_LAYER = curvefit(x, y, curvefunc, 4, 2, False)
    # print(HEAD_LAYER)

    # front end acos point
    # x = [0, 0.01, 0.02, 0.03, 0.05, 0.08, 0.1, 0.12, 0.15, 0.2, 0.3, 0.5, 0.8, 1, 2]
    # y = [99, 98, 97, 96, 93, 90, 85, 82, 78, 72, 60, 35, 10, 1, 0]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 1, 100, True)
    # HEAD_LAYER = curvefit(x, y, curvefunc, 4, 2, False)
    # print(HEAD_LAYER)

    # sku point ctr
    # x = [0.01,   0.1, 0.2,  0.3, 0.4, 0.5,  0.6,  0.8, 0.9,    1,  1.2,  1.5,    2, 3, 5, 10]
    # y = [0.43, 0.46, 0.48, 0.55, 0.6, 0.7, 0.76, 0.88, 0.9, 0.93, 0.95, 0.97, 0.99, 1, 1,  1]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 2, 1, True)
    # HEAD_LAYER = curvefit(x, y, curvefunc, 4, 2, False)
    # print(HEAD_LAYER)

    # sku point cvr
    # x = [0.01,  0.1,  0.2,  0.3, 0.4, 0.5, 0.6, 0.8, 0.9,     1,  1.2,  1.5,    2,    3,    5,  10]
    # y = [1.13, 1.16,  1.2,  1.3, 1.4, 1.6, 1.9, 2.2, 2.28, 2.32, 2.35, 2.38, 2.43, 2.48, 2.49, 2.5]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 2, 3, True)
    # HEAD_LAYER = curvefit(x, y, curvefunc, 4, 2, False)
    # print(HEAD_LAYER)

    # sku point acos
    # x = [0.01,  0.1,  0.2, 0.3, 0.4, 0.5, 0.6, 0.8,  0.9,    1,  1.2,  1.5,   2,    3,    5, 10]
    # y = [1.85, 1.856, 1.9,   2, 2.3, 2.6,   3, 3.6, 3.72, 3.78, 3.82, 3.87, 3.9, 3.97, 3.99,  4]
    # HEAD_LAYER = curvefit(x, y, curvefunc, 10, 4, True)
    # HEAD_LAYER = curvefit(x, y, curvefunc, 4, 2, False)
    # print(HEAD_LAYER)

    # sku point stock co
    x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    y = [0.4, 0.42, 0.44, 0.48, 0.5 ,0.7, 0.9, 1.15, 1.7, 2, 2.5]
    HEAD_LAYER = curvefit(x, y, curvefunc, 10, 3, True)
    HEAD_LAYER = curvefit(x, y, curvefunc, 4, 2, False)
    print(HEAD_LAYER)