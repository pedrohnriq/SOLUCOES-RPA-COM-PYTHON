import logging
from pathlib import Path


def configurar_logging(pasta_logs):

    Path(pasta_logs).mkdir(
        parents=True,
        exist_ok=True
    )

    arquivo_log = Path(pasta_logs) / "execucao_rpa.log"

    logging.basicConfig(
        filename=arquivo_log,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8"
    )

    return logging.getLogger(__name__)