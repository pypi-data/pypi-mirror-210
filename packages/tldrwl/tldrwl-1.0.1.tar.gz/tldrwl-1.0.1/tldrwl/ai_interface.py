#!/usr/bin/env python3
# www.jrodal.com

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .exception import TldrwlException
from .register import Register
from enum import Enum


class Model(Enum):
    GPT35TURBO = "gpt-3.5-turbo"

    @property
    def cost_per_1000_tokens(self) -> float:
        if self is self.GPT35TURBO:
            return 0.002
        else:
            return 0


@dataclass
class Summary:
    text: str
    num_tokens: int
    model: Model

    @property
    def estimated_cost_usd(self) -> float:
        return self.num_tokens * self.model.cost_per_1000_tokens * (1 / 1000)


class AiInterface(ABC):
    @abstractmethod
    def _summarize_sync(self, text: str) -> Summary:
        pass

    @abstractmethod
    async def _summarize_async(self, text: str) -> Summary:
        pass

    def summarize_sync(self, text: str) -> Summary:
        if not Register.is_registered():
            Register.register()
        try:
            return self._summarize_sync(text)
        except TldrwlException:
            raise
        except Exception as e:
            raise TldrwlException(msg=str(e), cause="n/a", remediation="n/a") from e

    async def summarize_async(self, text: str) -> Summary:
        if not Register.is_registered():
            Register.register()
        try:
            return await self._summarize_async(text)
        except TldrwlException:
            raise
        except Exception as e:
            raise TldrwlException(msg=str(e), cause="n/a", remediation="n/a") from e
