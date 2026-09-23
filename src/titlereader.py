import csv
import sys
import re
from pathlib import Path

try:
    from . import mathreader
except ImportError:  # pragma: no cover - suporte para execução direta do script
    import mathreader


def exibir_titulos(titulos):
    """Exibe todos os títulos formatados no terminal."""
    for titulo in titulos:
        print(titulo)
        print("-" * 100)


def exportar_titulos(titulos, arquivo_saida="titulos_exportados.txt"):
    """Exporta todos os títulos para um arquivo de texto."""
    try:
        with open(arquivo_saida, "w", encoding="utf-8") as f:
            for titulo in titulos:
                f.write(f"{titulo}\n")
                f.write("-" * 100 + "\n")
        print(f"\nTítulos exportados com sucesso para: {arquivo_saida}")
    except IOError as e:
        print(f"Erro ao exportar títulos: {e}")
        sys.exit(1)


def _listar_arquivos_export_validos(caminho_exports, extensoes=None):
    """Lista arquivos de exportação excluindo os nomes que terminam com '_bugs'."""
    caminho = Path(caminho_exports)
    extensoes = extensoes or {".csv", ".enw", ".txt"}

    if caminho.is_file():
        arquivos = [caminho]
    elif caminho.is_dir():
        arquivos = [
            arquivo for arquivo in sorted(caminho.rglob("*"))
            if arquivo.is_file() and arquivo.suffix.lower() in extensoes
        ]
    else:
        raise FileNotFoundError(f"Arquivo ou pasta não encontrado: {caminho_exports}")

    arquivos_validos = []
    for arquivo in arquivos:
        nome = arquivo.name.lower()
        if any(nome.endswith(f"_bugs{ext}") for ext in sorted(extensoes)):
            continue
        arquivos_validos.append(arquivo)

    return arquivos_validos


def ler_todos_artigos_exportados(caminho_exports="exports", coluna_titulo=None):
    """Lê todos os artigos dos exports válidos, sem repetir títulos e retorna a contagem."""
    arquivos = _listar_arquivos_export_validos(caminho_exports)
    titulos = []

    for arquivo in arquivos:
        try:
            titulos.extend(mathreader.ler_titulos(arquivo, coluna_titulo))
        except (FileNotFoundError, KeyError):
            continue

    artigos_unicos = list(dict.fromkeys(titulo.strip() for titulo in titulos if titulo and titulo.strip()))
    return {
        "artigos": artigos_unicos,
        "total_artigos_unicos": len(artigos_unicos),
    }


def main():
    resultado = ler_todos_artigos_exportados()

    with open("tunicos_encontrados.txt", "w") as arquivo:
        for artigo in resultado["artigos"]:
            arquivo.write(f"{artigo} \n")


if __name__ == "__main__":
    main()