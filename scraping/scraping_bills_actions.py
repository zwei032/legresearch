import pandas as pd
import requests
from selectorlib import Extractor
import platform

def ext_bill_type(strg):
    text = strg[::-1]
    typer = text.split('.', maxsplit=1)[1]
    return typer[::-1]

# Function to create df from a link and a yml extractor

def create_data_actions(link, extractor):
    r = requests.get(link)
    l = extractor.extract(r.text)['all_actions']
    n = extractor.extract(r.text)['n_actions'].replace(
        '[', '').replace(']', '')
    n = n.replace(',', '')
    n = int(n)
    if len(l)/n == 3:
        date = [l[x] for x in range(len(l)) if (
            l[x].__contains__('/')) and (len(l[x]) < 19)]
        chamber = [l[x]
                   for x in range(len(l)) if l[x] in ['', 'House', 'Senate']]
        action = [l[x] for x in range(len(l)) if (
            l[x] not in date) and (l[x] not in chamber)]
        df = pd.DataFrame({'date': date, 'action': action, 'chamber': chamber})
    else:
        date = [l[x] for x in range(len(l)) if l[x].__contains__(
            '/') and (len(l[x]) < 19)]
        action = [l[x] for x in range(len(l)) if l[x] not in date]
        df = pd.DataFrame({'date': date, 'action': action})
    return df

# Function to create congress.gov link

def create_link(congress, bill_type, bill_number):
    map_btype = {'H.Con.Res': 'house-concurrent-resolution', 'H.J.Res': 'house-joint-resolution',
                 'H.Res': 'house-resolution', 'H.R': 'house-bill', 'S.Con.Res': 'senate-concurrent-resolution',
                 'S.J.Res': 'senate-joint-resolution', 'S.Res': 'senate-resolution', 'S': 'senate-bill'}
    ntype = map_btype[bill_type]
    if congress % 10 == 1:
        pt = 'st'
    elif congress % 10 == 2:
        pt = 'nd'
    elif congress % 10 == 2:
        pt = 'rd'
    else:
        pt = 'th'
    link = 'https://www.congress.gov/bill/' + \
        str(congress)+pt+'-congress/'+ntype+'/' + \
        str(int(bill_number))+'/all-actions'
    return link

# Import bills data and only keep unique bill numbers by congress

path = '/Users/zeouwei/OneDrive/compleglab 2/data/us_data'
bills = pd.read_csv(path+'/final/bills.csv')
billsact = bills[['congress', 'bill_incong_number',
                  'bill_number']].drop_duplicates()
billsact = billsact.dropna(subset=['bill_number']).reset_index()
billsact['bill_type'] = billsact['bill_number'].apply(ext_bill_type)

# Iterate over all the possible bills to extract actions
nb = len(billsact)
bills_actions = pd.DataFrame()

for i in range(160001, nb):
    bi = billsact.iloc[i]
    link = create_link(bi['congress'], bi['bill_type'],
                       bi['bill_incong_number'])
    e = Extractor.from_yaml_file('selectorlib_yml/bills_actions.yml')
    try:
        subframe = create_data_actions(link, e)
        subframe['congress'] = bi['congress']
        subframe['bill_number'] = bi['bill_number']
        bills_actions = bills_actions.append(subframe)
        print('Iteration', i, 'for Bill', int(
            bi['bill_incong_number']), 'Congress', bi['congress'])
    except:
        try:
            subframe = create_data_actions(link, e)
            subframe['congress'] = bi['congress']
            subframe['bill_number'] = bi['bill_number']
            bills_actions = bills_actions.append(subframe)
            print('Iteration', i, 'for Bill', int(
                bi['bill_incong_number']), 'Congress', bi['congress'])
        except:
            try:
                subframe = create_data_actions(link, e)
                subframe['congress'] = bi['congress']
                subframe['bill_number'] = bi['bill_number']
                bills_actions = bills_actions.append(subframe)
                print('Iteration', i, 'for Bill', int(
                    bi['bill_incong_number']), 'Congress', bi['congress'])
            except:
                print('Bill '+str(bi['bill_number'])+' not found')
    if (i % 5000 == 0) and (i != 0):
        bills_actions.to_csv(
            path+'/scraped/bills_actions_byn/bills_actions_'+str(i)+'.csv', index=False)

bills_actions.to_csv(
    path+'/scraped/bills_actions_byn/bills_actions_161867.csv', index=False)
