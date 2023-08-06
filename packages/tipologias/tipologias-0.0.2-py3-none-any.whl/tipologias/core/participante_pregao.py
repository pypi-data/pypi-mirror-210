from tipologias.core.base import BaseTipologia
from tipologias.queries.pregao import PARTICIPANTE_PREGAO


class ParticipantePregao(BaseTipologia):
    def __init__(self, engine, pregao_list: list[int]) -> None:
        self._engine = engine
        self._pregao_list = [str(pregao) for pregao in set(pregao_list)]
        super().__init__(__class__.__name__)

    def input_data(self):
        query = PARTICIPANTE_PREGAO.format(pregao_list=",".join(self._pregao_list))
        self._df = self._pd.read_sql_query(query, self._engine, dtype={"numprp": int})
