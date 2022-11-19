#! ../../env/bin/python3

from bs4 import BeautifulSoup
import pandas as pd
import requests

DATADIR = '../../data/processed/housing-off-campus/'

req_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.8',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}

with requests.Session() as s:
    base_url = 'https://www.zillow.com/san-diego-ca-92122/rentals/'
    
    # initialize variables
    page_num = 1
    status = 200
    zillow_text = ''
    
    print('Scraping page {}'.format(page_num))
    
    while status == 200:
        # update every 5 pages
        if page_num % 5 == 0:
            print('Scraping page {}'.format(page_num))
        
        # add page number suffix to url
        if page_num != 1:
            url = base_url + str(page_num+1) + '_p/'
        else:
            url = base_url
            
        # get page    
        r = s.get(url, headers=req_headers)
        
        try:
            soup = BeautifulSoup(r.content, 'html.parser')
            
            # append text
            zillow_text += soup.get_text()
            
        except:
            print('Last page reached.\n Total pages scraped: {}'.format(page_num-1))
        
        # update status and page number                         
        status = r.status_code
        page_num += 1
        
        
# initialize dataframe
df = pd.DataFrame(columns=['price', 'unit-type', 'beds', 'note'])

# populate with scraped data
df['price'] = [x.split(' ')[0] for x in zillow_text.split('$')[1:]]
df['note'] = ['minimum price listed in range' if '+' in x else 'exact price' for x in df['price']]
df['price'] = [int(x.split('+')[0].replace(',', '')) for x in df['price']]
df['unit-type'] = [x.split(' ')[1] for x in zillow_text.split('$')[1:]]
df['beds'] = [1 if x == 'Studio' else int(x) for x in df['unit-type']]
df['bedrooms'] = [0 if x == 'Studio' else int(x) for x in df['unit-type']]

# create price per bed column
df['price-per-bed'] = round(df['price'] / df['beds'], 2)

# get summary statistics
stats = pd.concat([df.describe().T, df.median(numeric_only=True)], axis=1).rename(columns={0: 'median'})

# save to csv
df.to_csv('{}/zillow-92122-111922.csv'.format(DATADIR), index=False)
stats.to_csv('{}/zillow-stats-92122-111922.csv'.format(DATADIR), index=False)