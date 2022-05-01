import os

KEYWORD = 1
ASIN = 2
CATEGORY = 3
AUTO_CAMPAIGN = 4

EXACT_MATCH = 5
PHRASE_MATCH = 6
BROAD_MATCH = 7

# keywords classification
min_click = 8
min_cvr = 0.05
max_cvr =0.095

# bid
targeting_min_click = 8
basic_price_default = 0.2
minimum_bid_price = 0.02
broad_co = 0.8
exact_co = 1.2

amzdata_dir = 'Advertising\\script\\report_files'
customize_dir = 'Advertising\\script\\user_customize'
test_dir = 'Advertising\\script\\test_files'
insight_dir = 'Advertising\\script\\insight'
database_dir = 'Advertising\\script\\database'

searchterm_file = os.path.join(amzdata_dir, 'Sponsored Products Search term report.xlsx')
bulk_file = os.path.join(amzdata_dir, 'bulk-a2v0fn8puweidr-20201021-20201220-1608458124423.xlsx')
template_file = os.path.join(amzdata_dir, 'AmazonAdvertisingBulksheetSellerTemplate.xlsx')

disable_tg_file = os.path.join(customize_dir, 'disable-targetings.csv')
negative_st_file = os.path.join(customize_dir, 'negative-searchterms.csv')
optimize_st_file = os.path.join(customize_dir, 'optimize-searchterms.csv')
new_campaign_file = os.path.join(customize_dir, 'new-campaigns.csv')
acos_targeting_file = os.path.join(customize_dir, 'acos_targeting.csv')

searchterm_group_file = os.path.join(test_dir, 'searchterm.csv')
targeting_group_file = os.path.join(test_dir, 'targeting.csv')
target_bid_file = os.path.join(test_dir, 'bid.csv')

searchterm_date_grouped_file = os.path.join(insight_dir, 'searchterm.xlsx')
sku_date_grouped_file = os.path.join(insight_dir, 'sku_data_grouped.csv')

searchterm_info_pickle_path = os.path.join(database_dir, 'searchterm_obj')
skudata_info_pickle_path = os.path.join(database_dir, 'skudata_obj')