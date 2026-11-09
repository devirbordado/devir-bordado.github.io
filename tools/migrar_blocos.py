"""Converte posts exportados do WordPress que têm elementos especiais: mural de fotos, vídeo do YouTube, tabela
e textos do Word (PT e EN no mesmo arquivo).
Uso (da raiz do projeto):  python tools/migrar_blocos.py PASTA_COM_AS_4_PASTAS [PASTA_DE_SAIDA]
A pasta de entrada deve conter (em qualquer profundidade) os .md, .webp do mural e os .docx.
Escreve content/<idioma>/blog/<slug>/index.md e static/assets/images/blog/…  na pasta de saída."""
import re, sys, json, html, shutil, subprocess, tempfile, unicodedata
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalizar_referencias import normaliza
ENT = Path(sys.argv[1]); SAI = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("saida")
RAIZ = Path(__file__).resolve().parent.parent
q = lambda s: json.dumps(s, ensure_ascii=False)
SELO = {"pt-br": "selos", "en-us": "seals"}
avisos = []
def aviso(m): avisos.append(m)

# ---------- configuração editorial (mural, selos dos textos do Word) ----------
# ordem = ordem das fotos no mural (a 1ª é a maior); "n" = número da imagem original (1 a 5)
MURAL = {
 "2026091001": {"pref": "post-202609100", "legenda": {"pt-br": "Fonte: reddit. Imagens: Zentralschaden e dylanjames.", "en-us": "Source: reddit. Images: Zentralschaden and dylanjames."},
   "fotos": [
    (1, "Placa de circuito verde com uma matriz quadrada de minúsculos núcleos magnéticos no centro, cercada por fios dourados.", "Green circuit board with a square matrix of tiny magnetic cores in the middle, surrounded by golden wires.", None),
    (2, "Malha de núcleos de ferrite pretos entrelaçados por fios de cobre, como uma trama.", "Mesh of black ferrite cores interlaced with copper wires, like a weave.", None),
    (3, "Close de anéis laranja atravessados por fios vermelhos, dispostos em fileiras.", "Close-up of orange rings threaded with red wires, arranged in rows.", None),
    (4, "Close de núcleos laranja e peças brancas com feixes de fios vermelhos sobre uma placa.", "Close-up of orange cores and white pieces with bundles of red wires on a board.", None),
    (5, "Módulo de memória de núcleos magnéticos visto de cima, com blocos de fios vermelhos e componentes eletrônicos.", "Magnetic-core memory module seen from above, with blocks of red wires and electronic components.", None)]},
 "2026091701": {"pref": "post-2026091701", "legenda": {"pt-br": "Fonte e fotos: Music Center.", "en-us": "Source and photos: Music Center."},
   "fotos": [
    (1, "Guitarra elétrica preta com padrão floral dourado e vermelho, deitada em um estojo forrado de vermelho.", "Black electric guitar with a gold and red floral pattern, lying in a red-lined case.", "35% 45%"),
    (3, "Close do corpo da guitarra com estampa floral e folhas douradas e vermelhas sobre fundo preto, com ponte e botões à mostra.", "Close-up of the guitar body with a floral print and gold and red leaves on a black background, bridge and knobs in view.", None),
    (5, "Guitarra em pé em um canto, junto a uma parede de madeira, mostrando o padrão floral.", "Guitar standing in a corner next to a wooden wall, showing the floral pattern.", "50% 30%"),
    (2, "Guitarra Ibanez aberta no estojo rígido de forro vermelho, com manual e acessórios ao lado.", "Ibanez guitar in its open hard case with red lining, with a manual and accessories beside it.", None),
    (4, "Guitarra vista de cima, com incrustações em forma de árvore no braço, sobre uma superfície de madeira clara.", "Guitar seen from above, with tree-shaped inlays on the neck, on a light wooden surface.", "50% 25%")]},
 "2026110801": {"pref": "post-2026110801", "legenda": {"pt-br": "Imagens: Ahmed Amin/Egypt Ministry of Tourism and Antiquities.", "en-us": "Images: Ahmed Amin/Egypt Ministry of Tourism and Antiquities."},
   "fotos": [
    (3, "Relevo pintado de duas figuras oferecendo vasos, uma delas com corpo de serpente, ao lado de colunas de hieróglifos.", "Painted relief of two figures offering vessels, one with a serpent's body, beside columns of hieroglyphs.", None),
    (1, "Colunas do templo com capitéis em forma de papiro pintados, hieróglifos ao fundo e andaimes.", "Temple columns with painted papyrus-shaped capitals, hieroglyphs in the background and scaffolding.", None),
    (2, "Relevo de um escorpião entalhado, com fileiras de estrelas acima.", "Relief of a carved scorpion, with rows of stars above it.", None),
    (4, "Teto do templo com aves de asas abertas pintadas em azul e faixas de hieróglifos coloridos.", "Temple ceiling with blue-painted birds with open wings and bands of colorful hieroglyphs.", None),
    (5, "Vista de baixo para cima de capitéis florais coloridos e faixas de hieróglifos no teto.", "View from below of colorful floral capitals and bands of hieroglyphs on the ceiling.", None)]},
}
# selo dos textos do Word (o arquivo não traz categoria): chave = trecho do nome do arquivo
WORD_SELO = {"taro": ("Tarô", "Tarot"), "feito_a_mao": ("Entrelinhas", "Overtone"), "Para_onde": ("Meraki", "Meraki"), "boas_lonjuras": ("Meraki", "Meraki")}
WORD_SLUG = {  # (pt, en)
 "taro_parte_1": ("ensinando-taro-versao-fofoca-parte-1", "teaching-tarot-gossip-version-part-1"), "taro_parte_2": ("ensinando-taro-versao-fofoca-parte-2", "teaching-tarot-gossip-version-part-2"),
 "taro_parte_3": ("ensinando-taro-versao-fofoca-parte-3", "teaching-tarot-gossip-version-part-3"), "taro_parte_4": ("ensinando-taro-versao-fofoca-parte-4", "teaching-tarot-gossip-version-part-4"),
 "feito_a_mao": ("feito-a-mao-e-marketing", "handmade-and-marketing"), "Para_onde": ("para-onde-este-blog-esta-caminhando", "where-is-this-blog-heading"), "boas_lonjuras": ("boas-lonjuras", "fairfarren")}
