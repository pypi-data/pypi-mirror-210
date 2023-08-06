from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from plutous.trade.enums import BotType

from .api_key import ApiKey
from .base import Base, Enum
from .strategy import Strategy

if TYPE_CHECKING:
    from .position import Position


class Bot(Base):
    name: Mapped[str] = mapped_column(unique=True)
    type: Mapped[BotType] = mapped_column(Enum(BotType))
    strategy_id: Mapped[int] = mapped_column(ForeignKey(Strategy.id))
    api_key_id: Mapped[int] = mapped_column(ForeignKey(ApiKey.id))
    allocated_capital: Mapped[float]
    max_position: Mapped[int]
    accumulate: Mapped[bool]

    api_key: Mapped[ApiKey] = relationship(ApiKey, back_populates="bots")
    strategy: Mapped[Strategy] = relationship(Strategy, back_populates="bots")
    positions: Mapped[list["Position"]] = relationship(
        "Position", back_populates="bot"
    )

    @property
    def exchange(self):
        return self.api_key.exchange