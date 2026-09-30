import logging
import smtplib
from datetime import datetime
from email.message import EmailMessage

from config import (
    PASTA_EMAILS_ENVIADOS,
    SIMULAR_ENVIO,
    SMTP_HOST,
    SMTP_PORT,
    SMTP_SENHA,
    SMTP_USUARIO,
)

logger = logging.getLogger(__name__)


def _formatar_numero(valor, sufixo=""):
    return "N/D" if valor is None else f"{valor}{sufixo}"


def _formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def montar_assunto(relatorio):
    return f"Relatório Gerencial - {relatorio['gestor_nome']}"


def montar_corpo(relatorio):
    """Monta o corpo do e-mail em texto simples, só com o escopo daquele gestor."""

    projetos = relatorio["projetos"]
    treinamentos = relatorio["treinamentos"]
    status_map = projetos["projetos_por_status"]

    linhas = [
        f"Olá, {relatorio['gestor_nome']}.",
        "",
        "Segue o relatório consolidado do setor: "
        f"{', '.join(relatorio['areas']) or 'sem área identificada'}.",
        "",
        "=== Projetos sob sua responsabilidade ===",
        f"Total de projetos: {projetos['total_projetos']}",
        f"  - Em andamento dentro do prazo: {status_map.get('Em andamento', 0)}",
        f"  - Em andamento com atraso: {status_map.get('Atrasado', 0)}",
        f"  - Concluído dentro do prazo: {status_map.get('Concluído dentro do prazo', 0)}",
        f"  - Concluído com atraso: {status_map.get('Concluído com atraso', 0)}",
        "Percentual médio de execução (projetos ainda não concluídos): "
        f"{_formatar_numero(projetos['percentual_medio_execucao'], '%')}",
        "Tempo médio de duração dos projetos concluídos: "
        f"{_formatar_numero(projetos['tempo_medio_duracao_dias'], ' dias')}",
        f"Valor total orçado: {_formatar_moeda(projetos['valor_total_orcado'])}",
        "",
        "=== Pendências de treinamento da sua área ===",
        f"Total de treinamentos: {treinamentos['total_treinamentos']}",
        f"Treinamentos pendentes: {treinamentos['treinamentos_pendentes']}",
        f"Treinamentos vencidos: {treinamentos['treinamentos_vencidos']}",
        "Percentual de conformidade: "
        f"{_formatar_numero(treinamentos['percentual_conformidade'], '%')}",
        "",
    ]

    if treinamentos["colaboradores_treinamento_vencido"]:
        linhas.append("Colaboradores com treinamento vencido (cobrança imediata):")
        linhas.extend(f"  - {nome}" for nome in treinamentos["colaboradores_treinamento_vencido"])
    else:
        linhas.append("Nenhum colaborador com treinamento vencido.")

    linhas.extend(["", "Relatório gerado automaticamente pela automação RPA."])

    return "\n".join(linhas)


def _salvar_simulacao(destinatario, assunto, corpo):
    """Grava o e-mail simulado em arquivo .txt"""

    PASTA_EMAILS_ENVIADOS.mkdir(parents=True, exist_ok=True)

    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"{carimbo}_{destinatario.replace('@', '_at_')}.txt"
    caminho = PASTA_EMAILS_ENVIADOS / nome_arquivo

    caminho.write_text(
        f"Para: {destinatario}\nAssunto: {assunto}\n\n{corpo}",
        encoding="utf-8",
    )
    return caminho


def _enviar_smtp(destinatario, assunto, corpo):
    if not SMTP_USUARIO or not SMTP_SENHA:
        raise RuntimeError(
            "SIMULAR_ENVIO=false mas SMTP_USUARIO/SMTP_SENHA não estão definidos "
            "como variáveis de ambiente."
        )

    mensagem = EmailMessage()
    mensagem["From"] = SMTP_USUARIO
    mensagem["To"] = destinatario
    mensagem["Subject"] = assunto
    mensagem.set_content(corpo)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as servidor:
        servidor.starttls()
        servidor.login(SMTP_USUARIO, SMTP_SENHA)
        servidor.send_message(mensagem)


def enviar_email(destinatario, assunto, corpo, simular=None):
    """
    Envia (ou simula o envio de) um e-mail. simular=None usa o valor de
    config.SIMULAR_ENVIO; passe True/False explicitamente para sobrescrever.
    """
    simular = SIMULAR_ENVIO if simular is None else simular

    try:
        if simular:
            caminho = _salvar_simulacao(destinatario, assunto, corpo)
            logger.info("[SIMULADO] E-mail para %s salvo em %s", destinatario, caminho)
        else:
            _enviar_smtp(destinatario, assunto, corpo)
            logger.info("E-mail enviado com sucesso para %s", destinatario)

        return True

    except Exception:
        logger.exception("Falha ao enviar e-mail para %s", destinatario)
        return False


def enviar_relatorios(relatorios, simular=None):
    """Dispara o e-mail de cada gestor e retorna um resumo {sucesso, falha}."""

    sucesso = 0
    falha = 0

    for relatorio in relatorios:
        assunto = montar_assunto(relatorio)
        corpo = montar_corpo(relatorio)

        enviado = enviar_email(relatorio["email_gestor"], assunto, corpo, simular=simular)

        if enviado:
            sucesso += 1
        else:
            falha += 1

    logger.info("enviar_relatorios: %d enviados, %d falharam", sucesso, falha)

    return {"sucesso": sucesso, "falha": falha}


def enviar_para_professor(relatorios, gestor_id, email_professor, simular=None):
    
    relatorio = next((r for r in relatorios if r["gestor_id"] == gestor_id), None)
 
    if relatorio is None:
        ids_disponiveis = [r["gestor_id"] for r in relatorios]
        raise ValueError(
            f"gestor_id '{gestor_id}' não encontrado. IDs disponíveis: {ids_disponiveis}"
        )
 
    assunto = f"[Desafio Final RPA] {montar_assunto(relatorio)}"
    corpo = montar_corpo(relatorio)
 
    enviado = enviar_email(email_professor, assunto, corpo, simular=simular)
 
    if enviado:
        logger.info("Relatório de %s enviado ao professor (%s)", gestor_id, email_professor)
    else:
        logger.error("Falha ao enviar relatório de %s ao professor", gestor_id)
 
    return enviado