import csv
import matplotlib.pyplot as plt
import pickle

def write_group_data(portfolio_list, search_term_path, targeting_path):
    with open(search_term_path,"w",newline='') as csvfile: 
        writer = csv.writer(csvfile)
        writer.writerow(["name","type","impression","clicks", "orders"])
        for _, portfolio in portfolio_list.items():
            for _, search_term in portfolio.search_term_list.items():
                name = search_term['searchterm']
                term_type = search_term['type']
                impression = search_term['impressions']
                clicks = search_term['clicks']
                orders = search_term['orders']
                writer.writerow([name,term_type,impression,clicks,orders])

    with open(targeting_path,"w",newline='') as csvfile: 
        writer = csv.writer(csvfile)
        writer.writerow(["name","type","impression","clicks", "orders"])
        for _, portfolio in portfolio_list.items():
            for _, targeting in portfolio.targeting_list.items():
                name = targeting['target']
                targeting_type = targeting['type']
                impression = targeting['impressions']
                clicks = targeting['clicks']
                orders = targeting['orders']
                writer.writerow([name,targeting_type,impression,clicks,orders])


def view_data_distribution(portfolio_list, minimum_st_clicks, minimum_tg_clicks):
    x, y, z = [], [], []
    for _, portfolio in portfolio_list.items():
        for _, search_term in portfolio.search_term_list.items():
            clicks = search_term['clicks']
            orders = search_term['orders']
            if orders < 3: continue
            
            impression = search_term['impressions']
            cvr = orders / clicks
            ctr = clicks / impression
            if cvr > 1: cvr = 1
            x.append(ctr)
            y.append(cvr)
            z.append(orders*20)
    plt.xlabel('CTR')
    plt.ylabel('CVR')
    plt.scatter(x,y,s=z,alpha=0.6)
    plt.show()


def list_to_csv(list_obj, file_path, header=None):
    file = open(file_path, 'w+', newline ='')
    with file:
        write = csv.writer(file)
        if header:
            write.writerow(header)
        write.writerows(list_obj)

def write_obj_local(path, data):
    f = open(path, 'wb')
    pickle.dump(data, f)
    f.close()

def read_obj_local(path):
    f = open(path, 'rb')
    data = pickle.load(f)
    return data