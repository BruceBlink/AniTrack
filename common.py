from dataclasses import dataclass


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