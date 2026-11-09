"""Converte os textos "só textuais" (post-AAAAMMDDNN-*.md, exportados do WordPress) em posts do Hugo, SEM capa.
Uso (da raiz do projeto):  python tools/migrar_textuais.py PASTA_COM_OS_ARQUIVOS [PASTA_DE_SAIDA]
Pareamento PT/EN: pela data do nome do arquivo (AAAAMMDD), idioma pelo permalink (/en/ = inglês); não depende do campo id,
que diverge em alguns pares. translationKey = AAAAMMDD01 (id do texto em português). Slug: último trecho do permalink antigo (mantém as URLs antigas)."""
import re, sys, html, json, yaml
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalizar_referencias import normaliza
ENT = Path(sys.argv[1]); SAI = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("saida")
SELO = {"pt-br": "selos", "en-us": "seals"}
q = lambda s: json.dumps(s, ensure_ascii=False)
pares = defaultdict(dict); avisos = []
for f in sorted(ENT.glob("post-*.md")):
    m = re.match(r"post-(\d{8})\d{2}-", f.name)
    fm = yaml.safe_load(re.split(r"^---\s*$", f.read_text(encoding="utf8"), maxsplit=2, flags=re.M)[1])
    lang = "en-us" if "/en/" in str(fm["permalink"]) else "pt-br"   # idioma pelo permalink
    if lang in pares[m.group(1)]: avisos.append(f"DUPLICADO {lang} em {m.group(1)}: {f.name}")
    pares[m.group(1)][lang] = f
def le(f):
    t = f.read_text(encoding="utf8").replace("\r\n", "\n")
    _, fm, corpo = re.split(r"^---\s*$", t, maxsplit=2, flags=re.M)
    return yaml.safe_load(fm), corpo.strip()

def arruma_espacos(txt):
    """A exportação do WordPress removeu espaços em volta de negrito/itálico/links ("de**Lammas**,", "o*Udyat*").
    Recoloca o espaço: antes da abertura e depois do fechamento (sem mexer antes de pontuação)."""
    txt = re.sub(r"\*([.,;:!?])\*", r"\1", txt)                       # *,* e *.* (pontuação "enfatizada" sem texto)
    def span(m):
        ini, d, t, fim = m.start(), m.group(1), m.group(2), m.end()
        pre = txt_ref[ini - 1] if ini > 0 else " "; pos = txt_ref[fim] if fim < len(txt_ref) else " "
        a = " " if (pre not in " \n\t([{“\"‘'—/-" ) else ""
        b = " " if (pos.isalnum() or pos in "([“‘") else ""
        return f"{a}{d}{t}{d}{b}"
    global txt_ref
    out = []
    for linha in txt.split("\n"):
        txt_ref = linha
        out.append(re.sub(r"(?<![*\\])(\*{1,2})(?![\s*])([^*\n]+?)(?<![\s\\])\1(?!\*)", span, linha))
    txt = "\n".join(out)
    txt = re.sub(r"(?<=[\wÀ-ÿ])\[(?!\^)", " [", txt)                  # palavra colada no link: "o[livro](url)"
    txt = re.sub(r"\[ +([^\]]+)\]\(", r" [\1](", txt)               # espaço dentro do texto do link: "[ aqui](url)"
    txt = re.sub(r"\]\(([^)]*)\)(?=[A-Za-zÀ-ÿ0-9])", r"](\1) ", txt) # "(url)palavra"
    txt = re.sub(r"[ \t]{2,}", " ", txt)
    return txt
def converte(f, lang, chave):
    fm, corpo = le(f)
    titulo = html.unescape(re.match(r"# (.+)", corpo).group(1)).strip(); corpo = corpo[corpo.index("\n"):].strip()
    # imagens hospedadas no WordPress antigo (domínio será vendido): saem do texto, ficam anotadas
    imgs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", corpo)
    if imgs: avisos.append(f"{f.name}: {len(imgs)} imagem(ns) do domínio antigo removida(s) do texto: " + ", ".join(Path(i.split('?')[0]).name for i in imgs))
    corpo = re.sub(r"[ \t]*!\[[^\]]*\]\([^)]+\)[ \t]*", "", corpo)
    corpo = re.sub(r"\n{3,}", "\n\n", corpo).strip()
    # seção de fontes: último título ### que começa com Fonte(s)/Source(s)/Souces (com ou sem negrito)
    ms = [x for x in re.finditer(r"^#{2,4}\s+\**\s*(Fonte|Source|Souce)[^\n]*\n", corpo, flags=re.M | re.I)]
    fontes = []
    if ms:
        x = ms[-1]
        for l in corpo[x.end():].splitlines():
            l = l.strip()
            if not l or l == "+": continue
            fontes.append(normaliza(html.unescape(l)))
        corpo = corpo[:x.start()].strip()
    elif lang == "pt-br" or True: avisos.append(f"{f.name}: sem seção de fontes (ok se o texto não tem referências)")
    corpo = arruma_espacos(corpo)
    corpo = html.unescape(corpo) if re.search(r"&#?\w+;", corpo) else corpo
    slug = fm["permalink"].rstrip("/").split("/")[-1]
    selo = fm["category"][0]
    d = str(fm["date"]).replace(" ", "T")
    out = ["---", f"title: {q(titulo)}", f"date: {d}", f"translationKey: {q(chave)}", f"{SELO[lang]}: [{q(selo)}]", "tags: []", "bordado: false"]
    if fontes: out += ["fontes:"] + [f"  - {q(s)}" for s in fontes]
    out += ["---", "", corpo, ""]
    dest = SAI / "content" / lang / "blog" / slug; dest.mkdir(parents=True, exist_ok=True)
    (dest / "index.md").write_text("\n".join(out), encoding="utf8")
    return lang, slug, titulo, d, selo, len(fontes), len(imgs)
tab = []
for dia, d in sorted(pares.items()):
    chave = dia + "01"   # translationKey = id do texto em português
    if set(d) != {"pt-br", "en-us"}: avisos.append(f"par incompleto: {dia} {list(d)}"); continue
    for lang in ("pt-br", "en-us"):
        fm, _ = le(d[lang])
        if str(fm["id"]) != chave: avisos.append(f"{d[lang].name}: campo id={fm['id']} difere do par ({chave}); usei {chave}")
        tab.append((chave,) + converte(d[lang], lang, chave))
print("\n".join(f"{t[0]} {t[1]} {t[2]:<40} {t[4]} {t[5]} fontes={t[6]} imgs={t[7]}" for t in tab))
print("\nAVISOS:"); print("\n".join("- " + a for a in avisos))
