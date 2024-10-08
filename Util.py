import pandas as pd
from datetime import timezone, datetime, timedelta, date
import json
import requests
from dateutil.relativedelta import relativedelta
from calendar import Calendar
import time

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

    df['Date'] = pd.to_datetime(df.Date, format='%Y-%m-%d')
    df['Date'] = df['Date'].dt.tz_localize(timezone(timedelta(hours=-10))) #convert to HST

    df.rename(columns={'Institution':'K1 Institution'}, inplace=True)
    df.rename(columns={'Institution.1':'K2 Institution'}, inplace=True)
    df.rename(columns={'K2 PI last':'K2 PI'}, inplace=True)

    holder = []
    for row in range(0, df.shape[0]):
        holder.append("")
    
    df['Holiday'] = holder

    hol = get_holidays(list(df['Date'].values[:1])[0], list(df['Date'].values[-1:])[0])
    hol_dates = [h+" 00:00:00-10:00" for h in hol]
    df.loc[df['Date'].isin(hol_dates), 'Holiday'] = 'X'

    for col in df:
        if '.' in col:
            df = df.drop(col, 1)

    search = False
    for col in df:
        if col == 'K2 Instrument':
            search = False
        if col != col.isupper() == False and col != 'Mtg' and search == True:
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

def compareJsons():

    with open('data.json') as json_file:
        data = json.load(json_file)

    

    range = {'Start': data[0]['Date'], 'End': data[-1]['Date'], 'Overlap': False}
    
    ns = json.loads(getNSFromTelSched(range))

    with open('config.live.json') as json_file:
            config = json.load(json_file)
    include = config[0]['night_shifts']
    i=0
    for night in data:
        tsnight = ns[i]
        for col in night:
            try:
                if night[col] in include and night[col] != tsnight[col] or tsnight[col] in include and night[col] != tsnight[col] :
                    night[col] += '!'
            except KeyError:
                pass
        i+=1

    return json.dumps(data)

def getNSFromTelSched(range):
    try:
        start = datetime.fromtimestamp(range['Start']/1000).strftime('%Y-%m-%d')
    except TypeError:
        start = range['Start'][:10]
    try:
        end = datetime.fromtimestamp(range['End']/1000).strftime('%Y-%m-%d') 
    except TypeError:
        end = range['End'][:10]

    holidays = get_holidays(start, end)
    
    nightstaff = []
    current_date = datetime.strptime(start, '%Y-%m-%d').date()
    last_date = datetime.strptime(end, '%Y-%m-%d').date()
    if range['Overlap'] == True:
        last_date = last_date - timedelta(days=1)
    while current_date <= last_date:
        with open('config.live.json') as json_file:
            config = json.load(json_file)
        response = requests.get(config[0]['nightstaff'] + f"&date={current_date}&type=oa", verify=False)
        data = response.json()
        nightstaff.append(data)
        current_date += timedelta(days=1)

    #TODO, get rid of nested loop
    oa_names = []
    for night in nightstaff:
        for oa in night:
            name = oa["FirstName"][0] + oa["LastName"][0]
            if name not in oa_names:
                oa_names.append(name)


    schedule = []
    current_date = datetime.strptime(start, '%Y-%m-%d').date()
    while current_date <= last_date:
        night = {}
        night["Date"] = datetime.fromtimestamp(time.mktime(current_date.timetuple())).timestamp()*1000
        night["DOW"] = current_date.strftime('%A')[:3]
        night["Holiday"] = ""
        if str(current_date.strftime('%Y-%m-%d')) in holidays:
            night["Holiday"] = "X"
        night["K1 PI"] = ""
        night["K1 Institution"] = ""
        night["K1 Instrument"] = ""
        for name in oa_names:
                night[name] = None

        people = 0
        for staff in nightstaff:
            try:
                s_date = datetime.strptime(staff[0]["Date"], '%Y-%m-%d').date()
                if s_date > current_date:
                    break
                if s_date == current_date:
                    for oa in staff:
                        name = oa["FirstName"][0] + oa["LastName"][0]
                        shift = oa["Type"].upper()
                        if "R" in shift:
                            tel = "R" + oa["TelNr"]
                            night[name] = shift.replace("OAR", tel)
                            people += 1
                        else:
                            tel = "K" + oa["TelNr"]
                            night[name] = shift.replace("OA", tel)
                            people += 1
                    if people == 0:
                        break
            except KeyError:
                break

        night["K2 PI"] = ""
        night["K2 Institution"] = ""
        night["K2 Instrument"] = ""
                
        schedule.append(night)
        current_date += timedelta(days=1)

    if fileCheck() == False:
        with open('data.json', 'w+', encoding='utf-8') as f:
            json.dump(schedule, f, ensure_ascii=False, indent=4)

    return(json.dumps(schedule))

