from abc import ABC, abstractmethod
from asyncio import Lock, sleep
from collections.abc import AsyncIterator, Awaitable, Iterator, Sized
from functools import reduce

import pandas as pd


class AbstractDataFrame(ABC, AsyncIterator, Awaitable, Sized, Iterator):
    @abstractmethod
    def __repr__(self):
        """Representação do obj."""
        ...

    @abstractmethod
    def __str__(self):
        """string do obj."""
        ...

    @abstractmethod
    def __enter__(self):
        ...

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...


class BaseDataFrame(AbstractDataFrame):
    def __init__(self, subclass_name) -> None:
        self._subclass_name = subclass_name
        self._pd = pd
        self._df = self._pd.DataFrame()
        self._lock = Lock()
        self._iterator = None

    def __len__(self) -> int:
        return len(self._df)

    def __await__(self):
        return sleep(0.0001, result=self.execute()).__await__()

    def __iter__(self):
        self._iterator = self._df.itertuples(name=self._subclass_name, index=False)
        return (it for it in self._iterator)

    def __aiter__(self):
        self._iterator = self._df.itertuples(name=self._subclass_name, index=False)

        async def async_gen():
            for it in self._iterator:
                await sleep(0.0001)
                yield it

        return async_gen()

    def __next__(self):
        return next(self._iterator)

    async def __anext__(self):
        async with self._lock:
            try:
                row = next(self._iterator)
                await sleep(0.0001)
                return row
            except StopIteration:
                raise StopAsyncIteration

    def __repr__(self):
        return repr(self._df)

    def __str__(self):
        return str(self._df)

    def __enter__(self):
        return self._df

    async def __aenter__(self):
        return self._df

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return None

    def col_to_list(self, col_name, drop_duplicates=True):
        if not drop_duplicates:
            return self._df[col_name].to_list()
        return self._df[col_name].drop_duplicates().to_list()


class DataFrame(BaseDataFrame):
    def __init__(self, df):
        super().__init__(__class__.__name__)
        self._df = df

    @property
    def df(self):
        return self._df

    def __add__(self, other):
        combined = self._pd.concat([self._df, other._df], ignore_index=True)
        return DataFrame(combined)

    @classmethod
    def concat_df(cls, df_list):
        df = reduce(lambda x, y: x + y, df_list)._df
        return DataFrame(df)
