"""Converte os textos do WordPress (.md) + a planilha em conteúdo do Hugo.
Uso: python tools/migrar_posts.py PASTA_COM_OS_ARQUIVOS
A pasta deve ter: lista_textos_do_blog.xlsx, os post-ID-*.md e as imagens
post-ID-capa-webp.webp e post-ID-original-webp.webp (ID = código do texto em português)."""
import re, sys, json
from pathlib import Path
import yaml, openpyxl
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalizar_referencias import normaliza  # corrige colchetes, URLs soltas e negrito sem par nas referências
RAIZ = Path(__file__).resolve().parent.parent
ENT = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "tools" / "entrada"
IDIOMA = {"PORTUGUÊS": "pt-br", "INGLÊS": "en-us"}
SELO = {"pt-br": "selos", "en-us": "seals"}
ALT = {"cartas taro": ("Cartas de tarô espalhadas sobre papel envelhecido, em estilo de gravura antiga", "Tarot cards spread on aged paper, in the style of an old engraving")}
ORIG = {"Tarô": ("Cartas de tarô usadas para a leitura.", "Tarot cards used for the reading."), "Tarot": ("Cartas de tarô usadas para a leitura.", "Tarot cards used for the reading.")}
PADRAO_ORIG = ("Fotografia que originou a capa deste post.", "Photograph that originated this post's cover.")
CAPA_LEG = ("Capa do post, ilustração criada a partir da fotografia original.", "Post cover, illustration created from the original photograph.")
def fonte_capa(ano): return (f"imagem gerada por IA a partir de fotografia de Iara Lima ({ano})", f"AI-generated image from a photograph by Iara Lima ({ano})")

ws = openpyxl.load_workbook(ENT / "lista_textos_do_blog.xlsx", data_only=True).active
meta = {str(r[0]): r for r in ws.iter_rows(min_row=2, values_only=True) if r[0]}

def q(s): return json.dumps(s, ensure_ascii=False)
for md in sorted(ENT.glob("post-*.md")):
    txt = md.read_text(encoding="utf8")
    _, fm, corpo = re.split(r"^---\s*$", txt, maxsplit=2, flags=re.M)
    fm = yaml.safe_load(fm); pid = str(fm["id"]); r = meta.get(pid)
    if not r: print("SEM LINHA NA PLANILHA:", pid); continue
    lang = IDIOMA[r[4]]; i = 0 if lang == "pt-br" else 1
    chave = pid if lang == "pt-br" else str(int(pid) - 1)
    slug = str(fm["permalink"]).rstrip("/").split("/")[-1]
    corpo = corpo.strip()
    titulo = re.match(r"# (.+)", corpo).group(1).strip(); corpo = corpo[corpo.index("\n"):].strip()
    m = re.search(r"^###\s+(Fonte|Sources?)[^\n]*\n", corpo, flags=re.M | re.I)
    fontes = []
    if m:
        fontes = [re.sub(r"^[-*]\s*", "", l).strip() for l in corpo[m.end():].splitlines() if l.strip() and l.strip() != "+"]
        corpo = corpo[:m.start()].strip()
    corpo = re.sub(r"\*\*([^*\n]+)\*\*(?=[^\s*.,;:!?)])", r"**\1** ", corpo)
    data = str(fm["date"]); ano = data[:4]
    tags = [t.strip() for t in str(r[3]).split(",") if t.strip()]
    for sub in ("capa", "original"):
        src = ENT / f"post-{chave}-{sub}-webp.webp"
        dst = RAIZ / "static/assets/images/blog" / f"{chave}-{sub}.webp"
        if src.exists() and not dst.exists():
            im = Image.open(src).convert("RGB")
            if sub == "capa":
                w, h = im.size; nh = round(w * 3 / 4)
                im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh)) if nh <= h else im
                im = im.resize((1200, 900), Image.LANCZOS)
            else:
                im.thumbnail((800, 800), Image.LANCZOS)
            dst.parent.mkdir(parents=True, exist_ok=True); im.save(dst, "WEBP", quality=80, method=6)
    desc = str(r[5] or "")
    alt = ALT.get(desc, (desc.capitalize(),) * 2)[i]
    ol = ORIG.get(r[2], PADRAO_ORIG)[i]
    img = RAIZ / "static/assets/images/blog"
    out = [ "---", f"title: {q(titulo)}", f"date: {data.replace(' ', 'T')}", f"translationKey: {q(chave)}", f"{SELO[lang]}: [{q(r[2])}]",
            "tags: [" + ", ".join(q(t) for t in tags) + "]" ]
    # capa e imagem original só entram se o arquivo existir; sem imagem, o post sai sem capa (e entra depois)
    if (img / f"{chave}-capa.webp").exists():
        out += [f"cover: /assets/images/blog/{chave}-capa.webp", f"cover_alt: {q(alt)}", f"cover_caption: {q(CAPA_LEG[i])}", f"cover_source: {q(fonte_capa(ano)[i])}"]
    if (img / f"{chave}-original.webp").exists():
        out += [f"original: /assets/images/blog/{chave}-original.webp", f"original_alt: {q(ol)}", f"original_caption: {q(ol)}", f"original_source: {q('Iara Lima (' + ano + ')')}"]
    out += ["bordado: false"]
    if fontes: out += ["fontes:"] + [f"  - {q(normaliza(f))}" for f in fontes]
    out += ["---", "", corpo, ""]
    d = RAIZ / "content" / lang / "blog" / slug; d.mkdir(parents=True, exist_ok=True)
    (d / "index.md").write_text("\n".join(out), encoding="utf8"); print("ok", lang, slug)
