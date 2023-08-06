"""
fill in
"""

import abc
from dataclasses import dataclass


class restConfig(abc.ABC):
    """
    fill in

    """
    name = ""
    url = ""


@dataclass
class MachineRestConfiguration(restConfig):
    """
    fill in
    """
    name = "bronze_maine_raw"
    url = "https://my.api.mockaroo.com/machine.json"


class SalesRestConfiguration(restConfig):
    """
    fill in
    """
    name = "bronze_sales"
    url = "https://my.api.mockaroo.com/sales.json"


class BronzeSapBsegRestConfiguration(restConfig):
    """
    fill in
    """
    name = "bronze_sap_bseg"
    url = "https://my.api.mockaroo.com/sap_bseg.json"


Apis = [
    MachineRestConfiguration,
    BronzeSapBsegRestConfiguration,
    SalesRestConfiguration,
]
