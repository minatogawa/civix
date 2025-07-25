"""
Configuração de logging estruturado com Loguru para o CiviX.
Centralizador para todo o sistema de logs da aplicação.
"""

import os
import sys
from pathlib import Path

from loguru import logger


def setup_logger():
    """
    Configura o sistema de logging estruturado com Loguru.

    Features:
    - Logs estruturados em JSON para produção
    - Logs coloridos e legíveis para desenvolvimento
    - Rotação automática de arquivos de log
    - Diferentes níveis configuráveis via .env
    - Context tracking para requests
    - Categorias de log configuráveis
    """

    # Remove handler padrão do loguru
    logger.remove()

    # Configurações baseadas no ambiente e .env
    env = os.getenv("FLASK_ENV", "development")
    log_level = os.getenv("LOG_LEVEL", "INFO" if env == "production" else "DEBUG")
    log_format = os.getenv("LOG_FORMAT", env)  # development/production

    # Configurações específicas de categorias
    log_requests = os.getenv("LOG_REQUESTS", "true").lower() == "true"
    log_database = os.getenv("LOG_DATABASE", "true").lower() == "true"
    log_telegram = os.getenv("LOG_TELEGRAM", "true").lower() == "true"

    # Configurações de retenção
    retention_days = int(os.getenv("LOG_RETENTION_DAYS", "30"))
    error_retention_days = int(os.getenv("LOG_ERROR_RETENTION_DAYS", "90"))

    # Diretório de logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Handler para console
    if log_format == "development":
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>",
            level=log_level,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )
    else:
        # Handler para console (produção) - JSON estruturado
        logger.add(
            sys.stdout,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
            level=log_level,
            serialize=True,  # Output em JSON
        )

    # Handler para arquivo principal
    logger.add(
        log_dir / "civix.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        level=log_level,
        rotation="100 MB",
        retention=f"{retention_days} days",
        compression="zip",
        serialize=log_format == "production",  # JSON apenas em produção
        backtrace=True,
        diagnose=True,
    )

    # Handler para erros críticos
    logger.add(
        log_dir / "errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="50 MB",
        retention=f"{error_retention_days} days",
        compression="zip",
        serialize=log_format == "production",
        backtrace=True,
        diagnose=True,
    )

    # Handler para bot do Telegram (se habilitado)
    if log_telegram:
        logger.add(
            log_dir / "telegram_bot.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
            level=log_level,
            rotation="50 MB",
            retention=f"{retention_days} days",
            compression="zip",
            filter=lambda record: "telegram" in record["name"].lower()
            or "bot" in record["name"].lower(),
            serialize=log_format == "production",
        )

    # Handler para requests HTTP (se habilitado)
    if log_requests:
        logger.add(
            log_dir / "requests.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra[method]} {extra[path]} | "
            "{extra[status_code]} | {extra[response_time]}ms | {message}",
            level="INFO",
            rotation="100 MB",
            retention=f"{retention_days} days",
            compression="zip",
            filter=lambda record: "extra" in record and "method" in record["extra"],
            serialize=log_format == "production",
        )

    # Log de inicialização
    logger.info(
        "Logger configurado com sucesso",
        env=env,
        log_level=log_level,
        log_format=log_format,
        log_requests=log_requests,
        log_database=log_database,
        log_telegram=log_telegram,
        retention_days=retention_days,
        error_retention_days=error_retention_days,
        log_dir=str(log_dir.absolute()),
    )

    return logger


def get_logger(name: str = None):
    """
    Retorna uma instância do logger com nome específico.

    Args:
        name: Nome do logger (geralmente __name__ do módulo)

    Returns:
        Logger configurado
    """
    if name:
        return logger.bind(name=name)
    return logger


def log_request_context(method: str, path: str, status_code: int, response_time: float):
    """
    Helper para log de requests HTTP com contexto estruturado.

    Args:
        method: Método HTTP (GET, POST, etc.)
        path: Path da requisição
        status_code: Código de status da resposta
        response_time: Tempo de resposta em ms
    """
    # Só loga se request logging estiver habilitado
    if os.getenv("LOG_REQUESTS", "true").lower() == "true":
        logger.bind(
            method=method,
            path=path,
            status_code=status_code,
            response_time=response_time,
        ).info("HTTP Request processed")


def log_telegram_event(event_type: str, user_id: int, message: str = None, **kwargs):
    """
    Helper para log de eventos do Telegram com contexto estruturado.

    Args:
        event_type: Tipo do evento (message, callback, command, etc.)
        user_id: ID do usuário no Telegram
        message: Mensagem associada ao evento
        **kwargs: Contexto adicional
    """
    # Só loga se telegram logging estiver habilitado
    if os.getenv("LOG_TELEGRAM", "true").lower() == "true":
        logger.bind(
            event_type=event_type, user_id=user_id, message=message, **kwargs
        ).info("Telegram event processed")


def log_database_operation(
    operation: str, table: str, duration: float = None, **kwargs
):
    """
    Helper para log de operações de banco de dados.

    Args:
        operation: Tipo da operação (SELECT, INSERT, UPDATE, DELETE)
        table: Nome da tabela
        duration: Duração da operação em ms
        **kwargs: Contexto adicional
    """
    # Só loga se database logging estiver habilitado
    if os.getenv("LOG_DATABASE", "true").lower() == "true":
        logger.bind(operation=operation, table=table, duration=duration, **kwargs).info(
            "Database operation completed"
        )


# Inicializa o logger automaticamente ao importar o módulo
setup_logger()
