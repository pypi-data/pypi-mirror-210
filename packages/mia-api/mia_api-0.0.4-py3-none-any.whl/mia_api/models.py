import requests
import json
import os
from typing import Union, List
from datetime import datetime

import xarray as xr
import netCDF4
import pandas as pd
from tqdm import tqdm
from tabulate import tabulate

from mia_api.config_file import APIPATH
from mia_api.utils import response_return

token = os.getenv("MIA_API_TOKEN")


class MIAJuice:
    """
    This creates a Juice, which must be stored in an available JuiceBar

    :param name: str The name of the Juice
    :param barname: str Name of JuiceBar in which the Juice is stored

    """
    def __init__(
            self,
            name: str,
            barname: str):
        self.name = name
        self.barname = barname

    def historical(
            self,
            dataset: bool = False):
        """
        Retrieve historical data from a Juice

        :param dataset: bool False for xr.DataArray, True for xr.Dataset

        :return: xr.DataArray or xr.Dataset

        """
        getjuicepath = f"{APIPATH}/bars/juices/get/?barname=" \
                       f"{self.barname}&juicename={self.name}" \
                       "&operational=false"
        headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + os.getenv("MIA_API_TOKEN")
        }
        response = requests.request("POST", getjuicepath, headers=headers)
        response_return(response)
        if dataset:
            ds = xr.open_dataset(
                xr.backends.NetCDF4DataStore(
                    netCDF4.Dataset(
                        'name',
                        mode='r',
                        memory=response.content
                    )
                )
            )
        else:
            ds = xr.open_dataarray(
                xr.backends.NetCDF4DataStore(
                    netCDF4.Dataset(
                        'name',
                        mode='r',
                        memory=response.content
                    )
                )
            )
        return ds

    def operational(
            self,
            rundate: Union[datetime, List[datetime], None] = None,
            dataset: bool = False):
        """
        Retrieve operational data from a Juice

        :param rundate: Union[datetime, List[datetime], None]
            1) Datetime: Process data for this datetime
            2) List[datetime]: Process data for all datetimes within List
            3) None: Process for all available datetime
        :param dataset: bool False for xr.DataArray, True for xr.Dataset

        :return: xr.DataArray or xr.Dataset

        """
        getjuicepath = f"{APIPATH}/bars/juices/get/?barname={self.barname}" \
                       f"&juicename={self.name}&operational=true"
        if rundate:
            if type(rundate) == list:
                data = json.dumps([d.isoformat() for d in rundate])
            else:
                data = json.dumps([rundate.isoformat()])
        else:
            data = {}
        headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + os.getenv("MIA_API_TOKEN")
        }
        response = requests.request(
            "POST",
            getjuicepath,
            headers=headers,
            data=data
        )
        response_return(response)
        if dataset:
            ds = xr.open_dataset(
                xr.backends.NetCDF4DataStore(
                    netCDF4.Dataset(
                        'name',
                        mode='r',
                        memory=response.content
                    )
                )
            )
        else:
            ds = xr.open_dataarray(
                xr.backends.NetCDF4DataStore(
                    netCDF4.Dataset(
                        'name',
                        mode='r',
                        memory=response.content
                    )
                )
            )
        return ds


class MIAJuiceBar:
    """
    This creates a JuiceBar, which stores the Juices produced in the
    MIA System. It is possible to check the available bars with the
    method available_bars. To know the Juices available and its features
    the method show_menu must be used.

    :param name: str The name of the JuiceBar

    """

    def __init__(
            self,
            name: str):
        self.name = name

    @staticmethod
    def available_bars():
        """
        Lists the available MIA JuiceBars

        :return: List[dict] with available JuiceBars

        """
        availablebarspath = f"{APIPATH}/users/me/bars"
        headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + os.getenv("MIA_API_TOKEN")
        }
        response = requests.request(
            "GET",
            availablebarspath,
            headers=headers
        )
        response_return(response)
        return response.json()

    def show_menu(
            self):
        """
        Show menu of Juices within JuiceBar, its features, such as
        names, available dates, timedelta, preprocessing are listed

        """
        menupath = f"{APIPATH}/bars/menu?barname={self.name}&html=false"
        headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + os.getenv("MIA_API_TOKEN")
        }
        response = requests.request("GET", menupath, headers=headers)
        response_return(response)
        menu = response.json()
        data = pd.concat(
            [pd.DataFrame.from_dict(m, orient="index") for m in menu]
        )
        print('#' * 40)
        print(tabulate(data, tablefmt="psql"))
        print(f'JuiceBar total juices/fruits: ' + str(data.shape[0]))
        print('#' * 40)

    def list_juices(
            self):
        """
        Show list of Juices names within JuiceBar

        :return: List[dict] with Juices names within a JuiceBar

        """
        listjuicepath = f"{APIPATH}/bars/juices/list/?barname={self.name}"
        headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + os.getenv("MIA_API_TOKEN")
        }
        response = requests.request("GET", listjuicepath, headers=headers)
        response_return(response)
        return response.json()

    def get_juice(
            self,
            juice_name: str):
        """
        Retrieve a Juice within this JuiceBar, its methods can be seen
        in class MIAJuice

        :param juice_name: str MIAJuice name

        :return: MIAJuice

        """
        return MIAJuice(name=juice_name, barname=self.name)

    def run_mia_model(
            self,
            jsonfile):
        """
        Run a mia model. A JSON config file with the model characteristics
        must be provided. And also a py file with historical and
        operational methods for this Juice

        :param jsonfile: File

        """
        runmodelpath = f"{APIPATH}/apps/?barname=f{self.name}"
        headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + os.getenv("MIA_API_TOKEN")
        }
        files = (
            'json_file',
            (
                os.path.basename(jsonfile.name),
                open(jsonfile.name, "rb"),
                'application/json'
            )
        )
        response = requests.request(
            "POST",
            runmodelpath,
            headers=headers,
            files=files
        )
        response_return(response)


