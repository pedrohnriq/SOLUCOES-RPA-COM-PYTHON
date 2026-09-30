import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

STATUS_EM_ANDAMENTO = "Em andamento"
STATUS_ATRASADO = "Atrasado"
STATUS_CONCLUIDO_PRAZO = "Concluído dentro do prazo"
STATUS_CONCLUIDO_ATRASO = "Concluído com atraso"

STATUS_CONCLUIDOS = (STATUS_CONCLUIDO_PRAZO, STATUS_CONCLUIDO_ATRASO)
STATUS_NAO_CONCLUIDOS = (STATUS_EM_ANDAMENTO, STATUS_ATRASADO)

TREINAMENTO_CONCLUIDO = "CONCLUIDO"  # já vem sem acento e em upper do tratamento


def calcular_status_projeto(df_projetos, data_referencia=None):
    """
    Deduz a situação de cada projeto comparando data_inicio, data_prevista_fim
    e data_conclusao. Não depende de nenhum rótulo textual pronto.

    - Concluído dentro do prazo : data_conclusao preenchida e <= data_prevista_fim
    - Concluído com atraso      : data_conclusao preenchida e >  data_prevista_fim
    - Atrasado                  : sem data_conclusao e data_prevista_fim já passou
    - Em andamento               : sem data_conclusao e data_prevista_fim ainda não passou
    """
    try:
        df = df_projetos.copy()

        hoje = data_referencia or pd.Timestamp.now().normalize()

        concluido = df["data_conclusao"].notna()
        dentro_do_prazo = df["data_conclusao"] <= df["data_prevista_fim"]
        prazo_vencido = df["data_prevista_fim"] < hoje

        condicoes = [
            concluido & dentro_do_prazo,
            concluido & ~dentro_do_prazo,
            ~concluido & prazo_vencido,
            ~concluido & ~prazo_vencido,
        ]
        valores = [
            STATUS_CONCLUIDO_PRAZO,
            STATUS_CONCLUIDO_ATRASO,
            STATUS_ATRASADO,
            STATUS_EM_ANDAMENTO,
        ]

        # default="Indefinido" cobre casos de data_prevista_fim ausente,
        # que não deveriam existir em dados válidos, mas evita erro silencioso
        df["status_projeto"] = np.select(condicoes, valores, default="Indefinido")

        indefinidos = (df["status_projeto"] == "Indefinido").sum()
        if indefinidos:
            logger.warning(
                "%d projeto(s) com status indefinido (provável data_prevista_fim ausente)",
                indefinidos,
            )

        logger.info(
            "calcular_status_projeto: %s",
            df["status_projeto"].value_counts().to_dict(),
        )

        return df

    except Exception:
        logger.exception("Falha ao calcular o status dos projetos")
        raise


def _indicadores_projetos(df_gestor):
    """Indicadores do Bloco 1 para os projetos de UM gestor."""

    total_projetos = len(df_gestor)

    contagem_status = {
        status: int((df_gestor["status_projeto"] == status).sum())
        for status in (STATUS_EM_ANDAMENTO, STATUS_ATRASADO,
                       STATUS_CONCLUIDO_PRAZO, STATUS_CONCLUIDO_ATRASO)
    }

    nao_concluidos = df_gestor[df_gestor["status_projeto"].isin(STATUS_NAO_CONCLUIDOS)]
    percentual_medio_execucao = (
        round(nao_concluidos["percentual_concluido"].mean(), 1)
        if not nao_concluidos.empty and nao_concluidos["percentual_concluido"].notna().any()
        else None
    )

    concluidos = df_gestor[df_gestor["status_projeto"].isin(STATUS_CONCLUIDOS)]
    duracoes = (concluidos["data_conclusao"] - concluidos["data_inicio"]).dt.days
    tempo_medio_duracao_dias = (
        round(duracoes.mean(), 1) if not duracoes.dropna().empty else None
    )

    valor_total_orcado = df_gestor["valor_orcado"].sum(skipna=True)

    return {
        "total_projetos": total_projetos,
        "projetos_por_status": contagem_status,
        "percentual_medio_execucao": percentual_medio_execucao,
        "tempo_medio_duracao_dias": tempo_medio_duracao_dias,
        "valor_total_orcado": round(float(valor_total_orcado), 2),
    }


def _indicadores_treinamentos(df_treinamentos, areas, data_referencia=None):
    """Indicadores do Bloco 2 para as áreas sob responsabilidade de UM gestor."""

    hoje = data_referencia or pd.Timestamp.now().normalize()

    df_area = df_treinamentos[df_treinamentos["area"].isin(areas)]

    total_treinamentos = len(df_area)
    concluido = df_area["status_treinamento"] == TREINAMENTO_CONCLUIDO
    vencido = ~concluido & df_area["data_limite"].notna() & (df_area["data_limite"] < hoje)
    pendente = ~concluido & ~vencido

    percentual_conformidade = (
        round((concluido.sum() / total_treinamentos) * 100, 1)
        if total_treinamentos
        else None
    )

    colaboradores_vencidos = sorted(
        df_area.loc[vencido, "colaborador_nome"].dropna().unique().tolist()
    )

    return {
        "total_treinamentos": total_treinamentos,
        "treinamentos_pendentes": int(pendente.sum()),
        "treinamentos_vencidos": int(vencido.sum()),
        "percentual_conformidade": percentual_conformidade,
        "colaboradores_treinamento_vencido": colaboradores_vencidos,
    }


def gerar_relatorios_por_gestor(df_projetos, df_treinamentos, data_referencia=None):
    """
    Monta, para cada gestor, um dicionário com tudo que o e-mail precisa:
    identificação do gestor + Bloco 1 (projetos) + Bloco 2 (treinamentos das
    áreas sob sua responsabilidade).

    df_projetos precisa já ter passado por calcular_status_projeto.
    Um gestor pode responder por mais de uma área (a lista de áreas é
    deduzida a partir dos próprios projetos que ele gerencia) — nada aqui é
    fixo para um gestor específico.
    """
    try:
        relatorios = []

        gestores = (
            df_projetos[["gestor_id", "gestor_nome", "email_gestor"]]
            .drop_duplicates()
            .sort_values("gestor_id")
        )

        for _, gestor in gestores.iterrows():
            df_gestor = df_projetos[df_projetos["gestor_id"] == gestor["gestor_id"]]

            areas_do_gestor = sorted(df_gestor["area"].dropna().unique().tolist())

            relatorio = {
                "gestor_id": gestor["gestor_id"],
                "gestor_nome": gestor["gestor_nome"],
                "email_gestor": gestor["email_gestor"],
                "areas": areas_do_gestor,
                "projetos": _indicadores_projetos(df_gestor),
                "treinamentos": _indicadores_treinamentos(
                    df_treinamentos, areas_do_gestor, data_referencia
                ),
            }
            relatorios.append(relatorio)

        logger.info("gerar_relatorios_por_gestor: %d gestores processados", len(relatorios))

        return relatorios

    except Exception:
        logger.exception("Falha ao gerar os relatórios por gestor")
        raise
