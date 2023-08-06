"""a simple API to transcribe some Finno-Ugric, Turkic and the Russian language"""

import requests
from bs4 import BeautifulSoup

lang_dict = {
    "Mari (Hill Mari)": "mhr", "Udmurt": "udm", "Komi": "kom",
    "Erzya": "myv", "Moksha": "mdf", "Mansi": "mns", "Tatar": "tat",
    "Bashkir": "bak", "Chuvash": "chv", "Russian": "rus"
}

orth = {"Cyrillic": "c", "Latin": "l", "IPA": "i", "ISO9":"9", "<1917": "3"}

orth_dict = {f"{osrc} to {otgt}" : f"{orth[osrc]}{orth[otgt]}"
             for osrc in orth for otgt in list(orth)[:-1]
             if orth[osrc]+orth[otgt] not in ["ii", "99"]}

def transcribe(text, language='udm', which_orth='li'):
    """
    This is an api for https://copius.eu/trtr.php (© 2021 COPIUS)

    :param text: The text you want to transcribe
    :type text: str

    :param language: Abbreviation of the language you want to transcribe from.
                     Call lang_dict for a comprehensive list of abbreviations
    :type language: str

    :param which_orth: Abbreviation of source and target orthography.
                       Call orth_dict for a comprehensive list of abbreviations
    :tpye which_orth: str

    """


    r = requests.post(
            f'https://copius.eu/trtr.php?lang={language}',
            data={'inField':text, 'dir': which_orth}
            )
    soup = BeautifulSoup(r.text, 'html.parser')
    for t in soup.find_all("td"):
        res = t.find("div", class_="trans")
        if res:
            return res.text