class MIAProduct:
    """
    This class calls and retrieves the MIA Products. The name given
    must be of a MIA Product listed in available_products

    :param name: str The name of the Product

    """

    def __init__(
            self,
            name: str):
        if any(x['name'] == name for x in self.available_products()):
            self.name = name
        else:
            raise Exception(f"Product {name} not available")
        self.task_id = None

    @staticmethod
    def available_products():
        """
        Lists the available MIA Products

        :return: List[dict] with available products

        """
        availableproductspath = f"{APIPATH}/products/available"
        headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + os.getenv("MIA_API_TOKEN")
        }
        response = requests.request(
            "GET",
            availableproductspath,
            headers=headers
        )
        response_return(response)
        return response.json()

    def available_dates(
            self):
        """
        Lists the available dates for a MIA Product

        :return: List[str] with available dates

        """
        availabledatespath = f"{APIPATH}/products/{self.name}/dates"
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + os.getenv("MIA_API_TOKEN")
        }
        response = requests.request(
            "GET",
            availabledatespath,
            headers=headers
        )
        response_return(response)
        return response.json()

    def call(
            self,
            rundate: str):
        """
        Calls a MIA Product for a desired rundate, if available

        :param rundate: str Rundate, it must be in format YYYY-MM-DD

        """
        callpath = f"{APIPATH}/tasks"
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + os.getenv("MIA_API_TOKEN")
        }
        data = json.dumps({"type": self.name, "rundate": rundate})
        response = requests.request(
            "POST",
            callpath,
            headers=headers,
            data=data
        )
        response_return(response)
        self.task_id = response.json()['task_id']
        message = f"MIA_API: Created task {self.task_id} " \
                  f"to process product {self.name}"
        print(message)

    def status(
            self):
        """
        Gets the processing status of a called MIA Product
        If no product has been called, this will return a warning

        :param rundate: str Rundate, it must be in format YYYY-MM-DD
        :return: str SUCCESS, PENDING, FAILURE or NO TASK

        """
        if self.task_id is None:
            status = "NO TASK. Create one using the method call"
        else:
            statuspath = f"{APIPATH}/tasks/{self.task_id}"
            headers = {
                'accept': 'application/json',
                'Authorization': 'Bearer ' + os.getenv("MIA_API_TOKEN")
            }
            response = requests.request(
                "GET",
                statuspath,
                headers=headers
            )
            status = response.json()['task_status']
        return status

    def retrieve(
            self,
            outpath: str = None):
        """
        Retrieves a MIA Product successfully processed
        If the product fails, an error is raised

        :param outpath: str Desired outpath, there are three possibilities:
            1) Path is a directory: retrieves in it with original filename
            2) Path is a file: retrieves to this file
            3) Path is None: retrieves with the original filename in the
            current directory

        """
        retrieve_message = f"MIA_API: Retrieving product {self.name} " \
                           f"processed by task {self.task_id}"
        print(retrieve_message)
        done = False
        while not done:
            status = self.status()
            if status != 'PENDING':
                done = True
                if status != 'SUCCESS':
                    error_message = f"Product {self.name} " \
                                    "finished with errors"
                    raise Exception(error_message)
                success_message = f"MIA_API: Product {self.name} " \
                                  f"successfully processed by task {self.task_id}"
                print(success_message)

        download_message = f"MIA_API: Downloading product {self.name} " \
                           f"result of task {self.task_id}"
        print(download_message)
        retrievepath = f"{APIPATH}/tasks/get/{self.task_id}"
        headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + os.getenv("MIA_API_TOKEN")
        }
        response = requests.request(
            "GET",
            retrievepath,
            headers=headers,
            stream=True
        )
        total = int(response.headers['content-length'])
        original_file = response.headers["content-disposition"].split('"')[1]
        if outpath:
            if os.path.isdir(outpath):
                filename = f"{outpath}/{original_file}"
            else:
                filename = outpath
        else:
            filename = original_file
        print(f"MIA_API: Downloading file {filename}")
        with open(filename, "wb") as f, tqdm(
                desc=filename,
                total=total,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                bar.update(size)
