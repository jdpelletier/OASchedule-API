import pandas as pd
from datetime import timezone, datetime, timedelta
import json

def writeToJson(f):

    df = pd.read_excel(f)

    df.dropna(subset=["Date"], inplace=True)
    df = df[df.filter(regex='^(?!Unnamed)').columns]

    df = df[~(df['Date'] == 'Date')]

    df = df[~(df['Date'] == 'K1')]
    df = df[~(df['Date'] == 'R1')]
    df = df[~(df['Date'] == 'K1O')]
    df = df[~(df['Date'] == 'K1T')]
    df = df[~(df['Date'] == 'R2')]
    df = df[~(df['Date'] == 'K2')]
    df = df[~(df['Date'] == 'K2O')]
    df = df[~(df['Date'] == 'K2T')]
    df = df[~(df['Date'] == 'HQ')]
    df = df[~(df['Date'] == 'PD')]
    df = df[~(df['Date'] == 'SD')]
    df = df[~(df['Date'] == 'JD')]
    df = df[~(df['Date'] == 'OM')]
    df = df[~(df['Date'] == 'X')]
    df = df[~(df['Date'] == 'L')]
    df = df[~(df['Date'] == 'H')]

    df['Date'] = df['Date'].dt.tz_localize(timezone(timedelta(hours=-10))) #convert to HST

    df.rename(columns={'Institution':'Institution:K1'}, inplace=True)
    df.rename(columns={'Institution.1':'Institution:K2'}, inplace=True)

    for col in df:
        if '.' in col:
            df = df.drop(col, 1)

    search = False
    for col in df:
        if col == 'K2 Instrument':
            search = False
        if col != col.isupper() == False and search == True:
            df = df.drop(col, 1)
        if col == 'K1 Instrument':
            search = True

    df = df.to_json(orient='records')
    parsed = json.loads(df)

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(parsed, f, ensure_ascii=False, indent=4)

    return 200

def readFromJson(f):

    with open(f) as json_file:
        data = json.load(json_file)

    return json.dumps(data)

def exportPersonalSchedule(f, employee):
    df = pd.read_json('data.json')
    for col in df:
        if col != employee and col != 'Date':
            df = df.drop(columns=col)
    df['just_date'] = df['Date'].dt.date
    df.rename(columns={'just_date':'Start Date', employee:'Subject'}, inplace=True)
    df = df.drop(columns='Date')



    work_days = ['K1', 'R1', 'K1O', 'R1O', 'K1T', 'R1T', 'R2', 'K2', 'R2O', 'K2O', 'R2T', 'K2T', 'HQ', 'PD', 'SD', 'OM']
    location = []
    for ind in df.index:
        current = df['Subject'][ind]
        if current not in work_days:
            df.drop(ind, inplace=True)
        elif current.startswith('K') or current == 'SD':
            location.append('Summit')
        elif current.startswith('R') or current == 'HQ':
            location.append('Headquarters')
        else:
            location.append('No location')

    df['Location'] = location

    subject = df.pop('Subject')
    df.insert(0, 'Subject', subject)
    df.to_csv(f'{employee}.csv', index=False)
    return f'{employee}.csv'
