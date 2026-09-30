from pathlib import Path
from config import ARQUIVO_GESTORES, ARQUIVO_STATUS, ARQUIVO_TREINAMENTOS, PASTA_LOGS, EMAIL_DESTINO_PROFESSOR, GESTOR_ID_RELATORIO_PROFESSOR
from log_config import configurar_logging
from extracao import extrair_dados
from tratamento import tratar_gestores, tratar_status, tratar_treinamentos
from integracao import integrar_projetos
from regras_negocio import calcular_status_projeto, gerar_relatorios_por_gestor
from envio_email import enviar_relatorios, enviar_para_professor

logger = configurar_logging(PASTA_LOGS)


def main():

    logger.info("INICIANDO AUTOMAÇÃO")
    print("INICIANDO AUTOMAÇÃO")

    try:
        # utilizando o modulo de extracao
        df_gestores, df_status, df_treinamentos = extrair_dados(
            ARQUIVO_GESTORES,
            ARQUIVO_STATUS,
            ARQUIVO_TREINAMENTOS
        )
        logger.info("Extração concluída: %d gestores, %d projetos, %d treinamentos",
                    len(df_gestores), len(df_status), len(df_treinamentos))
    except Exception:
        logger.exception("Falha na etapa de extração")
        raise

    try:
        # utilizando o modulo de tratamento
        df_gestores = tratar_gestores(df_gestores)
        df_status = tratar_status(df_status)
        df_treinamentos = tratar_treinamentos(df_treinamentos)
        logger.info("Tratamento concluído com sucesso")
    except Exception:
        logger.exception("Falha na etapa de tratamento")
        raise

    try:
        # utilizando o modulo de join
        df_projetos = integrar_projetos(df_gestores, df_status)
        logger.info("Integração concluída: %d registros de projetos", len(df_projetos))
    except Exception:
        logger.exception("Falha na etapa de integração")
        raise

    try:
        # utilizando o modulo de regras de negocio
        df_projetos = calcular_status_projeto(df_projetos)
        relatorios = gerar_relatorios_por_gestor(df_projetos, df_treinamentos)
        logger.info("Regras de negócio aplicadas: %d relatórios gerados", len(relatorios))
    except Exception:
        logger.exception("Falha na etapa de regras de negócio")
        raise

    try:
        # utilizando o modulo de envio de email
        resumo_envio = enviar_relatorios(relatorios)
        logger.info(
            "Envio de e-mails concluído: %d sucesso(s), %d falha(s)",
            resumo_envio["sucesso"], resumo_envio["falha"]
        )
    except Exception:
        logger.exception("Falha na etapa de envio de e-mail")
        raise

    try:
        # entregável final: relatório de UM gestor para o e-mail real do professor
        gestor_id_escolhido = GESTOR_ID_RELATORIO_PROFESSOR or relatorios[0]["gestor_id"]
        if not GESTOR_ID_RELATORIO_PROFESSOR:
            logger.warning(
                "GESTOR_ID_RELATORIO_PROFESSOR não definido no .env — usando o primeiro "
                "gestor encontrado (%s)", gestor_id_escolhido
            )
 
        enviado_professor = enviar_para_professor(
            relatorios, gestor_id_escolhido, EMAIL_DESTINO_PROFESSOR
        )
        logger.info(
            "Envio ao professor (%s, gestor %s): %s",
            EMAIL_DESTINO_PROFESSOR, gestor_id_escolhido,
            "sucesso" if enviado_professor else "falha"
        )
    except Exception:
        logger.exception("Falha ao enviar o relatório final ao professor")
        raise
 
    logger.info("AUTOMAÇÃO FINALIZADA COM SUCESSO")
    print("AUTOMAÇÃO FINALIZADA COM SUCESSO")


if __name__ == "__main__":

    main()