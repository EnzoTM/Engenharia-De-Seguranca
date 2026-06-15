#!/usr/bin/env python3
"""Converte um arquivo Markdown em PDF.

Uso basico:
    python3 md2pdf.py relatorio.md
    python3 md2pdf.py relatorio.md -o saida.pdf

Opcoes:
    -o/--output     Caminho do PDF de saida (padrao: mesmo nome do .md).
    --paper         Tamanho da pagina: a4, letter, etc. (padrao: a4).
    --margin        Margem em pontos (padrao: 50).
    --font          Familia de fonte CSS (padrao: sans-serif).
    --font-size     Tamanho da fonte do corpo em pt (padrao: 10.5).
    --accent        Cor dos titulos e negritos, ex.: "#000000" ou "#0a1f44"
                    (padrao: #000000, preto).

Dependencias:
    pip3 install --index-url https://pypi.org/simple/ markdown pymupdf
"""

import argparse
import os
import sys

import markdown
import fitz


def build_css(font, font_size, accent):
    return f"""
* {{ font-family: {font}; }}
body {{ font-size: {font_size}pt; color: #000000; line-height: 1.5; }}
h1 {{ font-size: 19pt; color: {accent}; margin: 0 0 6pt 0; line-height: 1.25; }}
h2 {{ font-size: 14pt; color: {accent}; margin: 16pt 0 5pt 0; }}
h3 {{ font-size: 11.5pt; color: {accent}; margin: 11pt 0 3pt 0; }}
p  {{ margin: 0 0 7pt 0; text-align: justify; }}
ul {{ margin: 0 0 8pt 0; }}
li {{ margin: 0 0 3pt 0; text-align: justify; }}
strong {{ color: {accent}; }}
a {{ color: #1a56db; font-weight: bold; }}
hr {{ border: none; border-top: 1px solid #cccccc; margin: 10pt 0; }}
pre {{ border-left: 3pt solid #c4ccd6; padding: 0 0 0 9pt; margin: 0 0 8pt 0; }}
code {{ font-family: monospace; }}
table {{ border-collapse: collapse; margin: 0 0 8pt 0; }}
th, td {{ border: 1px solid #999999; padding: 3pt 6pt; text-align: left; }}
th {{ font-weight: bold; }}
"""


def md_to_pdf(src, out, paper="a4", margin=50, font="sans-serif",
              font_size=10.5, accent="#000000"):
    with open(src, "r", encoding="utf-8") as f:
        md_text = f.read()

    html_body = markdown.markdown(
        md_text,
        extensions=["extra", "sane_lists", "toc"],
    )

    css = build_css(font, font_size, accent)

    page_rect = fitz.paper_rect(paper)
    content = fitz.Rect(
        margin, margin,
        page_rect.width - margin, page_rect.height - margin,
    )

    story = fitz.Story(html=html_body, user_css=css)
    writer = fitz.DocumentWriter(out)

    pages = 0
    more = 1
    while more:
        device = writer.begin_page(page_rect)
        more, _ = story.place(content)
        story.draw(device)
        writer.end_page()
        pages += 1

    writer.close()
    return pages


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Converte um arquivo Markdown em PDF.",
    )
    parser.add_argument("input", help="Arquivo Markdown de entrada (.md).")
    parser.add_argument(
        "-o", "--output",
        help="PDF de saida (padrao: mesmo nome do .md com extensao .pdf).",
    )
    parser.add_argument("--paper", default="a4",
                        help="Tamanho da pagina (padrao: a4).")
    parser.add_argument("--margin", type=float, default=50,
                        help="Margem em pontos (padrao: 50).")
    parser.add_argument("--font", default="sans-serif",
                        help="Familia de fonte CSS (padrao: sans-serif).")
    parser.add_argument("--font-size", type=float, default=10.5,
                        help="Tamanho da fonte do corpo em pt (padrao: 10.5).")
    parser.add_argument("--accent", default="#000000",
                        help="Cor de titulos e negritos (padrao: #000000).")
    args = parser.parse_args(argv)

    output = args.output or (os.path.splitext(args.input)[0] + ".pdf")

    pages = md_to_pdf(
        args.input, output,
        paper=args.paper, margin=args.margin, font=args.font,
        font_size=args.font_size, accent=args.accent,
    )
    print(f"Saved: {output} pages: {pages}")


if __name__ == "__main__":
    sys.exit(main())
