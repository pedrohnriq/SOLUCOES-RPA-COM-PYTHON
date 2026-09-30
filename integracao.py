import logging
import pandas as pd
import os

logger = logging.getLogger(__name__)


def integrar_projetos(df_gestores, df_status):

    try:
        df_projetos = pd.merge(
            df_gestores,
            df_status,
            on="codigo_projeto",
            how="left"
        )

        
        sem_correspondencia = df_projetos["data_inicio"].isna().sum() if "data_inicio" in df_projetos else 0
        if sem_correspondencia:
            logger.warning(
                "%d projeto(s) em gestores_projetos.csv sem correspondência em status_projetos.csv",
                sem_correspondencia
            )

        logger.info("integrar_projetos: %d registros após o merge", len(df_projetos))
        
        return df_projetos
    
    except Exception:
        logger.exception("Falha ao integrar gestores e status dos projetos")
        raise

    