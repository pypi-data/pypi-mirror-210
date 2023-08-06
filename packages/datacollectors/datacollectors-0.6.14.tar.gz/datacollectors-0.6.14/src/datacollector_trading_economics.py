import re
from datetime import datetime, timedelta

import incentivedkutils as utils
import requests


def main():
    start_date = datetime(2019, 1, 1)
    for commodity in ['ttf_gas', 'urea_ammonium', 'EUA', 'brent_oil'][-1:]:
        indata_list = Trading_economics.commodity_prices_df(commodity, start_date)
        utils.prt(indata_list[:10])


class Trading_economics():
    @staticmethod
    def commodity_prices_df(commodity, start_date):
        import pandas as pd
        indata_list = Trading_economics.commodity_prices(commodity, start_date)
        df = pd.DataFrame(indata_list)
        df = df.set_index('date')
        df = df.resample('D').ffill()
        return df

    @staticmethod
    def commodity_prices(commodity, start_date):
        indata_list = []
        commodity_list = Trading_economics._read_commodity_list()
        period_length = int((datetime.today() - start_date) / timedelta(days=1)) + 1
        if commodity in [d['commodity'] for d in commodity_list]:
            links_dict = [d for d in commodity_list if d['commodity'] == commodity][0]
            url_site = links_dict['url_site']
            auth = Trading_economics._get_auth(url_site)
            url = f"{links_dict['url_data']}&span={period_length}d&AUTH={auth}"
            indata = requests.get(url).json()
            indata_list = [
                {'date': datetime.fromtimestamp(int(obs['x'] / 1000)) - timedelta(hours=1), commodity: obs['y']} for obs
                in indata['series'][0]['data']]
        return indata_list

    @classmethod
    def _get_auth(cls, url_site):
        headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0"}
        with requests.Session() as s:
            in_string = s.get(url_site, headers=headers).text
        pattern = re.compile('TESecurify = (.*)')
        match = pattern.findall(in_string)[-1:]
        auth = str(match[0][1:-3])
        return auth

    @classmethod
    def _read_commodity_list(cls):
        commodity_list = [
            {'commodity': 'ttf_gas', 'url_site': 'https://tradingeconomics.com/commodity/eu-natural-gas',
             'url_data': 'https://markets.tradingeconomics.com/chart?interval=1d&securify=new&url=/commodity/eu-natural-gas&s=ngeu:com'},
            {'commodity': 'urea_ammonium', 'url_site': 'https://tradingeconomics.com/commodity/urea-ammonium',
             'url_data': 'https://markets.tradingeconomics.com/chart?interval=1d&securify=new&url=/commodity/urea-ammonium&s=uaneu:com'},
            {'commodity': 'brent_oil', 'url_site': 'https://tradingeconomics.com/commodity/brent-crude-oil',
             'url_data': 'https://markets.tradingeconomics.com/chart?interval=1d&securify=new&url=/commodity/brent-crude-oil&s=co1:com'},
            {'commodity': 'EUA', 'url_site': 'https://tradingeconomics.com/commodity/carbon',
             'url_data': 'https://markets.tradingeconomics.com/chart?interval=1d&securify=new&url=/commodity/carbon&s=eecxm:ind'},
        ]
        return commodity_list


if __name__ == "__main__":
    main()