BOAS_ALT = {"pt-br": "Bordado de um coração anatômico vermelho do qual brotam galhos de árvore com folhas verdes, em bastidor de madeira escura segurado diante de folhagem.", "en-us": "Embroidery of a red anatomical heart from which tree branches with green leaves grow, in a dark wooden hoop held up against foliage."}

# ---------- utilitários de texto ----------
def slugify(s): return re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()).strip("-")
PT_W = set("o a os as de do da dos das que não um uma para com por mais mas como se em é foi são ao na no nas nos você ele ela isso essa esse eu minha meu muito já também quando".split())
EN_W = set("the of and to in is that it for with as was on are this be by at an or from but not you have his her they we what when which their been".split())
def idioma(txt):
    w = re.findall(r"[a-záéíóúâêôãõç']+", txt.lower()); p = sum(x in PT_W for x in w); e = sum(x in EN_W for x in w)
    return "pt-br" if p >= e else "en-us"
def _linha_enfase(ln):
    """Pareia os * / ** / *** da linha em ordem (abre, fecha) e arruma os espaços: nada de espaço dentro da marcação
    ("** palavra**", "**palavra **") e um espaço fora quando a palavra vizinha está colada ("de**Lammas**,")."""
    ini = 0
    m0 = re.match(r"\s*(?:[-+*]|\d+[.)])\s+", ln)
    if m0: ini = m0.end()
    runs = [m for m in re.finditer(r"(?<![\\*])\*{1,3}(?!\*)", ln) if m.start() >= ini]
    pilha, pares = [], []
    for m in runs:
        if pilha and pilha[-1].group() == m.group(): pares.append((pilha.pop(), m))
        else: pilha.append(m)
    if pilha or not pares: return ln, bool(pilha)
    abre = {a.start(): a for a, _ in pares}; fecha = {b.start(): b for _, b in pares}
    out = []; i = 0
    while i < len(ln):
        if i in abre:
            m = abre[i]; k = m.end()
            while k < len(ln) and ln[k] in " \t": k += 1
            pre = out[-1] if out else " "
            if pre not in " \t([{“\"‘'—/-|": out.append(" ")
            out.append(m.group()); i = k; continue
        if i in fecha:
            m = fecha[i]
            while out and out[-1] in " \t": out.pop()
            out.append(m.group()); i = m.end()
            pos = ln[i] if i < len(ln) else " "
            if pos.isalnum() or pos in "([“‘": out.append(" ")
            continue
        out.append(ln[i]); i += 1
    return "".join(out), False
