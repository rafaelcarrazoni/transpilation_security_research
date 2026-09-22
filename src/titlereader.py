import csv
import sys
import re
from pathlib import Path
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


def main():
    if len(sys.argv) < 2:
        print("Uso: python contador.py <arquivo.csv|arquivo.enw|pasta> [coluna_titulo]")
        sys.exit(1)

    caminho = sys.argv[1]
    coluna_titulo = sys.argv[2] if len(sys.argv) > 2 else "Title"

    titulos = mathreader.ler_titulos_csv(caminho, coluna_titulo)

    exibir_titulos(titulos)
    exportar_titulos(titulos)


if __name__ == "__main__":
    main()