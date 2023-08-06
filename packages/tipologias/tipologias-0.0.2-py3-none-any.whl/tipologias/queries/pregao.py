PARTICIPANTE_PREGAO = """
SELECT part.[numprp]
      ,part.[numero_pregao]
      ,[prgDataAbertura]
      ,[prgObjeto]
      ,[prpCNPJ]
      ,[prpRazaoSocial]
  FROM [BIG_DATA_CIEG].[dbo].[trilhas_participantes_pregao] part
  INNER JOIN [BIG_DATA_CIEG].[dbo].[trilhas_pregao] AS pregao ON pregao.numprp = part.numprp
  WHERE part.[numprp] IN ({pregao_list})
"""
