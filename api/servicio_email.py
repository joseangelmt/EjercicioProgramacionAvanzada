import asyncio
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class EmailService(ABC):
    """Interfaz para enviar avisos por correo. Cada subclase implementa un medio de envío."""

    @abstractmethod
    async def enviar_aviso_palabrota(self, ip: str, campo: str) -> None: ...


class EmailServiceSimulado(EmailService):
    """No envía correos: espera como lo haría un servidor SMTP y escribe el aviso en el log."""

    def __init__(self, segundos_espera: float = 1.0):
        self.__segundos_espera = segundos_espera

    async def enviar_aviso_palabrota(self, ip: str, campo: str) -> None:
        logger.info("Simulando envío de aviso por email: la IP %s intentó crear una tarea con palabrotas en '%s'", ip, campo)
        await asyncio.sleep(self.__segundos_espera)  # simula el tiempo de respuesta del servidor de correo
        logger.warning("Aviso por email: la IP %s intentó crear una tarea con palabrotas en '%s'", ip, campo)
