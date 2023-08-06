from dataclasses import dataclass
from typing import Optional
import requests
import hashlib
from datetime import datetime, timedelta

@dataclass
class AquaTempData:
    powered_on: bool
    inlet_temp: float
    outlet_temp: float
    target_temp: float
    min_target_temp: float
    max_target_temp: float

@dataclass
class XToken:
    value: str
    created_at: datetime

class AquaTemp():
    __base_url = "http://cloud.linked-go.com:84/cloudservice/api/app/"
    __x_token: Optional[XToken] = None

    def __init__(self, device_code: str, user_name: str, password: str) -> None:
        self.device_code = device_code
        self.user_name = user_name
        self.password_md5 = hashlib.md5(password.encode()).hexdigest()

    def __refresh_x_token(self):
        body = {
            "password": self.password_md5,
            "login_source": "IOS",
            "type": "2",
            "user_name": self.user_name
        }

        r = requests.post("%suser/login.json"%(self.__base_url), json=body)

        self.__x_token = XToken(value=r.json()["object_result"]["x-token"], created_at=datetime.now())

    def __get_x_token(self):
        if self.__x_token is None:
            self.__refresh_x_token()
        elif self.__x_token.created_at + timedelta(days=1) < datetime.now():
            self.__refresh_x_token()
        else:
            pass
        return self.__x_token.value

    def get_data(self) -> AquaTempData:
        headers = { "x-token": self.__get_x_token() }
        body = {
            "device_code": self.device_code,
            "protocal_codes": [
                "power",
                # "Mode",
                "T02",
                "T03",
                # "R01",
                "R02",
                "R03",
                # "Manual-mute",
                # "1158",
                # "1159",
                # "H03",
                # "R08",
                # "R09",
                "R10",
                "R11",
                # "R12",
                # "T05",
                # "H02",
                # "software_code",
                # "ver"
            ]
        }
        r = requests.post("%sdevice/getDataByCode.json"%(self.__base_url), headers=headers, json=body)
        result = dict(map(lambda x: (x["code"], x["value"]), r.json()["object_result"]))
        return AquaTempData(
            powered_on=bool(result["power"]),
            inlet_temp=float(result["T02"]),
            outlet_temp=float(result["T03"]),
            target_temp=float(result["R02"]),
            min_target_temp=float(result["R10"]),
            max_target_temp=float(result["R11"]),
        )

    def __control (self, protocol_code: str, value: str):
        headers = { "x-token": self.__get_x_token() }
        body = {
            "param": [
                {
                    "device_code": self.device_code,
                    "value": value,
                    "protocol_code": protocol_code
                }
            ]
        }
        r = requests.post("%sdevice/control.json"%(self.__base_url), headers=headers, json=body)

    def power_off(self):
        self.__control("Power", "0")

    def power_on(self):
        self.__control("Power", "1")

    def set_target_temp(self, temp: float):
        self.__control("R02", str(temp))
