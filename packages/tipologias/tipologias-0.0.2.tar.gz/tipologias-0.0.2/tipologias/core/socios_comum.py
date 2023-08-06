from datetime import datetime

from tipologias.core.base import BaseTipologia
from tipologias.queries.socios import Q_LIST_SOCIO_CNPJ


class SociosComum(BaseTipologia):
    """Classe que implementa a tipologia SociosComum para analisar a ocorrência de sócios em comum entre cnpjs.

    Args:
        cnpj_list (tuple): Uma lista de cnpjs para analisar.

    Attributes:
        cnpj_list (tuple): Uma lista de cnpjs para analisar.
        df (pandas.DataFrame): O resultado da análise, armazenado em um DataFrame do pandas.

    Methods:
        input_data(): Extrai os dados necessários do banco de dados "big_data_cieg".
        processor(): Processa os dados extraídos e armazena o resultado em um DataFrame.
        execute(): Executa a análise completa.
    """

    def __init__(self, engine, cnpj_list: list[str], data_entrada=None, data_saida=None) -> None:
        """Inicializa a classe SociosComum com os parâmetros necessários.

        Args:
            crtl_analise_pregao_id (int): O ID da análise de pregão associada a essa tipologia.
            lista_pregoes (tuple): Uma lista de números de pregão para analisar.
        """
        self._engine = engine
        self._cnpj_list = set(cnpj_list)
        self._data_entrada = data_entrada or datetime.now().date()
        self._data_saida = data_saida or datetime.now().date()
        super().__init__(__class__.__name__)

    def input_data(self):
        query = Q_LIST_SOCIO_CNPJ.format(
            cnpj_list="','".join(self._cnpj_list), data_entrada=self._data_entrada, data_saida=self._data_saida
        )
        self._df = self._pd.read_sql_query(query, self._engine)

    def processor(self):
        df_temp = self._pd.DataFrame()
        for row in self._df.itertuples(name="Socio"):
            query = f'NUM_CNPJ_EMPRESA != "{row.NUM_CNPJ_EMPRESA}" and (NUM_CPF == "{row.NUM_CPF}" or NUM_CNPJ == "{row.NUM_CNPJ}")'
            df_query = self._df.query(query)
            df_temp = self._pd.concat([df_temp, df_query], ignore_index=True)

        self._df = df_temp
