import requests
import os
import json
import pandas as pd
import yagmail
import datetime as dt
import time
from premailer import transform

bearer_token = '{INSERT YOUR TOKEN HERE}'
search_url = "https://api.twitter.com/2/tweets/search/recent"

# Change query term here
query_params = {'query': 'Disney World -is:retweet has:media lang:en', 
                'tweet.fields':'created_at,entities,attachments', 
                'expansions': 'author_id,attachments.media_keys',
                'media.fields': 'url',
                'max_results': '10'}
                

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()
    print(url)

def main():
    global data
    json_response = connect_to_endpoint(search_url, query_params)
    #print(json.dumps(json_response, indent=4, sort_keys=True))
    data = json.dumps(json_response, indent=4, sort_keys=True)
    data = json.loads(data)
    

# Create dictionary mapping Name & User ID
names = {}
for i in data['includes']['users']:
    names[i['id']] = i['name']
    
# Create dictionary mapping Media Key & URL
pics = {}
for i in data['includes']['media']:
    pics[i['media_key']] = i['url']
    
# Create DF and replace Author ID with Name
df = pd.DataFrame(data['data'])
df = df.replace({"author_id": names})


# Convert Meedia to HTML
att = []

for i in df['attachments']:
    str1 = ""
    for j in i['media_keys']:
        str1 += '<img src="'+ pics[j] + '" width="250" > '
    att.append(str1)
    
df['media'] = att
df = df[['author_id', 'text', 'media']]

# Set dataframe styles here
s = df.style
s.set_properties(**{
    'font-size': '11pt',
    'font-family': 'Calibri'
})
s.set_properties(**{'vertical-align': 'top'})
s.set_properties(subset = ['text'],**{'text-align': 'center'})
s.set_properties(subset = ['media'],**{'text-align': 'left'})
s.set_properties(subset = ['media'], **{'width': '300px'})
s.background_gradient()

# Convert DataFrame to HTML
html = transform(s.hide_index().render().replace("\n", ""))

# Send email with HTML code in copy
yag = yagmail.SMTP('{YOUR GMAIL NAME}', '{YOUR PASSWORD}')
yag.send(to='{EMAIL RECIEPIENT]',
         subject='Twitter Pictures' ,
         contents= html)
