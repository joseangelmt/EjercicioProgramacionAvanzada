from spanlp.palabrota import Palabrota

class FiltroContenido:
    """Censura palabrotas en español. Delega la detección en spanlp."""

    def __init__(self, caracter: str = "*"):
        self.__palabrota = Palabrota(censor_char=caracter)

    def contiene_palabrotas(self, texto: str) -> bool:
        return self.__palabrota.contains_palabrota(texto)

    def limpiar(self, texto: str) -> str:
        return self.__palabrota.censor(texto)