import psycopg2

def get_product_record():
    conn = psycopg2.connect(database = 'production', user = 'tianxiahui', password = 'timobubble', host = '123.57.224.241', port = '5432')
    curs=conn.cursor()
    sql = "SELECT * FROM public.api_productsrecord WHERE \"profileId\" = '4116463299964550'"
    curs.execute(sql)
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data