import csv
import sys
import re
from pathlib import Path
import mathreader

def main():
    if len(sys.argv) < 2:
        print("Uso: python contador.py <arquivo.csv|arquivo.enw|pasta> [coluna_titulo]")
        sys.exit(1)

    caminho = sys.argv[1]
    coluna_titulo = sys.argv[2] if len(sys.argv) > 2 else "Title"

    titulos = mathreader.ler_titulos_csv(caminho, coluna_titulo)

    for titulo in titulos:
        print(titulo)
        print("-" * 100)

if __name__ == "__main__":
    main()