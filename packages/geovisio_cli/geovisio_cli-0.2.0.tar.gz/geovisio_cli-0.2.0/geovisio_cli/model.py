from dataclasses import dataclass
from typing import Optional


@dataclass
class Geovisio:
    url: str
    token: Optional[str] = None
