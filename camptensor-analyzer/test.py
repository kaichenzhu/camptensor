
WORD_POINT_CTR = [0.44170693, 2.5198298, 0.66554102, 0.99833884, 1.52838946]
WORD_POINT_CVR = [1.16715955, 4.44685412, 0.50580596, 2.47324923, 0.68486095]
WORD_POINT_ACOS = [1.86128753, 4.06296966, 0.58468287, 3.95402198, 1.08574716]
DEFAULT_CTR = 0.004
DEFAULT_CVR = 0.1
DEFAULT_ACOS = 0.35

def sku_ponint_ctr(x):
    a, b, c, d, m = WORD_POINT_CTR
    return d + (a-d) / (1+(x/c)**b)**m

def sku_ponint_cvr(x):
    a, b, c, d, m = WORD_POINT_CVR
    return d + (a-d) / (1+(x/c)**b)**m

def sku_ponint_acos(x):
    a, b, c, d, m = WORD_POINT_ACOS
    return d + (a-d) / (1+(x/c)**b)**m

if __name__ == '__main__':
    impressions, clicks, orders, cost, sales = 28552, 183, 5, 69, 119
    ctr, cvr, acos = clicks / impressions, orders / clicks, cost / sales
    print(ctr, cvr, acos)
    ctr_co = sku_ponint_ctr(ctr/DEFAULT_CTR)
    cvr_co = sku_ponint_cvr(cvr/DEFAULT_CVR)
    acos_co = sku_ponint_acos(0.3/acos)
    print(ctr_co, cvr_co, acos_co, ctr_co * cvr_co * acos_co)