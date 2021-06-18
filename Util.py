import pandas as pd
import json

def writeToJson(f):

    df = pd.read_excel(f)

    df.dropna(subset=["Date"], inplace=True)
    df = df[df.filter(regex='^(?!Unnamed)').columns]

    df = df[~(df['Date'] == 'Date')]

    # df = df[~(df['Date'] == ('K1' | 'R1' | 'K1O' | 'K1T' | 'K2' | 'R2' | 'K2O' | 'K2T' | 'HQ' | 'PD' | 'SD' | 'JD' | 'OM' | 'X' | 'L' | 'H'))]

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

    # df.to_excel("filteredsched.xlsx")
    df = df.to_json(orient='records')
    parsed = json.loads(df)

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(parsed, f, ensure_ascii=False, indent=4)

    return 200

def readFromJson(f):

    with open(f) as json_file:
        data = json.load(json_file)

    return json.dumps(data)
