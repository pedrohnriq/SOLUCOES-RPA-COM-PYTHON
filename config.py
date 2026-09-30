import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

PASTA_DADOS = BASE_DIR / "Base de Dados de RH"
PASTA_LOGS = BASE_DIR / "logs"
PASTA_EMAILS_ENVIADOS = BASE_DIR / "emails_enviados"

ARQUIVO_GESTORES = PASTA_DADOS / "gestores_projetos.csv"
ARQUIVO_STATUS = PASTA_DADOS / "status_projetos.csv"
ARQUIVO_TREINAMENTOS = PASTA_DADOS / "rh_treinamentos.csv"

EMAIL_DESTINO_PROFESSOR = "pedro.henriqcosta@gmail.com"
GESTOR_ID_RELATORIO_PROFESSOR = "G002"
# Envio de e-mail
# SIMULAR_ENVIO=True não manda e-mail de verdade: grava o conteúdo em
# PASTA_EMAILS_ENVIADOS e registra no log, o que já serve como evidência
# (print/arquivo) exigida na entrega. Para enviar de verdade, defina
# SIMULAR_ENVIO=false e preencha as variáveis de ambiente de SMTP abaixo
# (nunca coloque usuário/senha direto no código).
SIMULAR_ENVIO = os.getenv("SIMULAR_ENVIO", "true").lower() != "false"
#SIMULAR_ENVIO = os.getenv("SIMULAR_ENVIO")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USUARIO = os.getenv("SMTP_USUARIO")
SMTP_SENHA = os.getenv("SMTP_SENHA")