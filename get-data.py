import pandas as pd
import requests, zipfile, io

url = 'https://github.com/f1db/f1db/releases/download/v2024.6.0/f1db-csv.zip'
folder = 'f1db-csv/'
filename = 'f1db-races.csv'

r = requests.get(url)
zf = zipfile.ZipFile(io.BytesIO(r.content))
zf.extractall("f1db-csv")

df = pd.read_csv(folder + filename, sep=',')

print(df.head(1))