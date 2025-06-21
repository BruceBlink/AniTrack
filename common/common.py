import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
import aiohttp
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
        self.platform = str | None
        self.result = {utils.weekday_today: []}
        self.response_text = None

    async def send_request(self, session: aiohttp.ClientSession) -> None:
        if not self.api_url:
            raise RuntimeError("api_url 未设置")
        logging.info(f"Fetching today's data from [{self.platform}] {self.api_url} 发起异步请求 ...")
        try:
            async with session.get(self.api_url, headers=contants.HEADERS, timeout=10) as resp:
                resp.raise_for_status()
                self.response_text = await resp.text(encoding='utf-8')

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logging.error(f"from [{self.platform}] {self.api_url} 发起异步请求失败：{e}")
            raise e

    async def fetch_update_data(self, session: aiohttp.ClientSession) -> str | None:
        """异步获取数据并构建 Result 对象。"""
        await self.send_request(session)
        if not self.response_text:
            logging.error(f"从 [{self.platform}] {self.api_url} 获取数据失败")
            return None
        return self.response_text

    def _has_episode_info(self, episodes_info: str) -> bool:
        pass

    @abstractmethod
    def _build_result_from_episode(self, episodes: dict | Tag) -> Result:
        pass
