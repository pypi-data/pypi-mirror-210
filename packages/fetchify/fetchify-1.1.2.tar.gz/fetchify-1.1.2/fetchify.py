"""This a library that mean't to access files from github repo without opening it again and again"""

import requests

url1 = "https://raw.githubusercontent.com/Anupam1707/Python_Programmes/main/"
url2 = "https://raw.githubusercontent.com/Anupam1707/weather-app-py/main/"
url3 = "https://raw.githubusercontent.com/Anupam1707/ai/main/"
url4 = "https://raw.githubusercontent.com/Anupam1707/datasense/main/"
url5 = "https://raw.githubusercontent.com/Anupam1707/SecuriPy/main/"

def python(filename):
    """To access files from the Repository 'Python'"""
    page = requests.get(url1 + filename)
    return page.text

def weather(filename):
    """To access files from the Repository 'weather'"""
    page = requests.get(url2 + filename)
    return page.text

def ai(filename):
    """To access files from the Repository 'ai'"""
    page = requests.get(url3 + filename)
    return page.text

def sense(filename):
    """To access files from the Repository 'food'"""
    page = requests.get(url4 + filename)
    return page.text

def secure(filename):
    """To access files from the Repository 'SecuriPy'"""
    page = request.get(url + filename)
    return page.text

def save(file, name):
    with open(f"{name}", "w", encoding = "utf-8", newline = "") as f:
        f.writelines(file)