def arruma_espacos(txt):
    """Recoloca espaços em volta de negrito/itálico/links que a exportação do WordPress removeu."""
    txt = re.sub(r"\*([.,;:!?])\*", r"\1", txt)
    L = []
    for ln in txt.split("\n"):
        novo, desbalanceada = _linha_enfase(ln)
        if desbalanceada and len(re.findall(r"(?<![\\*])\*{1,3}(?!\*)", ln)) > 1: aviso("marcação * ou ** sem par numa linha (confira no site): " + ln[:90])
        L.append(novo)
    txt = "\n".join(L)
    txt = re.sub(r"(?<=[\wÀ-ÿ])\[(?!\^)", " [", txt); txt = re.sub(r"\[ +([^\]]+)\]\(", r" [\1](", txt)
    txt = re.sub(r"\]\(([^)]*)\)(?=[A-Za-zÀ-ÿ0-9])", r"](\1) ", txt)
    return re.sub(r"(?<=\S)[ \t]{2,}(?=\S)", " ", txt)   # só espaços duplos no meio da linha; os do fim (quebra de linha) ficam
def conserta_links(s):
    s = re.sub(r"\[([^\]]+)\]\s+\((https?://[^)\s]+)\)", r"[\1](\2)", s)                         # "[aqui] (url)"
    s = re.sub(r"(?<![\[\w])(here|aqui|Here|Aqui)\]\((https?://)", r"[\1](\2", s)                 # "here](url)" sem "["
    return s
def limpa_inv(s): return s.replace("​", "").replace("﻿", "").replace(" ", " ")

def parte_fontes(corpo):
    """Separa a seção de fontes (último título curto com 'Fontes/Sources' que tenha lista depois)."""
    L = corpo.split("\n"); ach = None
    for i, l in enumerate(L):
        t = re.sub(r"[#*\[\]_⤵️]|\{\.underline\}", "", l).strip()
        if t and len(t) < 90 and i > len(L) * 0.45 and re.match(r"^(Fontes?|Sources?|Souces?|Nada de esconder as fontes)\b", t, re.I) and not t.endswith(".") : ach = i
    if ach is None: return corpo, [], None
    itens = []
    for l in L[ach + 1:]:
        l = l.strip()
        if not l or l == "+": continue
        l = re.sub(r"^(?:[-•*]\s+|•\t)+", "", l).strip()
        if re.fullmatch(r"\*\*(.+)\*\*", l, re.S): l = l[2:-2].strip()
        itens.append(l)
    return "\n".join(L[:ach]).strip(), itens, L[ach].strip()
def links_internos(s, lang, slugs):
    def r(m):
        en, sl = bool(m.group(1)), m.group(2).strip("/")
        alvo = ("en-us" if en else "pt-br")
        if sl in slugs.get(alvo, set()): return f"(/{alvo}/blog/{sl}/)"
        aviso(f"link para aiaralima.com sem post correspondente: {m.group(0)}"); return m.group(0)
    return re.sub(r"\(https?://(?:www\.)?aiaralima\.com/(en/)?([^)\s]+?)/?\)", r, s)
