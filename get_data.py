import pandas as pd
import requests, zipfile, io

gh_latest_release = 'https://api.github.com/repos/f1db/f1db/releases/latest'

folder = 'f1db-csv'
last_version_file = "f1db_last_version_file.txt"

# Download and extract from {url} to {folder}
def download(url, last_version):
    print(f"f1-data > Downloading\t\t\t({last_version})")
    r = requests.get(url)
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    zf.extractall(folder)
    with open(last_version_file, 'w') as file:
        file.write(last_version)
        print(f"f1-data > Successfully Downloaded\t({last_version})")

# Get Data only if a new version is available                
def get_data():
    response = requests.get(gh_latest_release)
    last_version = response.json()["name"]
    print(f"f1-data > Fetching Version\t({last_version})")
    url = f'https://github.com/f1db/f1db/releases/download/{last_version}/f1db-csv.zip'

    try:
        with open(last_version_file, 'r') as file:
            content = file.read().strip()
        
        if content == last_version:
            print(f"f1-data > Already up to date\t({last_version})")
        else:
            download(url, last_version)

    except FileNotFoundError:
        download(url, last_version)