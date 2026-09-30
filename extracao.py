import pandas as pd
from config import ARQUIVO_GESTORES, ARQUIVO_STATUS, ARQUIVO_TREINAMENTOS
import logging


logger = logging.getLogger(__name__)

def ler_csv(caminho):
    try:
        df = pd.read_csv(caminho)

        logger.info("Arquivo carregado com sucesso: %s", caminho.name)

        return df

    except Exception as erro:

        logger.exception(f"Erro ao carregar arquivo {caminho}: {erro}")

        raise


def extrair_dados(arquivo_gestores,
                  arquivo_status,
                  arquivo_treinamentos):

    df_gestores = ler_csv(arquivo_gestores)

    df_status = ler_csv(arquivo_status)

    df_treinamentos = ler_csv(arquivo_treinamentos)

    return df_gestores, df_status, df_treinamentos



df_gestores, df_status, df_treinamentos = extrair_dados(
    ARQUIVO_GESTORES, 
    ARQUIVO_STATUS, 
    ARQUIVO_TREINAMENTOS
)