def quebra_paragrafos(corpo):
    """Linhas coladas: versos (linhas curtas) ganham quebra de linha; parágrafos longos viram parágrafos separados."""
    L = corpo.split("\n"); out = []; i = 0
    ehbloco = lambda x: x.strip() and not x.lstrip().startswith(("|", "-", "•", "#", ">", "!")) and not re.match(r"\s*\d+[.)]\s", x) and not x.startswith("    ")
    while i < len(L):
        if ehbloco(L[i]):
            j = i
            while j + 1 < len(L) and ehbloco(L[j + 1]): j += 1
            blk = L[i:j + 1]
            if len(blk) > 1:
                media = sum(len(x) for x in blk) / len(blk)
                if media < 90 or all(x.rstrip().endswith("\\") for x in blk[:-1]): blk = [x.rstrip("\\ ").rstrip() + ("  " if k < len(blk) - 1 else "") for k, x in enumerate(blk)]; out += blk
                else: out += ["\n".join([]) or ""] and [y for x in blk for y in (x, "")][:-1]
            else: out += blk
            i = j + 1
        else: out.append(L[i]); i += 1
    t = "\n".join(out)
    return re.sub(r"(?m)^(\d+[.)] .*[^ \n])\n(    +\S)", r"\1  \n\2", t)    # continuação indentada em listas numeradas: quebra de linha

# ---------- coleta ----------
posts = []   # dicts: lang, date8, fm(dict), corpo
def le_md(f):
    t = limpa_inv(f.read_text(encoding="utf8").replace("\r\n", "\n")); _, fm, corpo = re.split(r"^---\s*$", t, maxsplit=2, flags=re.M)
    d = {}
    for k in ("date", "slug", "id", "permalink"):
        m = re.search(rf"^{k}:\s*['\"]?(.*?)['\"]?\s*$", fm, re.M); d[k] = m.group(1) if m else None
    m = re.search(r"^tags?:\s*(.*)$", fm, re.M); raw = (m.group(1) if m else "").strip()
    tags = [re.sub(r'^["\']|["\']$', "", x.strip()).strip() for x in re.sub(r"^\[|\]$", "", raw).split(",")]
    d["tags"] = [x for x in tags if x and "inserir" not in x.lower()]
    m = re.search(r"^category:\s*\n\s*-\s*(.+)$", fm, re.M) or re.search(r"^\s+-\s+(\w+)\s*$", fm, re.M)   # 2º caso: arquivo sem a linha "category:"
    d["selo"] = m.group(1).strip() if m else None
    return d, corpo.strip()
for f in sorted(ENT.rglob("post-*.md")):
    t0 = limpa_inv(f.read_text(encoding="utf8").replace("\r\n", "\n")); fm0, corpo0 = re.split(r"^---\s*$", t0, maxsplit=2, flags=re.M)[1:]
    if re.search(r"^title:", fm0, re.M):   # já está no formato do Hugo (capa, selo, tags…): só entra o vídeo
        mt = re.search(r"^title:\s*(.*)$", fm0, re.M); tit = json.loads(mt.group(1)) if mt.group(1).startswith('"') else mt.group(1)
        slug = re.sub(r"^post-\d{10}\s*-?\s*", "", f.stem).strip("- ")
        posts.append(dict(lang="en-us" if re.search(r"^seals:", fm0, re.M) else "pt-br", date8=re.match(r"post-(\d{8})", f.name).group(1), fm=dict(slug=slug, permalink=None), corpo=corpo0.strip(), fmraw=fm0.strip("\n"), arq=f.name, kind="pronto", titulo=tit))
        continue
    d, corpo = le_md(f); lang = "en-us" if "/en/" in str(d.get("permalink") or "") else idioma(corpo)
    posts.append(dict(lang=lang, date8=re.match(r"post-(\d{8})", f.name).group(1), fm=d, corpo=corpo, arq=f.name, kind="md", titulo=html.unescape(re.match(r"# (.+)", corpo).group(1)).strip()))
