import json
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import incentivedkutils as utils
import requests
import xmltodict
from dateutil import parser


@utils.timer()
def main():
    start_date = datetime(2023, 5, 20)
    end_date = datetime(2023, 5, 31)
    areas = ['DE', 'DK1']
    entsoe_token = '95019cf4-6474-4df8-86b3-225459b315ca'
    indata = Entsoe.dayahead_prices_df(entsoe_token, areas, start_date, end_date)
    utils.prt(indata.head(10))
    utils.prt(indata.tail(10))
    area = 'DK'
    indata = Entsoe.actual_production_df(entsoe_token, area, start_date, end_date)
    utils.prt(indata.head(10))
    utils.prt(indata.tail(10))


class Entsoe:
    def dayahead_prices(token, areas, start_date, end_date):
        return dayahead_prices.dayahead_prices(token, areas, start_date, end_date)

    def dayahead_prices_df(token, areas, start_date, end_date):
        return dayahead_prices.dayahead_prices_df(token, areas, start_date, end_date)

    def actual_production(token, area, start_date, end_date):
        return actual_production.actual_production(token, area, start_date, end_date)

    def actual_production_df(token, area, start_date, end_date):
        return actual_production.actual_production_df(token, area, start_date, end_date)


class dayahead_prices:
    _error_list = []
    _chunksize = 20
    _batchsize = 369
    _max_workers = 24

    @classmethod
    def dayahead_prices(cls, token, areas, start_date, end_date=datetime(2030, 12, 31)):
        cls._token = token
        cls._areas = areas
        cls._start_date = start_date
        cls._end_date = end_date
        in_list = cls._get_dayahead_prices()
        return in_list

    @classmethod
    def dayahead_prices_df(cls, token, areas, start_date, end_date):
        import pandas as pd
        indata_list = cls.dayahead_prices(token, areas, start_date, end_date)
        df = pd.DataFrame(indata_list)
        df = df.pivot_table(index='ts', columns='area', values='price')
        df = df.ffill()
        return df

    @classmethod
    def _get_dayahead_prices(cls):
        tasks = []
        parms_list = cls._read_parms_A44()
        for area in cls._areas:
            segments = [obs for obs in parms_list if obs['area'] == area][0]['codes']
            for segment in segments:
                code_start_date = max(min(cls._start_date, segment['to_date']), segment['from_date'])
                code_end_date = min(min(cls._end_date, segment['to_date']), segment['to_date'])
                zone = segment['Code']
                if code_end_date - code_start_date:
                    tasks += cls._dayahead_prices_tasks(area, zone, code_start_date, code_end_date)
        indata = cls._dayahead_prices_executor(tasks)
        return indata

    @classmethod
    def _dayahead_prices_tasks(cls, area, zone, start_date, end_date):
        document_type = 'A44'
        base_url = f'https://web-api.tp.entsoe.eu/api?securityToken={cls._token}&'
        chunk_size = cls._chunksize
        start_date = start_date - timedelta(days=1)
        if end_date > datetime.today() + timedelta(days=2):
            end_date = datetime.today() + timedelta(days=2)
        tasks = []
        for datestep in range((end_date - start_date).days // chunk_size + 1):
            date_start = start_date + timedelta(days=chunk_size * datestep)
            date_end = min(date_start + timedelta(days=chunk_size), end_date)
            doc_url = f'documentType={document_type}&in_Domain={zone}&out_Domain={zone}' \
                      f'&periodStart={date_start.strftime("%Y%m%d2300")}&periodEnd={date_end.strftime("%Y%m%d2300")}'
            url = f'{base_url}{doc_url}'
            tasks.append((url, area))
        return tasks

    @classmethod
    def _dayahead_prices_executor(cls, tasks):
        indata_list = []
        batch_size = 60
        batch_duration = 10
        batches = len(tasks) // batch_size
        for batch in range(batches + 1):
            st = datetime.utcnow().timestamp()
            with ThreadPoolExecutor(max_workers=cls._max_workers) as executor:
                batch_list = list(
                    executor.map(cls._get_xml, tasks[batch * batch_size:(batch + 1) * batch_size]))
                indata_list += [cls._read_xml(indata[0], indata[1]) for indata in batch_list]
            duration = datetime.utcnow().timestamp() - st
            if duration < batch_duration and batch < batches:
                print(
                    f'\nwaiting for {batch_duration - duration} after batch {batch} of {batches} with batch_duration={batch_duration}')
                time.sleep(batch_duration - duration)
        indata_list = utils.flatten_list(indata_list)
        return indata_list

    @classmethod
    def _read_xml(cls, indata_xml, area):
        indata_json = json.dumps(xmltodict.parse(indata_xml))
        indata_dict = json.loads(indata_json)
        out_list = []
        if 'Publication_MarketDocument' in indata_dict.keys():
            timeseries = indata_dict['Publication_MarketDocument']['TimeSeries']
            timeseries = [ts for ts in timeseries if ts['Period']['resolution'] == 'PT60M']
            if type(timeseries) != list:
                timeseries = [timeseries]
            for obs in timeseries:
                ts_start = parser.parse(obs['Period']['timeInterval']['start'])
                time_resolution = int(obs['Period']['resolution'][-3:-1])
                data_points = obs['Period']['Point']
                if type(data_points) != list:
                    data_points = [data_points]
                for data_point in data_points:
                    obs_dict = {}
                    obs_dict['area'] = area
                    obs_dict['ts'] = ts_start + timedelta(minutes=(int(data_point['position']) - 1) * time_resolution)
                    obs_dict['price'] = float(data_point['price.amount'])
                    out_list.append(obs_dict)
        return out_list

    @classmethod
    def _get_xml(cls, task):
        # print(task[0])
        try:
            r = requests.get(task[0])
            r.encoding = r.apparent_encoding
            indata_xml = r.text
        except:
            dayahead_prices._error_list.append(task)
            indata_xml = ''
        return indata_xml, task[1]

    @classmethod
    def _read_parms_A44(cls):
        parms_list = [
            {'codes': [{'Code': '10YAT-APG------L', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'AT', 'area_long': 'Austria'},
            {'codes': [{'Code': '10YBE----------2', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'BE', 'area_long': 'Belgium'},
            {'codes': [{'Code': '10YCH-SWISSGRIDZ', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'CH', 'area_long': 'Switzerland'},
            {'codes': [{'Code': '10YDK-1--------W', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31)}], 'area': 'DK1', 'area_long': 'Denmark West'},
            {'codes': [{'Code': '10YDK-2--------M', 'from_date': datetime(1000, 1, 1),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'DK2', 'area_long': 'Denmark East'},
            {'codes': [{'Code': '10YES-REE------0', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'ES', 'area_long': 'Spain'},
            {'codes': [{'Code': '10YFI-1--------U', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'FI', 'area_long': 'Finland'},
            {'codes': [{'Code': '10YFR-RTE------C', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'FR', 'area_long': 'France'},
            {'codes': [{'Code': '10YGR-HTSO-----Y', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'GR', 'area_long': 'Greece'},
            {'codes': [{'Code': '10YHU-MAVIR----U', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'HU', 'area_long': 'Hungary'},
            {'codes': [{'Code': '10Y1001A1001A59C', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'IE', 'area_long': 'Ireland'},
            {'codes': [{'Code': '10Y1001A1001A70O', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'IT_N', 'area_long': 'Italy North'},
            {'codes': [{'Code': '10Y1001A1001A71M', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'IT_S', 'area_long': 'Italy South'},
            {'codes': [{'Code': '10YLT-1001A0008Q', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'LT', 'area_long': 'Lithuania'},
            {'codes': [{'Code': '10YLV-1001A00074', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'LV', 'area_long': 'Latvia'},
            {'codes': [{'Code': '10YNL----------L', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'NL', 'area_long': 'Netherlands'},
            {'codes': [{'Code': '10YNO-1--------2', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'NO1', 'area_long': 'Norway 1'},
            {'codes': [{'Code': '10YNO-2--------T', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'NO2', 'area_long': 'Norway 2'},
            {'codes': [{'Code': '10YNO-3--------J', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'NO3', 'area_long': 'Norway 3'},
            {'codes': [{'Code': '10YNO-4--------9', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'NO4', 'area_long': 'Norway 4'},
            {'codes': [{'Code': '10Y1001A1001A48H', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'NO5', 'area_long': 'Norway 5'},
            {'codes': [{'Code': '10YPL-AREA-----S', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'PL', 'area_long': 'Poland'},
            {'codes': [{'Code': '10YPT-REN------W', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'PT', 'area_long': 'Portugal'},
            {'codes': [{'Code': '10Y1001A1001A44P', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'SE1', 'area_long': 'Sweden 1'},
            {'codes': [{'Code': '10Y1001A1001A45N', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'SE2', 'area_long': 'Sweden 2'},
            {'codes': [{'Code': '10Y1001A1001A46L', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'SE3', 'area_long': 'Sweden 3'},
            {'codes': [{'Code': '10Y1001A1001A47J', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'SE4', 'area_long': 'Sweden 4'},
            {'codes': [{'Code': '10YGB----------A', 'from_date': datetime(1000, 1, 1, 0, 0),
                        'to_date': datetime(2099, 12, 31, 0, 0)}], 'area': 'UK', 'area_long': 'UK'},
            {'codes': [
                {"Code": "10Y1001A1001A63L", "from_date": datetime(1000, 1, 1), "to_date": datetime(2018, 9, 30)},
                {"Code": "10Y1001A1001A82H", "from_date": datetime(2018, 10, 1), "to_date": datetime(2099, 12, 31)}],
                'area': 'DE', 'area_long': 'Germany'},
        ]
        return parms_list


class actual_production:
    _error_list = []
    _chunksize = 20
    _batchsize = 369
    _max_workers = 24

    @classmethod
    def actual_production(cls, token, area, start_date, end_date=datetime(2030, 12, 31)):
        cls._token = token
        cls._area = area
        cls._start_date = start_date
        cls._end_date = end_date

        in_list = cls._get_actual_production()
        if dayahead_prices._error_list:
            print(dayahead_prices._error_list)
        return in_list

    @classmethod
    def actual_production_df(cls, token, area, start_date, end_date=datetime(2030, 12, 31)):
        import pandas as pd
        indata_list = cls.actual_production(token, area, start_date, end_date)
        df = pd.DataFrame(indata_list)
        df = df.pivot_table(index='ts', columns='asset_name', values='volume')
        df = df.ffill()
        return df

    @classmethod
    def _get_actual_production(cls):
        parms_list = cls._read_parms_A73()
        zone = [obs['Code'] for obs in parms_list if obs['area'] == cls._area][0]
        document_type = 'A73'
        base_url = f'https://web-api.tp.entsoe.eu/api?securityToken={cls._token}&'
        # start_date = cls._start_date  # - timedelta(days=1)
        if cls._end_date > datetime.today() + timedelta(days=2):
            cls._end_date = datetime.today() + timedelta(days=2)
        tasks = []
        for datestep in range((cls._end_date - cls._start_date).days + 1):
            step_start = cls._start_date + timedelta(days=datestep)
            step_end = min(step_start + timedelta(days=1), cls._end_date)
            doc_url = f'documentType={document_type}&processType=A16&in_Domain={zone}&periodStart={step_start.strftime("%Y%m%d0000")}&periodEnd={step_end.strftime("%Y%m%d0000")}'
            url = f'{base_url}{doc_url}'
            tasks.append((url, cls._area))
        indata_list = []
        batch_size = 60
        batch_duration = 10
        batches = len(tasks) // batch_size
        for batch in range(batches + 1):
            st = datetime.utcnow().timestamp()
            with ThreadPoolExecutor(max_workers=cls._max_workers) as executor:
                batch_list = list(executor.map(cls._get_xml, tasks[batch * batch_size:(batch + 1) * batch_size]))
                indata_list += [cls._read_xml(indata[0], indata[1]) for indata in batch_list]
            duration = datetime.utcnow().timestamp() - st
            if duration < batch_duration and batch < batches:
                print(
                    f'waiting for {batch_duration - duration} after batch {batch} of {batches} with batch_duration={batch_duration}')
                time.sleep(batch_duration - duration)
        indata_list = utils.flatten_list(indata_list)
        return indata_list

    @classmethod
    def _read_xml(cls, indata_xml, area):
        try:
            indata_json = json.dumps(xmltodict.parse(indata_xml))
            indata_dict = json.loads(indata_json)
        except:
            indata_dict = {}
        out_list = []
        if 'GL_MarketDocument' in indata_dict.keys():
            timeseries = indata_dict['GL_MarketDocument']['TimeSeries']
            if type(timeseries) != list:
                timeseries = [timeseries]
            for obs in timeseries:
                ts_start = parser.parse(obs['Period']['timeInterval']['start'])
                time_resolution = int(obs['Period']['resolution'][-3:-1])
                data_points = obs['Period']['Point']
                if type(data_points) != list:
                    data_points = [data_points]
                for data_point in data_points:
                    obs_dict = {}
                    obs_dict['asset_name'] = obs['MktPSRType']['PowerSystemResources']['name']
                    obs_dict['area'] = area

                    obs_dict['ts'] = ts_start + timedelta(minutes=(int(data_point['position']) - 1) * time_resolution)
                    obs_dict['volume'] = float(data_point['quantity'])
                    out_list.append(obs_dict)
        return out_list

    @classmethod
    def _read_parms_A73(cls):
        parms_list = [
            {"Code": "10Y1001A1001A796", "Meaning": "DK1 BZ / MBA", "area": "DK", "area_long": "Denmark"},
            {"Code": "10YDE-VE-------2", "Meaning": "DE Vattenfall area", "area": "DE_VE",
             "area_long": "Germany Vattenfall"},
            {"Code": "10YDE-EON------1", "Meaning": "DE Eon area", "area": "DE_EON", "area_long": "Germany Eon"},
            {"Code": "10YDE-RWENET---I", "Meaning": "DE RWE area", "area": "DE_RWE", "area_long": "Germany RWE"},
            {"Code": "10YDE-ENBW-----N", "Meaning": "DE ENBW area ", "area": "DE_ENBW", "area_long": "Germany ENBW"},
            {"Code": "10YSE-1--------K", "Meaning": "Sweden", "area": "SE", "area_long": "Sweden"},
        ]
        return parms_list

    @classmethod
    def _get_xml(cls, task):
        # print(task[0])
        try:
            r = requests.get(task[0])
            r.encoding = r.apparent_encoding
            indata_xml = r.text
        except:
            dayahead_prices._error_list.append(task)
            indata_xml = ''
        return indata_xml, task[1]


if __name__ == '__main__':
    main()
