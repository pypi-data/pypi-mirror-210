from abc import abstractmethod

from tipologias.utils.padastools import BaseDataFrame, DataFrame


class Tipologia(BaseDataFrame):
    @abstractmethod
    def input_data(self):
        """Extrai os dados necessários do banco de dados e armazena em um DataFrame."""
        ...

    @abstractmethod
    def processor(self):
        """Processa os dados extraídos e armazena o resultado em um DataFrame."""
        ...

    @abstractmethod
    def output_data(self):
        """Escreve o resultado da análise na tabela resposta do banco de dados."""
        ...

    @abstractmethod
    def execute(self):
        """Executa a análise completa."""
        ...


class BaseTipologia(Tipologia):
    def __init__(self, subclass_name) -> None:
        self._subclass_name = subclass_name
        self._executed = False
        super().__init__(__class__.__name__)

    def __len__(self) -> int:
        self.execute()
        return super().__len__()

    def __iter__(self):
        self.execute()
        return super().__iter__()

    def __aiter__(self):
        self.execute()
        return super().__aiter__()

    def __enter__(self):
        self.execute()
        return super().__enter__()

    async def __aenter__(self):
        self.execute()
        return await super().__aenter__()

    def __add__(self, other):
        self.execute()
        other.execute()
        return DataFrame(self._df) + DataFrame(other._df)

    def __radd__(self, other):
        self.execute()
        other.execute()
        return DataFrame(self._df) + DataFrame(other._df)

    def col_to_list(self, col_name, drop_duplicates=True):
        self.execute()
        return super().col_to_list(col_name, drop_duplicates)

    def processor(self):
        ...

    def output_data(self):
        """Escreve o resultado da análise na tabela resposta do banco de dados."""
        self.execute()
        return self._df

    def execute(self):
        """Executa a sequência do script completa."""
        if self._executed:
            return self

        self.input_data()
        self.processor()
        self._executed = True
        return self