# Word: pt + en no mesmo arquivo
tmp = Path(tempfile.mkdtemp())
for f in sorted(ENT.rglob("*.docx")):
    nome = re.sub(r"[^A-Za-z0-9._-]", "_", f.name); chave = next(k for k in WORD_SLUG if k in nome)
    md = tmp / (nome + ".md"); subprocess.run(["pandoc", str(f), "-f", "docx", "-t", "markdown-smart", "--wrap=none", f"--extract-media={tmp / nome}", "-o", str(md)], check=True)
    t = limpa_inv(md.read_text(encoding="utf8")); y, m_, d_ = re.match(r"(\d{4})\.(\d\d)\.(\d\d)", f.name).groups()
    partes = re.split(r"\n\\_(?:\\_)+-?\s*\n", t); assert len(partes) == 2, (f.name, len(partes))
    for lang, p in zip(("pt-br", "en-us"), partes):
        L = [l for l in p.strip().split("\n")]
        tit = re.sub(r"^\*\*|\*\*$", "", L[0].strip()).strip(); i = 1
        while i < len(L) and (not L[i].strip() or re.match(r"^\**\s*(\d{1,2} de [\wç]+ de \d{4}|\d+[–-]\d+ (minutos|minutes))\**\s*$", L[i].strip())): i += 1
        corpo = "\n".join(L[i:]).strip()
        ne = [x for x in corpo.split("\n") if x.strip() and not x.startswith(("-", "#", "!", "\\"))]
        if ne and sum(bool(re.fullmatch(r"\*\*.+\*\*", x.strip())) for x in ne) / len(ne) > .6:   # documento inteiro em negrito: remove o negrito
            corpo = re.sub(r"\*\*", "", corpo); aviso(f"{f.name} ({lang}): o texto inteiro estava em negrito no Word; o negrito foi removido")
        corpo = re.sub(r"\[([^\]]+)\]\{\.underline\}", r"\1", corpo)
        sel = next(v for k, v in WORD_SELO.items() if k in nome)[0 if lang == "pt-br" else 1]
        img = None
        mi = re.search(r"!\[\]\(([^)]*media/[^)]+)\)(\{[^}]*\})?", corpo)
        if mi: img = Path(mi.group(1)); corpo = corpo.replace(mi.group(0), "@@IMG@@")
        posts.append(dict(lang=lang, date8=y + m_ + d_, fm=dict(date=f"{y}-{m_}-{d_}T07:5{0 if lang=='pt-br' else 1}:00", slug=WORD_SLUG[chave][0 if lang == "pt-br" else 1], id=None, permalink=None, tags=[], selo=sel, titulo=tit), corpo=corpo, arq=f.name, kind="docx", img=img, titulo=tit))
tit_re = lambda c: re.match(r"# (.+)", c)
slugs_existentes = {"pt-br": set(), "en-us": set()}
for lg, cam in (("pt-br", "content/pt-br/blog"), ("en-us", "content/en-us/blog")):
    for base in (RAIZ / cam, RAIZ.parent / "saida" / cam, RAIZ.parent / "saida2" / cam):
        if base.exists(): slugs_existentes[lg] |= {p.name for p in base.iterdir() if p.is_dir()}

# ---------- pareamento e escrita ----------
grupos = defaultdict(dict)
for p in posts:
    if p["lang"] in grupos[p["date8"]]: aviso(f"IDIOMA REPETIDO em {p['date8']}: {p['arq']} e {grupos[p['date8']][p['lang']]['arq']}")
    grupos[p["date8"]][p["lang"]] = p
for dia, g in grupos.items():
    if set(g) != {"pt-br", "en-us"}: aviso(f"par incompleto em {dia}: {list(g)}")
