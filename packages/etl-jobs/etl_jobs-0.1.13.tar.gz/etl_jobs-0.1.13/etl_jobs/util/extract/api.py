"""
fill in
"""

import pandas as pd
import polars as pl
import requests


def get_api_data(url: str, key: str):
    """
    fill in
    :param url:
    :param key:
    :return:
    """
    headers = {"x-api-key": key}
    response = requests.get(url, headers=headers)
    json = response.json()
    return pl.from_pandas(pd.DataFrame(json))
