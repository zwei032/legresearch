from selectorlib import Extractor
import requests
import platform
import pandas as pd
import datetime as dt
from math import floor 

path = '/Users/zeouwei/OneDrive/compleglab 2/data/us_data'

def create_date(date_time):
    month_name = date_time.split(',')[0].split(' ')[0]
    month = dt.datetime.strptime(month_name, '%b').month
    day = date_time.split(',')[0].split(' ')[1]
    year = date_time.split(',')[1].replace(' ', '')
    date = str(month)+'/'+day+'/'+year
    return date

def data_series(link, i):
    import numpy as np
    # Create dictionaries to make changes in strings
    dparty = {'Democratic':'D', 'Republican': 'R', 'Independent':'I'}
    dstate = {
        "Alabama": "AL",
        "Alaska": "AK",
        "Arizona": "AZ",
        "Arkansas": "AR",
        "California": "CA",
        "Colorado": "CO",
        "Connecticut": "CT",
        "Delaware": "DE",
        "Florida": "FL",
        "Georgia": "GA",
        "Hawaii": "HI",
        "Idaho": "ID",
        "Illinois": "IL",
        "Indiana": "IN",
        "Iowa": "IA",
        "Kansas": "KS",
        "Kentucky": "KY",
        "Louisiana": "LA",
        "Maine": "ME",
        "Maryland": "MD",
        "Massachusetts": "MA",
        "Michigan": "MI",
        "Minnesota": "MN",
        "Mississippi": "MS",
        "Missouri": "MO",
        "Montana": "MT",
        "Nebraska": "NE",
        "Nevada": "NV",
        "New Hampshire": "NH",
        "New Jersey": "NJ",
        "New Mexico": "NM",
        "New York": "NY",
        "North Carolina": "NC",
        "North Dakota": "ND",
        "Ohio": "OH",
        "Oklahoma": "OK",
        "Oregon": "OR",
        "Pennsylvania": "PA",
        "Rhode Island": "RI",
        "South Carolina": "SC",
        "South Dakota": "SD",
        "Tennessee": "TN",
        "Texas": "TX",
        "Utah": "UT",
        "Vermont": "VT",
        "Virginia": "VA",
        "Washington": "WA",
        "West Virginia": "WV",
        "Wisconsin": "WI",
        "Wyoming": "WY",
        "District of Columbia": "DC",
        "American Samoa": "AS",
        "Guam": "GU",
        "Northern Mariana Islands": "MP",
        "Puerto Rico": "PR",
        "United States Minor Outlying Islands": "UM",
        "U.S. Virgin Islands": "VI",
    }

    e = Extractor.from_yaml_file('selectorlib_yml/roll-call-votes.yml')
    r = requests.get(link)
    data = e.extract(r.text)
    split = data['date'].split(' \r\n')
    date_time = split[0]
    date = create_date(date_time)
    year = date[len(date) - 4 : len(date)]


    cong_sess = split[len(split)-1]
    congress = cong_sess.split(', ')[0].split(' ')[-2]
    congress[: len(congress) - 2]
    session = cong_sess.split(', ')[1][0]

    vote_question = data['question'].split(': ')[1]
    explanation = data['explanation']

    rbn = data['roll_number'].split('\r\n')
    roll_number = int(rbn[0].split(' ')[2])
    if ':' in rbn[len(rbn)-1]:
        bill = rbn[len(rbn)-1].split(': ')[1]
    else:
        bill = rbn[len(rbn)-1].replace(' ', '')

    vote_type = data['vote_type'].split(': ')[1]
    status = data['status'].split(': ')[1]
    yea = data['yea'].split(': ')[1]
    nay = data['nay'].split(': ')[1]
    present = data['present'].split(': ')[1]
    not_voting = data['not_voting'].split(': ')[1]

    dmajority = {'116th':'R', '117th':'D'}

    data_agg = pd.DataFrame({'year': year, 'roll_number': roll_number,
                         'congress': congress, 'session': session,
                         'chamber': 1, 'bill': bill, 'vote_question': vote_question,
                         'vote_type': vote_type, 'date': date, 'majority': dmajority[congress],
                         'vote_result': status, 'description': explanation, 'yea': yea, 'nay': nay, 
                         'present': present, 'not_voting': not_voting}, index=[i])

    if data['party'] is not None:
        party = [dparty[x] for x in data['party']]
    else:
        party =  np.nan

    if data['state'] is not None:
        state = [dstate[x] for x in data['state']]
    else:
        state = np.nan

    if data['representative'] is not None:
        rep = data['representative']
        rep = rep[0:len(rep)-1]
    else:
        rep = np.nan

    detailed = pd.DataFrame({'last_name':rep,'party':party, 'state':state, 'vote':data['vote']})
    detailed['roll_number'] = roll_number
    detailed['congress'] = congress

    return {'agg':data_agg, 'detailed':detailed}

year = 2020

rcv_data = pd.DataFrame()
rcv_details = pd.DataFrame()
j = 0
if year == 2020:
    ivoten = 7
    fvoten = 53
    for i in range(ivoten, fvoten+1):
        page = floor((fvoten-i)/10) + 1
        number = str(i) if i>=10 else '0'+str(i)
    
        if page > 1:
            link = 'https://clerk.house.gov/Votes/'+str(year)+'2'+number+'?Page='+str(page)
        else:
            link = 'https://clerk.house.gov/Votes/'+str(year)+'2'+number
        df = data_series(link, j)
        rcv_data = rcv_data.append(df['agg'])
        rcv_details = rcv_details.append(df['detailed'])
        j += 1
        print('Roll Call Vote Number '+str(i)+' done for year '+str(year))
else:
    ivoten = 1
    fvoten = 449
    for i in range(ivoten, fvoten+1):
        page = floor((fvoten-i)/10) + 1
        link = 'https://clerk.house.gov/Votes/'+str(year)+str(i)+'?Page='+str(page)
        df = data_series(link, j)
        rcv_data = rcv_data.append(df['agg'])
        rcv_details = rcv_details.append(df['detailed'])
        j += 1
        print('Roll Call Vote Number '+str(i)+' done for year '+str(year))

save = True 

if save:
    rcv_data.to_csv(path+'/scraped/roll_call_vote_house/us_house_vote_'+str(year)+'_new.csv', index=False)
    rcv_details.to_csv(path+'/scraped/roll_call_vote_house/us_house_vote_'+str(year)+'_details.csv', index=False)