def slug_de(p, outro):
    fm = p["fm"]; s = (str(fm["permalink"]).rstrip("/").split("/")[-1] if fm.get("permalink") else None) or fm.get("slug")
    if not s: s = slugify(p["titulo"])
    if outro and outro["fm"].get("slug"):
        a, b = s, outro["fm"]["slug"]
        if re.sub(r"-\d$", "", a) == re.sub(r"-\d$", "", b) and a != b: s = re.sub(r"-\d$", "", a); aviso(f"slug '{a}' e '{b}' viraram '{s}' (um por idioma)")
    return s
for p in posts:
    outro = grupos[p["date8"]].get("en-us" if p["lang"] == "pt-br" else "pt-br")
    p["slug"] = slug_de(p, outro); slugs_existentes[p["lang"]].add(p["slug"])
resumo = []
def escreve_pronto(p):
    """Post que ela já formatou: mantém o cabeçalho, conserta as aspas das fontes (\\[ inválido em YAML) e põe o vídeo no fim."""
    lang, corpo = p["lang"], conserta_links(p["corpo"])
    L = p["fmraw"].split("\n"); out = []; i = 0
    while i < len(L):
        if L[i].startswith("fontes:"):
            out.append("fontes:"); i += 1
            while i < len(L) and re.match(r"^\s+-\s", L[i]):
                raw = re.sub(r'^\s+-\s+"?|"?\s*$', "", L[i]); raw = html.unescape(conserta_links(raw)); out.append("  - " + q(normaliza(raw))); i += 1
            continue
        out.append(L[i]); i += 1
    yts = re.findall(r"^\s*https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})\S*\s*$", corpo, re.M)
    corpo = re.sub(r"^\s*https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w-]{11}\S*\s*$", "", corpo, flags=re.M).strip()
    corpo = links_internos(corpo, lang, slugs_existentes)
    if yts: corpo += "\n\n" + "\n\n".join("{{< youtube id=" + q(y) + " titulo=" + q(p["titulo"]) + " >}}" for y in yts)
    d = SAI / "content" / lang / "blog" / p["slug"]; d.mkdir(parents=True, exist_ok=True)
    (d / "index.md").write_text("---\n" + "\n".join(out) + "\n---\n\n" + corpo + "\n", encoding="utf8")
    resumo.append((p["date8"] + "01", lang, p["slug"], "(já formatado)", sum(1 for x in out if x.startswith("  - ")), "", "", "youtube" if yts else "", "", ""))
