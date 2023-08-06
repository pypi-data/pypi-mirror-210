from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_euribor_row_values(table_row):
    row_date = table_row.find_all('th')[0].text
    # 12 months' euribor rates are the last values in this row.
    row_value = float(table_row.find_all('td')[-1].text.strip(' %'))/100
    return row_date, row_value


def get_euribor_rates(year: int):
    web_url = f'https://www.euribor-rates.eu/en/euribor-rates-by-year/{year}/'
    whole_page = requests.get(web_url)
    soup = BeautifulSoup(whole_page.content, "html.parser")
    eu_table = soup.find_all("table", class_="table table-striped")
    table_values = eu_table[0].find_all('tr')
    # Skipping first row
    results = {'date': list(), 'euribor': list()}
    for val_row in table_values[1:]:
        loc_date, loc_euribor = get_euribor_row_values(val_row)
        results['date'].append(loc_date)
        results['euribor'].append(loc_euribor)
    results = pd.DataFrame(results)
    results['date'] = pd.to_datetime(results['date'], format='%m/%d/%Y')
    results.date = results.date.dt.strftime('%Y-%m-%d')
    return results


def generate_euribor_csv(db_engine):
    euribor_values = list()
    for year_ in range(2018, 2024):
        euribor_values.append(get_euribor_rates(year=year_))
    euribor_df = pd.concat(euribor_values)
    euribor_df.to_sql('price_euribor', db_engine, if_exists='replace', index=False)


if __name__ == '__main__':
    generate_euribor_csv()
