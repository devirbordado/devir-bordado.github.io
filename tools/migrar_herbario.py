"""Gera o Herbário (PT e EN) a partir de lista_herbario.xlsx, da listagem de legendas (.md) e das imagens.
Uso: python tools/migrar_herbario.py PASTA   (a pasta tem o .xlsx, o .md e a subpasta herbario/ com os .webp)
Traduções longas (distribuição e observações) ficam em tools/herbario_en_longos.json."""
import re, sys, json, difflib, unicodedata
from pathlib import Path
import openpyxl
from PIL import Image
R = Path(__file__).resolve().parent.parent
E = Path(sys.argv[1])
IMG = E / "herbario"
# plantas cujo nome da legenda difere do da planilha (sinônimo ou só o gênero na legenda)
MANUAL = {"alecrim": "Rosmarinus officinalis", "pimenta": "Capsicum frutescens"}
def norm(s): return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
def limpa(s): return re.sub(r"\s+", " ", re.sub(r"\s+([.,;:])", r"\1", str(s or ""))).strip().rstrip(";").strip()
def slug(s): return norm(s).replace(" ", "-")
ETNO = {"medicinal": "medicinal", "ornamental": "ornamental", "comestível": "edible", "ritualístico": "ritual", "cosmético": "cosmetic"}
PONTO = {"reto": "straight stitch", "cheio": "satin stitch", "partido": "split stitch", "partio": "split stitch", "nó francês": "French knot", "matiz": "long-and-short stitch",
         "margarida": "lazy daisy stitch", "cheio radial": "radial satin stitch", "haste": "stem stitch", "atrás": "backstitch", "rococó": "rococo stitch"}
TEC = {"lona de algodão natural cru": "raw natural cotton canvas", "algodão natural cru": "raw natural cotton"}
SUP = {"bastidor circular de bambu": "circular bamboo hoop"}
def etno_en(s):
    itens = [x for x in re.split(r",\s*| e ", re.sub(r"^Uso\s+", "", s.strip())) if x]
    t = [ETNO.get(x.strip().lower(), x.strip()) for x in itens]
    j = t[0] if len(t) == 1 else ", ".join(t[:-1]) + " and " + t[-1]
    return j[0].upper() + j[1:] + " use"
def pontos(s, en):
    p = [x.strip() for x in s.split(",")]
    p = ["partido" if x == "partio" else x for x in p]
    p = [PONTO.get(x, x) for x in p] if en else p
    t = ", ".join(p); return t[0].upper() + t[1:]
def binom(s):
    t = s.split(); n = 3 if len(t) > 2 and t[1] == "×" else 2
    return " ".join(t[:n]), " ".join(t[n:])
ws = openpyxl.load_workbook(E / "lista_herbario.xlsx", data_only=True).active
rows = [r for r in ws.iter_rows(min_row=3, values_only=True) if r[2]]
leg = {}
txt = (E / "Listagem_de_legendas_para_herbário.md").read_text(encoding="utf8").replace("\r", "")
for nome, c in re.findall(r"\\\[Nome do arquivo: (.+?)\] - Legenda --> (.+?)(?=\n\n\n\n\\\[|\Z)", txt, flags=re.S):
    leg[nome.strip()] = re.sub(r"\s+", " ", c).replace("\\_", "_").strip()
def en_leg(c):
    for a, b in [("Imagem:", "Image:"), ("Bordado de", "Embroidery of"), (" por ", " by "), ("Fonte:", "Source:"), ("Foto:", "Photo:"), ("Disponível em:", "Available at:"), ("Licença:", "License:")]: c = c.replace(a, b)
    return c
longos = json.loads((R / "tools/herbario_en_longos.json").read_text(encoding="utf8"))
nomes = sorted({re.match(r"(.+?) (bordado|foto \d+)\.webp$", f.name).group(1) for f in IMG.glob("*.webp")})
usadas = set()
for n in nomes:
    lb = re.search(r"\*([^*]+)\*", leg[n + " bordado"]).group(1)
    sc = [(difflib.SequenceMatcher(None, norm(lb), norm(binom(r[2])[0])).ratio(), i) for i, r in enumerate(rows)]
    s, i = max(sc)
    if n in MANUAL: i = [k for k, r0 in enumerate(rows) if binom(r0[2])[0] == MANUAL[n]][0]; s = 1
    if s < 0.85: print("SEM CORRESPONDÊNCIA CLARA:", n, "|", lb, "| melhor:", rows[i][2], round(s, 2)); continue
    r = rows[i]; usadas.add(i); xb, aut = binom(r[2])
    if len(lb.split()) < 2: lb = xb
    elif norm(xb) != norm(lb): print("NOME DIFERENTE:", n, "| planilha:", xb, "| legenda:", lb); aut = ""
    sl = slug(n); popular = re.sub(r",(?=\S)", ", ", limpa(r[3]))
    saida = R / "static/assets/images/herbario"
    b = Image.open(IMG / f"{n} bordado.webp").convert("RGB"); b.thumbnail((1350, 1800), Image.LANCZOS); b.save(saida / f"{sl}-bordado.webp", "WEBP", quality=80, method=6)
    gal = []
    for k in (1, 2):
        g = Image.open(IMG / f"{n} foto {k}.webp").convert("RGB"); g.thumbnail((1200, 1200), Image.LANCZOS); g.save(saida / f"{sl}-foto-{k}.webp", "WEBP", quality=80, method=6)
        gal.append((f"/assets/images/herbario/{sl}-foto-{k}.webp", leg[f"{n} foto {k}"]))
    for lang, en in (("pt-br", False), ("en-us", True)):
        d = {"title": lb, "translationKey": sl, "type": "herbario", "autoria": aut, "familia": r[0], "classe": r[1], "popular": popular,
             "etnobotanica": etno_en(limpa(r[5])) if en else limpa(r[5]),
             "bordado_por": limpa(r[7]), "ano": limpa(r[8]), "risco": limpa(r[9]), "pontos": pontos(limpa(r[10]), en),
             "tecido": TEC.get(limpa(r[11]), limpa(r[11])) if en else limpa(r[11]), "suporte": SUP.get(limpa(r[12]), limpa(r[12])) if en else limpa(r[12]), "dimensoes": limpa(r[13]),
             "img": f"/assets/images/herbario/{sl}-bordado.webp", "img_caption": en_leg(leg[n + " bordado"]) if en else leg[n + " bordado"],
             "img_alt": ("Embroidery of " if en else "Bordado de ") + lb,
             "galeria": [{"img": a, "caption": en_leg(c) if en else c} for a, c in gal]}
        if en:
            if sl in longos: d["distribuicao"], d["observacoes"] = longos[sl]["distribuicao"], longos[sl]["observacoes"]
        else: d["distribuicao"], d["observacoes"] = limpa(r[4]), limpa(r[6])
        d = {k: v for k, v in d.items() if v not in ("", None)}
        pasta = R / "content" / lang / ("herbarium" if en else "herbario") / sl; pasta.mkdir(parents=True, exist_ok=True)
        (pasta / "index.md").write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf8")
print("plantas:", len(usadas), "de", len(rows), "| sem uso na planilha:", [rows[i][2] for i in range(len(rows)) if i not in usadas])