for p in sorted(posts, key=lambda x: (x["date8"], x["lang"])):
    if p["kind"] == "pronto": escreve_pronto(p); continue
    lang, fm, corpo, chave = p["lang"], p["fm"], p["corpo"], p["date8"] + "01"
    if p["kind"] == "md":
        m = tit_re(corpo); titulo = html.unescape(m.group(1)).strip(); corpo = corpo[corpo.index("\n"):].strip()
    else: titulo = fm["titulo"]
    corpo = conserta_links(corpo)
    # vídeo, mural
    yts = re.findall(r"^\s*https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})\S*\s*$", corpo, re.M)
    corpo = re.sub(r"^\s*https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w-]{11}\S*\s*$", "", corpo, flags=re.M)
    mur = re.search(r"^\(\s*inserir aqui[^\n]*\)\s*\n(?:\s*legenda:[^\n]*\n?)?", corpo, re.M | re.I)
    if mur: corpo = corpo.replace(mur.group(0), "")
    corpo = re.sub(r"^\s*\(?\s*inserir aqui[^\n]*\n", "", corpo, flags=re.M | re.I)
    corpo, fontes_raw, cab = parte_fontes(corpo)
    if p["kind"] == "docx" and not fontes_raw and cab is None: pass
    corpo = limpa_inv(corpo); corpo = html.unescape(corpo) if re.search(r"&#?\w+;", corpo) else corpo
    corpo = quebra_paragrafos(corpo)
    corpo = arruma_espacos(corpo)
    corpo = links_internos(corpo, lang, slugs_existentes)
    if lang == "en-us":   # o Word em inglês perdeu os links "here": religa às partes anteriores / à receita do chá
        base = "/en-us/blog/teaching-tarot-gossip-version-part-"
        corpo = re.sub(r"(read part 1 of this little story) here\?", rf"\1 [here]({base}1/)?", corpo)
        corpo = re.sub(r"^And part 2 here\?", rf"And part 2 [here]({base}2/)?", corpo, flags=re.M)
        corpo = re.sub(r"^(Part 3 was the most interesting!) Here\s*$", rf"\1 [Here]({base}3/)", corpo, flags=re.M)
        corpo = corpo.replace("I already taught you here.", "I already taught you [here](/en-us/blog/recipe-apple-cinnamon-tea/).")
        corpo = corpo.replace("**Tea accompaniment:**", "**Tea accompaniment:**")
    corpo = re.sub(r"\n{3,}", "\n\n", corpo).strip()
    fontes = [normaliza(links_internos(html.unescape(conserta_links(x)), lang, slugs_existentes)) for x in fontes_raw]
    # blocos finais: mural e vídeo (depois das notas, antes das referências)
    extra = []
    if mur:
        cfg = MURAL[chave]; lin = []
        for k, (n, apt, aen, foco) in enumerate(cfg["fotos"], 1):
            src = SAI / "static/assets/images/blog" / f"{chave}-mural-{k}.webp"; src.parent.mkdir(parents=True, exist_ok=True)
            orig = next(ENT.rglob(f"{cfg['pref']}-imagem{n}.webp")); shutil.copy(orig, src)
            lin.append(f'{{{{< foto src="/assets/images/blog/{chave}-mural-{k}.webp" alt={q(apt if lang == "pt-br" else aen)}' + (f' foco="{foco}"' if foco else "") + " >}}")
        extra.append("{{< mural legenda=" + q(cfg["legenda"][lang]) + " >}}\n" + "\n".join(lin) + "\n{{< /mural >}}")
    for y in yts: extra.append("{{< youtube id=" + q(y) + " titulo=" + q(titulo) + " >}}")
    if p.get("img") is not None or "@@IMG@@" in corpo:
        from PIL import Image
        dst = SAI / "static/assets/images/blog" / f"{chave}-imagem-1.webp"; dst.parent.mkdir(parents=True, exist_ok=True)
        im = Image.open(p["img"]).convert("RGB"); im.thumbnail((1200, 1200), Image.LANCZOS); im.save(dst, "WEBP", quality=82, method=6)
        corpo = corpo.replace("@@IMG@@", "{{< figura src=\"/assets/images/blog/%s-imagem-1.webp\" alt=%s >}}" % (chave, q(BOAS_ALT[lang])))
    if extra: corpo += "\n\n" + "\n\n".join(extra)
    tags = fm["tags"]
    out = ["---", f"title: {q(titulo)}", f"date: {str(fm['date']).replace(' ', 'T')}", f"translationKey: {q(chave)}", f"{SELO[lang]}: [{q(fm['selo'])}]",
           "tags: [" + ", ".join(q(t) for t in tags) + "]", "bordado: false"]
    if fontes: out += ["fontes:"] + [f"  - {q(s)}" for s in fontes]
    out += ["---", "", corpo, ""]
    d = SAI / "content" / lang / "blog" / p["slug"]; d.mkdir(parents=True, exist_ok=True); (d / "index.md").write_text("\n".join(out), encoding="utf8")
    resumo.append((chave, lang, p["slug"], fm["selo"], len(fontes), len(tags), "mural" if mur else "", "youtube" if yts else "", "figura" if "@@IMG@@" in p["corpo"] else "", "tabela" if re.search(r"^\|", corpo, re.M) else ""))
    if p["kind"] == "md" and not fontes and not (lang and fm["selo"] in ("Meraki",)): aviso(f"{p['arq']}: sem referências (selo {fm['selo']})")
for r in resumo: print(*r)
print("\nAVISOS:"); [print("-", a) for a in avisos]
