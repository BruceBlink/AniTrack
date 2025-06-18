import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict

import requests

import utils
from common import contants


@dataclass(order=True)
class Result:
    platform: str
    title: str
    update_count: str
    update_info: str
    image_url: str
    detail_url: str
    update_time: str

    def __getitem__(self, key: str):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def __hash__(self):
        return hash((
            self.platform,
            self.title,
            self.update_count,
            self.update_info,
            self.image_url,
            self.detail_url,
            self.update_time
        ))

    def to_dict(self) -> dict:
        """将 Result 对象转换为字典，用于序列化等操作。"""
        return asdict(self)


class AbstractFetcher(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.api_url = None
        self.platform = None
        self.result = {utils.weekday_today: []}
        self.response = None

    @abstractmethod
    def send_request(self):
        self.logger.info(f"Fetching today's data from {self.api_url} ...")
        try:
            self.response = requests.get(self.api_url, headers=contants.HEADERS, timeout=10)
            self.response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(f"请求 {self.api_url} 失败：{e}")
            raise e
