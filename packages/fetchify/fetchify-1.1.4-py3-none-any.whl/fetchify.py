"""This a library that mean't to access files from github repo without opening it again and again"""

import requests
url = {
    "py" : "https://raw.githubusercontent.com/Anupam1707/Python_Programmes/main/"
    "we" : "https://raw.githubusercontent.com/Anupam1707/weather-app-py/main/",
    "aiu" : "https://raw.githubusercontent.com/Anupam1707/ai/main/",
    "ds" : "https://raw.githubusercontent.com/Anupam1707/datasense/main/",
    "spy" : "https://raw.githubusercontent.com/Anupam1707/SecuriPy/main/"
}

def fetch(filename, code, image = False):
    page = requests.get(url[code] + filename)
    if image == False:
        return page.text
    else :
        return page.content

def save(file, name):
    with open(f"{name}", "w", encoding = "utf-8", newline = "") as f:
        f.writelines(file)
