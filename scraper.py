import requests
from bs4 import BeautifulSoup
from bidi.algorithm import get_display
from itertools import filterfalse

URL = 'https://votes25.bechirot.gov.il/'
DEFAULT_URL = 'https://votes25.bechirot.gov.il/'
CITY_URL = 'https://votes25.bechirot.gov.il/cityresults'
BALLOT_URL = 'https://votes25.bechirot.gov.il/ballotresults'

def get_page():
    response = requests.get(URL)
    assert response.status_code == 200, 'Wrong status code'
    data = response.text
    soup = BeautifulSoup(data, 'html.parser')
    table2 = soup.find('table', class_='ResultsSummaryTable')
    cells2 = table2.find_all("td")
    votes_counted = int(cells2[3].text.replace(',', ''))
    table = soup.find('table', class_='TableData')
    return table, votes_counted

def get_parties(table):
    parties = dict()
    for row in table.tbody.find_all('tr'):
        party_name = row.find('th').text.strip()
        votes = int(row.find('div', {"class":'FloatDir'}).text.strip().replace(',',''))
        parties[party_name] = votes
    return parties

def get_cities_list():
    response = requests.get(CITY_URL)
    assert response.status_code == 200, 'Wrong status code'
    data = response.text
    soup = BeautifulSoup(data, 'html.parser')
    cities_list = soup.findAll('option')
    cities = {x.text: x['value'] for x in cities_list}
    return cities

def get_kalpi_list(cities):
    combo = dict()
    for city, value in cities.items():
        response = requests.get(BALLOT_URL+f"?cityID={value}")
        assert response.status_code == 200, 'Wrong status code'
        data = response.text
        soup = BeautifulSoup(data, 'html.parser')
        kalpis = soup.findAll('option')
        for kalpi in list(kalpis):
            if kalpi.text != "- בחר קלפי -":
                kalpis.remove(kalpi)
            else:
                kalpis.remove(kalpi)
                break
        kalpis = {x.text: x['value'] for x in kalpis}
        combo[city] = kalpis
    return combo