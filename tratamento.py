import pandas as pd
import unicodedata
import logging

logger = logging.getLogger(__name__)


def normalizar_texto(valor):

    if pd.isna(valor):
        return valor

    valor = str(valor).strip()

    valor = " ".join(valor.split())

    return valor


def remover_acentos(texto):

    if pd.isna(texto):
        return texto

    texto = unicodedata.normalize("NFKD", texto)

    return "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )


def padronizar_categoria(valor):

    if pd.isna(valor):
        return valor

    valor = normalizar_texto(valor)

    valor = remover_acentos(valor)

    return valor.upper()


def tratar_gestores(df):

    try:
        df = df.copy()

        # Remover espaços e padronizar nomes
        df["gestor_nome"] = (df["gestor_nome"].apply(normalizar_texto).str.title())

        # Padronizar área
        df["area"] = df["area"].apply(padronizar_categoria)

        # Padronizar código
        df["codigo_projeto"] = (
            df["codigo_projeto"]
            .apply(normalizar_texto)
            .str.upper()
        )

        # Padronizar gestor
        df["gestor_id"] = (
            df["gestor_id"]
            .apply(normalizar_texto)
            .str.upper()
        )

        # Email
        df["email_gestor"] = (
            df["email_gestor"]
            .apply(normalizar_texto)
            .str.lower()
        )

        # Remover duplicidades
        linhas_antes = len(df)
        df = df.drop_duplicates()
        logger.info(
            "tratar_gestores: %d linhas tratadas (%d duplicadas removidas)",
            len(df), linhas_antes - len(df)
        )

        return df

    except Exception:
        logger.exception("Falha ao tratar a base de gestores")
        raise


def tratar_status(df):

    try:
        df = df.copy()

        df["codigo_projeto"] = (
            df["codigo_projeto"]
            .apply(normalizar_texto)
            .str.upper()
        )

        # Datas
        colunas_datas = [
                "data_inicio",
                "data_prevista_fim",
                "data_conclusao"
            ]

        for coluna in colunas_datas:
            df[coluna] = pd.to_datetime(
                df[coluna],
                format="mixed",
                errors="coerce"
            )

        # As colunas de data permanecem como datetime (não como string).
        # Isso é essencial para o regras_negocio.py, que precisa comparar
        # data_inicio / data_prevista_fim / data_conclusao para calcular
        # status e duração em dias. A formatação "dd/mm/aaaa" para exibição
        # deve ser feita apenas na hora de montar o e-mail (envio_email.py),
        # nunca antes disso.

        # Percentual
        df["percentual_concluido"] = pd.to_numeric(
            df["percentual_concluido"],
            errors="coerce"
        )

        # Orçamento
        df["valor_orcado"] = pd.to_numeric(
            df["valor_orcado"],
            errors="coerce"
        )

        # Remover duplicidades
        linhas_antes = len(df)
        df = df.drop_duplicates(
            subset=["codigo_projeto"],
            keep="first"
        )
        logger.info(
            "tratar_status: %d linhas tratadas (%d duplicadas removidas)",
            len(df), linhas_antes - len(df)
        )

        return df

    except Exception:
        logger.exception("Falha ao tratar a base de status dos projetos")
        raise


def tratar_treinamentos(df):

    try:
        df = df.copy()

        # Nome
        df["colaborador_nome"] = (
            df["colaborador_nome"]
            .apply(normalizar_texto)
            .str.title()
        )

        # Área
        df["area"] = df["area"].apply(padronizar_categoria)

        # Treinamento
        df["treinamento"] = df["treinamento"].apply(normalizar_texto)

        # Status
        df["status_treinamento"] = (
            df["status_treinamento"]
            .apply(padronizar_categoria)
        )

        # Gestor
        df["gestor_id_area"] = (
            df["gestor_id_area"]
            .apply(normalizar_texto)
            .str.upper()
        )

        # Nome do gestor
        df["gestor_area_responsavel"] = (
            df["gestor_area_responsavel"]
            .apply(normalizar_texto)
            .str.title()
        )

        # Email
        df["email_gestor_area"] = (
            df["email_gestor_area"]
            .apply(normalizar_texto)
            .str.lower()
        )

        # Data limite
        df["data_limite"] = pd.to_datetime(
            df["data_limite"],
            format="mixed",
            errors="coerce"
        )

        # Remover duplicados
        linhas_antes = len(df)
        df = df.drop_duplicates()
        logger.info(
            "tratar_treinamentos: %d linhas tratadas (%d duplicadas removidas)",
            len(df), linhas_antes - len(df)
        )

        return df

    except Exception:
        logger.exception("Falha ao tratar a base de treinamentos")
        raise