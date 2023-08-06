import requests
import os
import pandas as pd
from cachetools.func import ttl_cache

token_url = "https://api.industrialinfo.com/idb/v1.4/token"
offline_events_summary_url = 'https://api.industrialinfo.com/idb/v1.4/offlineevents/summary'

proxies = {'http': 'proxy-rwest-uk.energy.local:8080', 'https': 'proxy-rwest-uk.energy.local:8080'}

def extract_credential(key: str):
    credentials = os.getenv("IIR_API_CREDENTIALS")
    tokens = credentials.split(";")
    token = [x for x in tokens if x.startswith(key)]
    if len(token) > 0:
        s = token[0].split("=")
        return s[1]


def get_access_token():
    """
    Given an api_dataset (eg OIL INVENTORY), get an access token from the Auth API
    :param api_dataset:
    :return:
    """
    params = {
        "username": extract_credential("username"),
        "password": extract_credential("password"),
        "tokeenLifeTime": 30,
    }


    token_request = requests.post(token_url, params=params, proxies=proxies)
    req_dic = token_request.headers
    access_token = req_dic["AUTHORIZATION"]
    return access_token


def build_header():
    header = {
        "Content-Type": "application/json",
        "Authorization": get_access_token(),
    }
    return header


@ttl_cache(ttl=10 * 60)
def summary_call(startdate: str = None, enddate: str = None, tradingRegion: str = None,
                 unitType: str = None, unitTypeGroup: str = None, country: str = None):
    fin = pd.DataFrame()
    offset = 0
    while True:
        params = {
            "eventStartDateMin": startdate,
            "limit": 1000,
            'offset': offset,
            'eventEndDateMax': enddate,
            "unitTypeDesc": unitType,
            "unitTypeGroup": unitTypeGroup,
            "physicalAddressCountryName": country,
        }
        headers = build_header()
        response = requests.post(url=offline_events_summary_url, headers=headers, params=params, proxies=proxies)
        summary = response.json()
        if summary['resultCount'] == 0:
            break
        res = pd.DataFrame(summary['offlineEvents'])
        if tradingRegion != None:
            res = res.loc[res['tradingRegionName'] == tradingRegion]
        cols = ['eventStartDate', 'eventEndDate', 'liveDate', 'releaseDate']
        res[cols] = res[cols].apply(lambda x: x.str[:-15])
        res[cols] = res[cols].apply(pd.to_datetime)
        res = pd.concat([res, res["offlineCapacity"].apply(pd.Series)], axis=1)
        res.drop(columns="offlineCapacity", inplace=True)
        offset = offset + 1000
        res = res.drop(res[res.eventStatusDesc == 'Cancelled'].index)
        fin = pd.concat([fin, res], ignore_index=True, axis=0)
    return fin


def details_call(eventId: str):
    params = {
        "eventId": eventId,
    }
    headers = build_header()
    response = requests.post(url=offline_events_summary_url, headers=headers, params=params, proxies=proxies)
    summary = response.json()
    summary = pd.DataFrame(summary['offlineEvents'])
    return summary

def tar_to_timeseries(taramount, startdate, enddate, tarname=None):
    dr = pd.date_range("01/01/2000", "12/01/2030")
    ser = pd.Series(0, index=dr)
    ser[startdate:enddate] = taramount
    ser.name = tarname
    return ser

def create_offline_dataset(startdate: str, enddate: str, tradingRegion: str, unitType: str, country: str):
    df = pd.DataFrame()
    fin = summary_call(startdate, enddate, tradingRegion, unitType, country)
    for index, row in fin.iterrows():
        row = tar_to_timeseries(row['capacityOffline'], row['eventStartDate'], row['eventEndDate'])
        df = pd.concat([df, row], axis=1)
    df = (df.sum(axis=1)) / 1000
    df = df.rename('capacityOffline')
    df = df.to_frame()
    return df