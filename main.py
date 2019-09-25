import requests, bs4, smtplib, json
import pandas as pd
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
# get credentials from local json file
with open('credentials.json') as creds:
    credentials = json.load(creds)
email_sender = credentials['email_sender']
email_recipient = credentials['email_recipient']
email_password = credentials['email_password']
email_server = credentials['email_server']
email_port = int(credentials['email_port'])

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
results = nflodds_df[nflodds_df.iloc[:,0] > 50].sort_values('Future_Value') 
print(results)

# email results
FROM = email_sender
TO = email_recipient  
SUBJECT = f'Survival pool report for the week of {datetime.now().strftime("%d %b %Y")}'
# summary = "\n".join(edit_count)
# details = ",\n ".join(edited_files)
TEXT = results.to_html()
# print(TEXT)
msg = MIMEMultipart()
msg['From'] = FROM
msg['To'] = TO
msg['Subject'] = SUBJECT
msg.attach(MIMEText(TEXT, 'html'))


#msg.attach(file)

# Connect to email server and send email
with smtplib.SMTP(email_server, email_port) as s:
    s.starttls()
    s.login(email_sender, email_password)
    s.send_message(msg)
# print("Done in " + str(datetime.now()- start) )