from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import logging


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

    @abstractmethod
    def fetch_data(self):
        """抽象方法，子类需要实现数据抓取逻辑。"""
        pass
