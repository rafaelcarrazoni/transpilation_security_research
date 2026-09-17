import csv
import sys
import re
from pathlib import Path

# na hora de compilar passa o nome do arquivo e a coluna do titulo entre aspas

# ---------------------------------------------------------------------------
# Leitura de CSV (IEEE)
# ---------------------------------------------------------------------------
def ler_titulos_csv(caminho_csv, coluna_titulo="Document Title"):
    """Lê todos os títulos de um CSV exportado da IEEE."""
    caminho = Path(caminho_csv)
    if not caminho.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_csv}")

    titulos = []
    with open(caminho, "r", encoding="utf-8-sig", newline="") as f:
        leitor = csv.DictReader(f)

        if coluna_titulo not in (leitor.fieldnames or []):
            raise KeyError(
                f"Coluna '{coluna_titulo}' não encontrada no CSV. "
                f"Colunas disponíveis: {leitor.fieldnames}"
            )

        for linha in leitor:
            titulo = (linha.get(coluna_titulo) or "").strip()
            if titulo:
                titulos.append(titulo)
    return titulos


# ---------------------------------------------------------------------------
# Leitura de ENW (ACM / EndNote)
# ---------------------------------------------------------------------------
def ler_titulos_enw(caminho_enw):
    """
    Lê todos os títulos (%T) de um arquivo ENW exportado da ACM.
    Cada referência é um bloco separado por linha em branco.
    """
    caminho = Path(caminho_enw)
    if not caminho.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_enw}")

    titulos = []
    titulo_atual = None

    with open(caminho, "r", encoding="utf-8-sig", errors="replace") as f:
        for linha in f:
            linha = linha.rstrip("\n").rstrip("\r")

            # Linha em branco => fim de uma referência
            if not linha.strip():
                if titulo_atual:
                    titulos.append(titulo_atual)
                titulo_atual = None
                continue

            # Campo do ENW: "%X valor" (X é uma letra maiúscula)
            m = re.match(r"^%(\w)\s+(.*)$", linha)
            if m:
                tag, valor = m.group(1), m.group(2).strip()
                if tag == "T":          # %T = Title
                    titulo_atual = valor
                # Ignora outras tags (A, B, D, K, U, etc.)

    # Último bloco caso o arquivo não termine com linha em branco
    if titulo_atual:
        titulos.append(titulo_atual)

    return titulos


def _listar_arquivos_compatíveis(caminho):
    """Resolve um caminho para um arquivo único ou para uma pasta com vários arquivos."""
    caminho = Path(caminho)
    if caminho.is_file():
        return [caminho]

    if caminho.is_dir():
        extensoes = {".csv", ".enw", ".txt"}
        arquivos = [
            arquivo for arquivo in sorted(caminho.rglob("*"))
            if arquivo.is_file() and arquivo.suffix.lower() in extensoes
        ]
        if not arquivos:
            raise FileNotFoundError(f"Nenhum arquivo compatível encontrado em: {caminho}")
        return arquivos

    raise FileNotFoundError(f"Arquivo ou pasta não encontrado: {caminho}")


# ---------------------------------------------------------------------------
# Detecção automática de formato
# ---------------------------------------------------------------------------
def ler_titulos(caminho, coluna_titulo="Document Title"):
    """Detecta o formato pelo sufixo e delega para o leitor adequado."""
    arquivos = _listar_arquivos_compatíveis(caminho)
    titulos = []

    for arquivo in arquivos:
        sufixo = arquivo.suffix.lower()
        try:
            if sufixo in (".enw", ".enw.txt"):
                titulos.extend(ler_titulos_enw(arquivo))
            elif sufixo in (".csv", ".txt"):
                titulos.extend(ler_titulos_csv(arquivo, coluna_titulo))
            else:
                try:
                    titulos.extend(ler_titulos_csv(arquivo, coluna_titulo))
                except Exception:
                    titulos.extend(ler_titulos_enw(arquivo))
        except (FileNotFoundError, KeyError):
            continue

    titulos_sem_repeticao = list(dict.fromkeys(t.strip() for t in titulos if t and t.strip()))
    return titulos_sem_repeticao


# ---------------------------------------------------------------------------
# Comparação
# ---------------------------------------------------------------------------
def _normalizar(txt):
    """Normaliza para comparação: minúsculas, espaços e pontuação colapsados."""
    txt = txt.lower().strip()
    # remove pontuação comum que varia entre exportações
    txt = re.sub(r"[^\w\s]", " ", txt)
    txt = re.sub(r"\s+", " ", txt)
    return txt


def contar_artigos(caminho, artigos, coluna_titulo="Document Title"):
    """
    Conta quantos artigos do vetor estão no arquivo (IEEE CSV ou ACM ENW).
    Retorna um dicionário com o resultado.
    """
    titulos_arquivo = ler_titulos(caminho, coluna_titulo)

    # Mapa normalizado -> título original do vetor
    artigos_norm = {}
    for a in artigos:
        a = a.strip()
        if a:
            artigos_norm[_normalizar(a)] = a

    titulos_norm = {_normalizar(t) for t in titulos_arquivo if t.strip()}

    encontrados = []
    nao_encontrados = []

    for norm, original in artigos_norm.items():
        if norm in titulos_norm:
            encontrados.append(original)
        else:
            nao_encontrados.append(original)

    return {
        "encontrados": encontrados,
        "nao_encontrados": sorted(nao_encontrados),
        "total_encontrados": len(encontrados),
        "total_nao_encontrados": len(nao_encontrados),
        "total": len(artigos_norm),
        "total_no_arquivo": len(titulos_arquivo),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Uso: python contador.py <arquivo.csv|arquivo.enw|pasta> [coluna_titulo]")
        sys.exit(1)

    caminho = sys.argv[1]
    coluna_titulo = sys.argv[2] if len(sys.argv) > 2 else "Document Title"

    artigos = [
        "Translating C to safer Rust",
        "Security Risks of Transpiling C Programs to Rust",
        "When Code Crosses Borders: A Security-Centric Study of LLM-based Code Translation",
        "SafeTrans: LLM-assisted Transpilation from C to Rust",
        "Cpp2Rust: Automatic Translation of C++ to Safe Rust",
        "Mostly Automatic Translation of Language Interpreters from C to Safe Rust",
    ]

    try:
        resultado = contar_artigos(caminho, artigos, coluna_titulo)
    except (FileNotFoundError, KeyError) as e:
        print(f"Erro: {e}")
        sys.exit(1)

    print("\n=== Resultado ===")
    print(f"Arquivo analisado:         {caminho}")
    print(f"Títulos no arquivo:        {resultado['total_no_arquivo']}")
    print(f"Total de artigos no vetor: {resultado['total']}")
    print(f"Encontrados no arquivo:    {resultado['total_encontrados']}")
    print(f"Não encontrados:           {resultado['total_nao_encontrados']}\n")

    if resultado["encontrados"]:
        print("✓ Encontrados:")
        for t in resultado["encontrados"]:
            print(f"   - {t}")

    if resultado["nao_encontrados"]:
        print("\n✗ Não encontrados:")
        for t in resultado["nao_encontrados"]:
            print(f"   - {t}")


if __name__ == "__main__":
    main()