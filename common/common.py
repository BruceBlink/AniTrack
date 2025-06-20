import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict

import requests
from bs4 import Tag

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
        return hash((  # 只比较标题和更新集数
            self.title,
            self.update_count,
        ))

    def __eq__(self, other):
        if not isinstance(other, Result):
            return NotImplemented
        return (
            # 只要标题和更新集数和相同即可
                self.title == other.title and
                self.update_count == other.update_count
        )

    def to_dict(self) -> dict:
        """将 Result 对象转换为字典，用于序列化等操作。"""
        return asdict(self)


class AbstractFetcher(ABC):
    def __init__(self):
        self.api_url = None
        self.platform = None
        self.result = {utils.weekday_today: []}
        self.response = None

    @abstractmethod
    def send_request(self):
        logging.info(f"Fetching today's data from {self.api_url} ...")
        try:
            self.response = requests.get(self.api_url, headers=contants.HEADERS, timeout=10)
            self.response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"请求 {self.api_url} 失败：{e}")
            raise e

    @abstractmethod
    def _build_result_from_episode(self, episodes: dict | Tag) -> Result:
        pass
