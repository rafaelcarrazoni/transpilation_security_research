from pathlib import Path

from src import titlereader


def test_ler_todos_artigos_exportados_ignora_arquivos_bugs(tmp_path):
    pasta_exports = tmp_path / "exports"
    pasta_exports.mkdir()

    (pasta_exports / "ieee.csv").write_text(
        "Document Title\nPrimeiro artigo\nSegundo artigo\nPrimeiro artigo\n",
        encoding="utf-8",
    )
    (pasta_exports / "ieee_bugs.csv").write_text(
        "Document Title\nArtigo de teste bug\n",
        encoding="utf-8",
    )
    (pasta_exports / "acm.enw").write_text(
        "%T Segundo artigo\n\n%T Terceiro artigo\n",
        encoding="utf-8",
    )
    (pasta_exports / "scopus.csv").write_text(
        "Title\nQuarto artigo\nSegundo artigo\n",
        encoding="utf-8",
    )
    (pasta_exports / "springer.csv").write_text(
        "Item Title\nQuinto artigo\n",
        encoding="utf-8",
    )
    (pasta_exports / "springer_bugs.csv").write_text(
        "Document Title\nArtigo de teste bug 2\n",
        encoding="utf-8",
    )

    resultado = titlereader.ler_todos_artigos_exportados(pasta_exports)

    assert set(resultado["artigos"]) == {"Primeiro artigo", "Segundo artigo", "Terceiro artigo", "Quarto artigo", "Quinto artigo"}
    assert len(resultado["artigos"]) == 5
    assert resultado["total_artigos_unicos"] == 5