def getObserversFromTelSchedule(schedule):
    
    data = schedule['Schedule']

    start = datetime.fromtimestamp(schedule['Start']/1000).strftime('%Y-%m-%d')
    end = datetime.fromtimestamp(schedule['End']/1000).strftime('%Y-%m-%d')
    set_date = datetime.strptime(start, '%Y-%m-%d').date()
    last_date = datetime.strptime(end, '%Y-%m-%d').date()
    delta_days = (last_date-set_date).days + 1
    if delta_days > 120:
        delta_days = 120
        last_date = last_date-timedelta(days=119)
    
    with open('config.live.json') as json_file:
        config = json.load(json_file)

    response = requests.get(config[0]['schedule'] + f"&date={set_date}&numdays={delta_days}", verify=False)
    observers = response.json()
    
    kOne = [x for x in observers if "1" in x["TelNr"]]
    kTwo = [x for x in observers if "2" in x["TelNr"]]

    for night in data:
        n_date = int(str(night["Date"])[:10])
        n_date = datetime.fromtimestamp(n_date).strftime('%Y-%m-%d')
        check_date = datetime.strptime(n_date, '%Y-%m-%d').date()
        if check_date == last_date:
            break
        night["K1 PI"] = ""
        night["K1 Institution"] = ""
        night["K1 Instrument"] = ""
        for observer in kOne:
            if n_date == observer["Date"]:
                if night["K1 PI"] == "":
                        night["K1 PI"] += observer["Principal"]
                        night["K1 Institution"] += observer["Institution"]
                        night["K1 Instrument"] += observer["Instrument"]
                else:
                    night["K1 PI"] += " / " + observer["Principal"]
                    night["K1 Institution"] += " / " + observer["Institution"]
                    night["K1 Instrument"] += " / " + observer["Instrument"]
        night["K2 PI"] = ""
        night["K2 Institution"] = ""
        night["K2 Instrument"] = ""
        for observer in kTwo:
            if n_date == observer["Date"]:
                if night["K2 PI"] == "":
                        night["K2 PI"] += observer["Principal"]
                        night["K2 Institution"] += observer["Institution"]
                        night["K2 Instrument"] += observer["Instrument"]
                else:
                    night["K2 PI"] += " / " + observer["Principal"]
                    night["K2 Institution"] += " / " + observer["Institution"]
                    night["K2 Instrument"] += " / " + observer["Instrument"]


    return(json.dumps(data))    

def exportPersonalSchedule(f, employee):
    df = pd.read_json('data.json')
    for col in df:
        if col != employee and col != 'Date':
            df = df.drop(columns=col)
    df['just_date'] = df['Date'].dt.date
    df.rename(columns={'just_date':'Start Date', employee:'Subject'}, inplace=True)
    df = df.drop(columns='Date')


    with open('config.live.json') as json_file:
            config = json.load(json_file)
    work_days = config[0]['all_shifts']
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


def get_holidays(startdate, enddate):

    with open('config.live.json') as json_file:
        config = json.load(json_file)
    
    response = requests.get(config[0]['holidays'] + f"?startdate={startdate}&enddate={enddate}", verify=False)

    return response.json()

def last_day(file):
    try:
        with open(file) as f:
            j = json.load(f)
            try:
                return json.dumps(j[-1]['Date'])
            except IndexError:
                return json.dumps(None)
    except FileNotFoundError:
            return json.dumps(None)

def fileCheck():
    try:
        file = open('data.json')
        file.close()
        return json.dumps({'File': True})
    except FileNotFoundError:
        return json.dumps({'File': False})

def isAdmin(data):
    username = data['Username']

    with open('config.live.json') as json_file:
        config = json.load(json_file)
    
    if username in config[0]['admins']:
        response = {'Admin': True}
    else:
        response = {'Admin': False}
    return json.dumps(response)
