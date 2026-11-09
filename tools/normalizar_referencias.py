"""Normaliza as referências (ABNT/APA) dos posts do blog para que não quebrem no Hugo.

Uso (rode da raiz do projeto):
  python tools/normalizar_referencias.py            # SÓ MOSTRA o que mudaria (nada é alterado)
  python tools/normalizar_referencias.py --aplicar  # altera os arquivos (guarda cópia .bak ao lado)
  python tools/normalizar_referencias.py --pasta caminho/outra/pasta

Atua nas linhas da lista "fontes:" do cabeçalho de cada content/*/blog/*/index.md
e, se existir, numa seção final "Referências/References/Fontes/Sources" no corpo.
Corrige os padrões que costumam quebrar:
  1. [S.l.], [s.n.], [2020], [...]  -> colchetes escapados (senão o Markdown acha que é link)
  2. URL "solta" (https://...)      -> link clicável [url](url), sem pontuação final dentro do link
  3. <https://...>                  -> link clicável
  4. _ e * dentro de URL            -> protegidos pelo link
  5. ** ou * sem par                -> removidos (negrito/itálico quebrado esconde o resto do texto)
  6. espaços duplos, espaço no fim, "+" solto, marcadores - e * no início da linha dentro de 'fontes'
Não mexe no restante do texto do post.
"""
import re, sys, argparse
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
URL = re.compile(r"(?<![\(\[<\"'])(https?://[^\s<>\)\]\"']+)")

def proteger_links(s, guard=None):
    """separa links markdown já prontos para não mexer neles (os índices continuam numa lista única)"""
    guard = [] if guard is None else guard
    def tira(m): guard.append(m.group(0)); return f"\x00{len(guard)-1}\x00"
    s = re.sub(r"\[[^\]]*\]\([^)]*\)", tira, s)
    return s, guard

def normaliza(linha):
    o = linha
    s = linha.replace(" ", " ")
    s = re.sub(r"<(https?://[^>\s]+)>", r"\1", s)
    s, guard = proteger_links(s)
    # URL solta -> link; pontuação final fica fora
    def link(m):
        u = m.group(1); fim = ""
        while u and u[-1] in ".,;:!?": fim = u[-1] + fim; u = u[:-1]
        return f"[{u}]({u}){fim}"
    s = URL.sub(link, s)
    s, guard = proteger_links(s, guard)  # links criados agora também ficam protegidos (mesma lista de índices)
    # colchetes soltos (ABNT: [S.l.], [s.n.], [2020])
    s = re.sub(r"(?<!\\)\[", r"\\[", s); s = re.sub(r"(?<!\\)\]", r"\\]", s)
    # negrito/itálico sem par
    if s.count("**") % 2: s = s.replace("**", "", 1) if s.count("**") == 1 else s.rsplit("**", 1)[0] + s.rsplit("**", 1)[1]
    t = s.replace("**", "")
    if t.count("*") % 2: s = re.sub(r"(?<!\*)\*(?!\*)", "", s, count=1) if "**" not in s else s
    s = re.sub(r" {2,}", " ", s).strip()
    s = re.sub(r"^(?:[-*+]\s+)+", "", s)
    s = re.sub(r"\x00(\d+)\x00", lambda m: guard[int(m.group(1))], s)
    # links protegidos dentro de links protegidos (criados no 2º passo)
    for _ in range(2): s = re.sub(r"\x00(\d+)\x00", lambda m: guard[int(m.group(1))], s)
    return s

def processa(texto):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", texto, flags=re.S)
    if not m: return texto, []
    fm, corpo = m.group(1), m.group(2)
    mudancas = []
    # 1) lista fontes no cabeçalho
    linhas = fm.split("\n"); out = []; dentro = False
    for l in linhas:
        if re.match(r"^fontes\s*:", l): dentro = True; out.append(l); continue
        if dentro and re.match(r"^\s+-\s", l):
            mk = re.match(r"^(\s+-\s+)(\"?)(.*?)(\"?)\s*$", l)
            pre, aspas, miolo = mk.group(1), mk.group(2), mk.group(3)
            if aspas:  # YAML entre aspas: desescapa, normaliza e reescapa
                bruto = miolo.replace('\\"', '"').replace("\\\\", "\\")
                n = normaliza(bruto)
                novo = pre + '"' + n.replace("\\", "\\\\").replace('"', '\\"') + '"'
            else:
                n = normaliza(miolo)
                novo = pre + '"' + n.replace("\\", "\\\\").replace('"', '\\"') + '"'
            if novo != l: mudancas.append((l, novo))
            out.append(novo); continue
        if dentro and l.strip() and not l.startswith(" "): dentro = False
        out.append(l)
    fm2 = "\n".join(out)
    # 2) seção de referências no corpo (após o último título com esses nomes)
    h = list(re.finditer(r"^#{2,6}\s+(Refer[êe]ncias|References|Fontes|Sources?)\b.*$", corpo, flags=re.M | re.I))
    if h:
        ini = h[-1].end(); novo = []
        for l in corpo[ini:].split("\n"):
            if l.strip() in ("", "+") : novo.append("" if l.strip() == "" else None); continue
            n = normaliza(l) if not l.lstrip().startswith("#") else l
            if n != l: mudancas.append((l, n))
            novo.append(n)
        corpo = corpo[:ini] + "\n".join(x for x in novo if x is not None)
    return f"---\n{fm2}\n---\n{corpo}", mudancas

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--aplicar", action="store_true"); ap.add_argument("--pasta", default=str(RAIZ / "content"))
    a = ap.parse_args(); total = 0
    for md in sorted(Path(a.pasta).glob("**/blog/*/index.md")) or sorted(Path(a.pasta).glob("*.md")):
        txt = md.read_text(encoding="utf8"); novo, mud = processa(txt)
        if not mud: continue
        total += len(mud); print(f"\n== {md.relative_to(a.pasta) if md.is_relative_to(a.pasta) else md}")
        for antes, depois in mud: print(f"  - {antes.strip()}\n  + {depois.strip()}")
        if a.aplicar:
            md.with_suffix(".md.bak").write_text(txt, encoding="utf8"); md.write_text(novo, encoding="utf8")
    print(f"\n{total} linha(s) {'alterada(s)' if a.aplicar else 'seriam alteradas (rode com --aplicar)'}.")
