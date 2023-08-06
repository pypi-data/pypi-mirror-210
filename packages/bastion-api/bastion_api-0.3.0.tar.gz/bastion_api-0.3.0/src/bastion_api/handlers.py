from abc import ABC
from enum import Enum
from http.cookies import SimpleCookie

from aiohttp import ClientSession
from pydantic import BaseModel


class BastionDeviceType(Enum):
    SYSTEM = 0  # Система
    WEB_GROUP = 40  # Сетевая группа
    CONTROLLER = 5  # Контроллер
    ALARM_INPUT = 12  # Тревожный вход
    RELE = 10  # Реле
    TURNSTILE = 22  # Турникет
    DOOR = 3  # Дверь
    READER = 19  # Считыватель
    All = ""


async def _handle_response(response, dto):
    model_list = []
    for info in response:
        model_list.append(dto(**info))
    return model_list


class ResponseMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATH = "PATCH"
    DELETE = "DELETE"


class BastionConfig(BaseModel):
    iks_host: str
    iks_port: int
    iks_operator_login: str
    iks_operator_password: str


class BastionInfo(ABC):
    session = ClientSession
    bastion_servers: []
    _code_for_url: str = ""
    config: BastionConfig
    cookies: SimpleCookie

    log_debug: bool = False
    log_info: bool = False
