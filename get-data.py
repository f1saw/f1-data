import pandas as pd
import requests, zipfile, io


gh_latest_release = 'https://api.github.com/repos/f1db/f1db/releases/latest'
response = requests.get(gh_latest_release)
print(response.json()["name"])

url = f'https://github.com/f1db/f1db/releases/download/{response.json()['name']}/f1db-csv.zip'
folder = 'f1db-csv/'
filename = 'f1db-races.csv'

r = requests.get(url)
zf = zipfile.ZipFile(io.BytesIO(r.content))
zf.extractall("f1db-csv")

df = pd.read_csv(folder + filename, sep=',')

print(df.head(1))