import dataclasses
from enum import Enum
from bittrade_huobi_websocket.models.book import RawOrderbook

class MarketDepthType(str, Enum):
    STEP0 = "step0"
    STEP1 = "step1"
    STEP2 = "step2"
    STEP3 = "step3"
    STEP4 = "step4"
    STEP5 = "step5"

class MarketDepthDepth(Enum):
    DEPTH_20 = 20
    DEPTH_10 = 10
    DEPTH_5 = 5

@dataclasses.dataclass(frozen=True)
class MarketDepthParams:
    symbol: str
    type: MarketDepthType = MarketDepthType.STEP0
    depth: MarketDepthDepth = MarketDepthDepth.DEPTH_20

@dataclasses.dataclass(frozen=True)
class MarketDepthResponse:
    ch: str
    status: str
    ts: int
    tick: RawOrderbook
