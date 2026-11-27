"""Limpieza de textos."""
SIGNOS = ".,;:¿?¡!\"'()-«»"

def palabras(texto):
    """Lista de palabras en minúsculas, sin signos."""
    texto = texto.lower()
    for signo in SIGNOS:
        texto = texto.replace(signo, " ")
    return texto.split()
