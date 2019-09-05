import requests, bs4
import pandas as pd
from datetime import datetime

year = datetime.now().year

url = f'https://projects.fivethirtyeight.com/{year}-nfl-predictions/games'

res = requests.get(url)
res.raise_for_status()
nflsoup = bs4.BeautifulSoup(res.text, 'html.parser')
weektexts = nflsoup.select('.week > h3')
weeks = [x for x in nflsoup.select('.week')]


# {team, odds for (i,j) in}
nflweeklyodds ={}
for count, week in enumerate(weeks):
    nflweeklyodds[weektexts[count].getText()]={i.getText():float(j.getText().strip('%'))  for (i,j) in zip(weeks[count].select('.td.text.team'),
                    weeks[count].select('.td.number.chance')
                    )
                    
                    }
# print(len(nflweeklyodds))                    
# for key, item in nflweeklyodds.items():
    # print(key, item)

nflodds_df = pd.DataFrame(nflweeklyodds)
nflodds_df.sort_index(inplace=True)
# null values should mean the team is on bye, so they have a zero percent chance of winning
nflodds_df = nflodds_df.fillna(0)
# nflodds_df['Week 4'].astype('float')
# print(nflodds_df)
# print(nflodds_df.info())

# print(nflodds_df['Week 5'] >50)
# this should count the number of weeks remaining where the team has better than 50% win odds
nflodds_df['Future_Value'] = nflodds_df.where(nflodds_df > 50).count(axis=1)
# print(nflodds_df)
print(nflodds_df[nflodds_df.iloc[:,0] > 50].sort_values('Future_Value'))