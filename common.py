from dataclasses import dataclass


@dataclass(order=True)
class Result:
    platform: str
    title: str
    update_count: int
    update_info: str
    image_url: str
    detail_url: str
    update_time: str

    def __getitem__(self, key: str):
        return getattr(self, key)