"""Converte textos agendados (post-*.md com date/id/category) em posts do Hugo.
Uso: python tools/migrar_agendados.py PASTA_COM_AS_SUBPASTAS [lista_textos_do_blog.xlsx]
Com a planilha, as tags saem preenchidas (casando título + idioma); sem ela, saem vazias.
Cada subpasta (o nome vira o endereço do post) traz um post-*.md. Os pares PT/EN têm o mesmo id.
Não cria capa: ela entra depois (cover* no cabeçalho do arquivo)."""
import re, sys, json
from pathlib import Path
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalizar_referencias import normaliza
RAIZ = Path(__file__).resolve().parent.parent
ENT = Path(sys.argv[1])
TAGS = {}
if len(sys.argv) > 2:
    import openpyxl
    for r in openpyxl.load_workbook(sys.argv[2], data_only=True).active.iter_rows(min_row=2, values_only=True):
        if r[1] and r[3]:
            lg = "en-us" if str(r[4]).upper().startswith("ING") else "pt-br"
            TAGS[(re.sub(r"\s+", " ", str(r[1]).replace("\u200b", "").replace("\xa0", " ")).strip().lower(), lg)] = [t.strip() for t in str(r[3]).replace("\u200b", "").split(",") if t.strip()]
SELO = {"pt-br": "selos", "en-us": "seals"}
def q(s): return json.dumps(s, ensure_ascii=False)

def idioma(t):
    t = " " + t.lower() + " "
    en = sum(t.count(w) for w in (" the ", " and ", " of ", " is ", " that "))
    pt = sum(t.count(w) for w in (" o ", " de ", " que ", " uma ", " não ", " para "))
    return "en-us" if en > pt else "pt-br"

def descola(s):
    """Reinsere o espaço que o WordPress perdeu ao redor de negrito/itálico: 'de**Alban**,' -> 'de **Alban**,'"""
    def f(m):
        b, a = s[m.start() - 1] if m.start() else " ", s[m.end()] if m.end() < len(s) else " "
        return (" " if b.isalnum() else "") + m.group(0) + (" " if a.isalnum() else "")
    return re.sub(r"(?<![*\\])(\*\*|\*)(?!\s)([^*\n]+?)(?<!\s)\1(?!\*)", f, s)

def amazon(s):
    """Links da Amazon sem parâmetros de rastreio: .../dp/ASIN"""
    return re.sub(r"https://www\.amazon\.com\.br/[^)\s]*?/dp/([A-Z0-9]{10})[^)\s]*", r"https://www.amazon.com.br/dp/\1", s)

for md in sorted(ENT.glob("*/*.md")):
    txt = md.read_text(encoding="utf8")
    m = re.match(r"\A---\s*\n(.*?)---\s*\n", txt, flags=re.S)
    fm = yaml.safe_load(m.group(1)); corpo = txt[m.end():].strip()
    lang = idioma(corpo); key = str(fm["id"])
    slug = re.sub(r"-2$", "", md.parent.name)
    titulo = re.match(r"# (.+)", corpo).group(1).strip(); corpo = corpo[corpo.index("\n"):].strip()
    mf = re.search(r"^###\s+(Fonte|Sources?)[^\n]*\n", corpo, flags=re.M | re.I)
    fontes = []
    if mf:
        fontes = [re.sub(r"^[-*]\s*", "", l).strip() for l in corpo[mf.end():].splitlines() if l.strip() and l.strip() != "+"]
        corpo = corpo[:mf.start()].strip()
    corpo = amazon(descola(corpo)); fontes = [amazon(descola(f)) for f in fontes]
    selo = str(fm["category"][0]).strip()
    tags = TAGS.get((titulo.lower(), lang), [])
    if len(sys.argv) > 2 and not tags: print("  AVISO: sem tags na planilha para", titulo)
    data = str(fm["date"]).replace(" ", "T")
    out = ["---", f"title: {q(titulo)}", f"date: {data}", f"translationKey: {q(key)}", f"{SELO[lang]}: [{q(selo)}]", "tags: [" + ", ".join(q(t) for t in tags) + "]", "bordado: false"]
    if fontes: out += ["fontes:"] + [f"  - {q(normaliza(f))}" for f in fontes]
    out += ["---", "", corpo, ""]
    d = RAIZ / "content" / lang / "blog" / slug; d.mkdir(parents=True, exist_ok=True)
    (d / "index.md").write_text("\n".join(out), encoding="utf8")
    print(f"ok {lang:5} {data} {key} {selo:12} {slug}  (fontes: {len(fontes)}, tags: {len(tags)})")
