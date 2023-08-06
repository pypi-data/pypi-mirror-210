from asyncio import get_event_loop, sleep
from collections.abc import AsyncIterator, Collection
from functools import reduce, singledispatchmethod
from types import coroutine

from tipologias.utils.padastools import DataFrame


class AsyncCollection(AsyncIterator):
    def __init__(self, col: Collection, *, loop=None):
        self._iterator = self._aiter(col)
        self._loop = loop or get_event_loop()

    @singledispatchmethod
    @coroutine
    def _aiter(self, iterator):
        pass

    @_aiter.register
    @coroutine
    def _col_aiter(self, iterator: Collection):
        yield from iterator

    @_aiter.register
    @coroutine
    def _col_aiter(self, iterator: dict):
        yield from iterator.items()

    def __aiter__(self):
        return self

    async def __anext__(self):
        value = await self._loop.run_in_executor(None, next, self._iterator, self)
        if value is self:
            raise StopAsyncIteration
        return await sleep(0.001, result=value)


class ReduceTipologia:
    def __init__(self, tp_list) -> None:
        self._tp_list = tp_list
        self._df = None
        self.reduce_tp()

    def concat(self, x, y):
        return DataFrame(x._df) + DataFrame(y._df)

    def reduce_tp(self):
        self._df = reduce(self.concat, self._tp_list)._df
        return self._df
