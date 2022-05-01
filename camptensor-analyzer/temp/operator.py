import pandas as pd
from config import *

class Operator:
    def __init__(self):
        self.template = pd.read_excel(template_file, sheet_name='Sponsored Products Campaigns')
        self.idx, _ = self.template.shape


    def create_campaigns(self):
        new_campaigns = pd.read_csv(new_campaign_file).values.tolist()
        for i in range(len(new_campaigns)):
            campaign = new_campaigns[i]
            campaign_name, campaign_type, dailybudget, adgroup, maxbid, sku = campaign
            if pd.isna(campaign_name):
                print('line %d does not has campaign name' % (i+1))
                continue
            if pd.isna(campaign_type):
                print('line %d does not has campaign type, set it auto' % (i+1))
                campaign_type = 'Auto'
            elif campaign_type not in ['Auto', 'Manual']:
                print('line %d has wrong campaign type, set it auto' % (i+1))
                campaign_type = 'Auto'
            if pd.isna(dailybudget):
                print('line %d does not has dailybudget, set it 2' % (i+1))
                dailybudget = 2
            if pd.isna(adgroup):
                print('line %d does not has goup name' % (i+1))
                continue
            if pd.isna(maxbid):
                print('line %d does not has maxbid, set it 0.5' % (i+1))
                maxbid = 0.5
            if pd.isna(sku):
                print('line %d does not has ads' % (i+1))
                continue
            
            # create campaign
            self.template.at[self.idx, 'Record Type'] = 'Campaign'
            self.template.at[self.idx, 'Campaign'] = campaign_name
            self.template.at[self.idx, 'Campaign Daily Budget'] = dailybudget
            self.template.at[self.idx, 'Campaign Targeting Type'] = campaign_type
            self.template.at[self.idx, 'Campaign Status'] = 'enabled'
            self.template.at[self.idx, 'Bidding strategy'] = 'Dynamic bidding (up and down)'
            self.idx += 1
            # bind group to campaign
            self.template.at[self.idx, 'Record Type'] = 'Ad Group'
            self.template.at[self.idx, 'Campaign'] = campaign_name
            self.template.at[self.idx, 'Ad Group'] = adgroup
            self.template.at[self.idx, 'Max Bid'] = maxbid
            self.template.at[self.idx, 'Ad Group Status'] = 'enabled'
            self.idx += 1
            # bind sku to group
            self.template.at[self.idx, 'Record Type'] = 'Ad'
            self.template.at[self.idx, 'Campaign'] = campaign_name
            self.template.at[self.idx, 'Ad Group'] = adgroup
            self.template.at[self.idx, 'SKU'] = sku
            self.template.at[self.idx, 'Status'] = 'enabled'
            self.idx += 1

if __name__ == "__main__":
    o = Operator()
    o.create_campaigns()