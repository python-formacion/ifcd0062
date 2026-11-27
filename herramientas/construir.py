"""Construye la web de recursos del libro a partir de recursos.csv (fuente única).

Genera en site/:
  - una página de redirección por cada código de QR (site/u1-01/index.html, ...),
  - el entorno JupyterLite con los notebooks (site/lab/...),
  - las páginas HTML de recursos (site/recursos/...),
  - un índice (site/index.html).

Con --libro RUTA actualiza además, dentro de libro.tex, el bloque situado entre
«% >>> RECURSOS» y «% <<< RECURSOS» con un \\defrecurso por fila de la tabla.

Uso:  python herramientas/construir.py [--sin-lab] [--libro ../libro/libro.tex]
"""
import argparse, csv, html, re, shutil, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SITE = RAIZ / "site"
BASE = "https://python-formacion.github.io/ifcd0062/"
TIPOS = {"ejecuta": "Ejecuta", "explora": "Explora", "compruebalo": "Comprueba", "actualizado": "Actualizado"}


def leer_tabla():
    with open(RAIZ / "recursos.csv", encoding="utf-8") as f:
        filas = list(csv.DictReader(f, delimiter=";"))
    codigos = set()
    for r in filas:
        assert re.fullmatch(r"u\d+-\d{2}", r["codigo"]), f"Código no válido: {r['codigo']}"
        assert r["codigo"] not in codigos, f"Código repetido: {r['codigo']}"
        assert r["tipo"] in TIPOS, f"Tipo no válido: {r['tipo']}"
        codigos.add(r["codigo"])
    return filas


def redireccion(destino, titulo):
    if not destino.startswith("http"):        # ruta dentro de la web
        destino = "../" + destino
    d, t = html.escape(destino, quote=True), html.escape(titulo)
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<title>{t}</title><meta http-equiv="refresh" content="0; url={d}">
<link rel="canonical" href="{d}"></head>
<body><p>Redirigiendo a <a href="{d}">{t}</a>…</p></body></html>
"""


def construir(filas, con_lab=True):
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    if con_lab:
        subprocess.run([sys.executable, "-m", "jupyter", "lite", "build",
                        "--contents", str(RAIZ / "contenido" / "notebooks"),
                        "--output-dir", str(SITE / "lab")], check=True, cwd=RAIZ)
    shutil.copytree(RAIZ / "contenido" / "recursos", SITE / "recursos")
    (SITE / ".nojekyll").write_text("")
    filas_idx = []
    for r in filas:
        carpeta = SITE / r["codigo"]
        carpeta.mkdir()
        (carpeta / "index.html").write_text(redireccion(r["destino"], r["titulo"]), encoding="utf-8")
        filas_idx.append(f'<li><strong>{r["codigo"].upper()}</strong> · {TIPOS[r["tipo"]]} · '
                         f'<a href="{r["codigo"]}/">{html.escape(r["titulo"])}</a></li>')
    (SITE / "index.html").write_text(f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>IFCD0062 · Recursos del libro</title><link rel="stylesheet" href="recursos/estilo.css"></head>
<body><header><div class="cod">IFCD0062</div><h1>Fundamentos de Programación en Python · Recursos del libro</h1></header>
<main><p>Material complementario del libro: cuadernos que se ejecutan en el navegador o en Google Colab, herramientas
interactivas, tests de autoevaluación y páginas actualizadas. No requiere registro.</p>
<ul>{''.join(filas_idx)}</ul></main></body></html>
""", encoding="utf-8")


def actualizar_libro(filas, ruta):
    tex = Path(ruta).read_text(encoding="utf-8")
    ini, fin = "% >>> RECURSOS", "% <<< RECURSOS"
    assert ini in tex and fin in tex, "Faltan las marcas de bloque en libro.tex"
    lineas = [ini, "% Bloque generado por herramientas/construir.py a partir de recursos.csv. No editar a mano.",
              f"\\renewcommand{{\\urlrecursos}}{{{BASE}}}"]
    for r in filas:
        lineas.append(f"\\defrecurso{{{r['codigo']}}}{{{r['tipo']}}}{{{r['titulo']}}}")
    a, b = tex.index(ini), tex.index(fin)
    Path(ruta).write_text(tex[:a] + "\n".join(lineas) + "\n" + tex[b:], encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sin-lab", action="store_true", help="no construir JupyterLite")
    ap.add_argument("--libro", help="ruta a libro.tex para actualizar el bloque de recursos")
    a = ap.parse_args()
    filas = leer_tabla()
    construir(filas, con_lab=not a.sin_lab)
    if a.libro:
        actualizar_libro(filas, a.libro)
    print(f"{len(filas)} recursos · web en {SITE}")
