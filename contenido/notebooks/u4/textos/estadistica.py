"""Recuentos de palabras."""

def frecuencias(lista):
    """Diccionario palabra -> número de apariciones."""
    conteo = {}
    for p in lista:
        conteo[p] = conteo.get(p, 0) + 1
    return conteo

def mas_frecuentes(conteo, n=10, minimo=1):
    """Las n palabras más frecuentes de al menos `minimo` letras."""
    pares = [(p, c) for p, c in conteo.items() if len(p) >= minimo]
    return sorted(pares, key=lambda par: par[1], reverse=True)[:n]
