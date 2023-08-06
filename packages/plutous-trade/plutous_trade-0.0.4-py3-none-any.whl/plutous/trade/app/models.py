from pydantic import BaseModel

from plutous.enums import Exchange
from plutous.trade.enums import AssetType, BotType, StrategyDirection, StrategyType


class StrategyPost(BaseModel):
    name: str
    description: str
    type: StrategyType
    asset_type: AssetType
    direction: StrategyDirection


class BotPost(BaseModel):
    name: str
    strategy_id: int
    api_key_id: int
    type: BotType
    allocated_capital: float
    accumulate: bool = True
    max_position: int = 1


class ApiKeyPost(BaseModel):
    name: str
    exchange: Exchange
    key: str
    secret: str
    passphrase: str | None = None
