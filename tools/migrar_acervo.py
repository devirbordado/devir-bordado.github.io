"""Gera o Acervo (PT e EN). Uso: python tools/migrar_acervo.py PASTA
A PASTA tem uma subpasta por coleção, com 1.webp, 2.webp... e o .md de texto e legendas."""
import re, sys, json
from pathlib import Path
from PIL import Image
R = Path(__file__).resolve().parent.parent
E = Path(sys.argv[1])
# pasta: (slug PT, slug EN, ordem, título EN, texto EN, ano EN, nota EN, tradução das legendas)
C = {
 "memorias bordadas": ("exposicao-memorias-bordadas", "embroidered-memories-exhibition", 1, "Embroidered Memories Exhibition",
  "The exhibition aimed to give back to the community the reflections developed throughout the academic research, in order to publicize, value and recognize the memories of the simple life in the countryside of the states of Minas Gerais and São Paulo, the authors' region of origin. This action offered the opportunity to observe and interact reflectively, since the works provide an experience that is both aesthetic and emotionally appealing, connecting with the visitor and leading them to awaken memories.",
  "between 2023 and 2024", "Access the catalog [here]({url}).",
  ["Embroidery of the plant *Coffea arabica*", "Embroidery of filtered coffee", "Embroidery of a basket of pão de queijo (cheese bread)", "Embroidery of Minas cheese", "Embroidery of doces de leite (milk sweets)", "Embroidery of Mãe d'Ouro (the \"Gold Mother\" legend)", "Embroidery of the town square bandstand", "Embroidery of festa junina (June festival)", "Embroidery of colony houses (farmworkers' houses)", "Embroidery of folia de reis (Three Kings' festival)", "Embroidery of a wood-fired oven"]),
 "fios de vida": ("fios-de-vida", "threads-of-life", 2, "Threads of Life",
  "This collection brings together the embroideries used as objects of analysis and narrative in the academic article \"**Fios de Vida: o bordado como etnobiografia visual feminina**\" (provisional translation: \"Threads of Life: embroidery as female visual ethnobiography\"). The work was published in the journal Iluminuras (vol. 27, no. 74, 2026), a periodical linked to the Graduate Program in Social Anthropology at the Federal University of Rio Grande do Sul (UFRGS).\n\nAccess the research below to better understand how the symbols dialogue with the embroideries created and how the narrative was used in building the work. The results indicate embroidery as a sensitive and biographical archive, which converts memory, territoriality and female ancestry into visual and tactile language. From this analysis, the conclusion was reached that textile practices expand the concept of biographical narrative and of document, highlighting their potential as a form of symbolic resistance and of situated knowledge production.",
  "between 2024 and 2025", "", ["Hanging plants", "Vocational plants", "Trinity of protection", "Adam's rib (costela-de-Adão)"]),
 "florilegio": ("florilegio", "florilegium", 3, "Florilegium",
  "The word *florilégio* comes from the Latin *florilegium*, formed by *flos*, meaning \"flower\", and *legere*, meaning \"to gather\" or \"to choose\". Literally, it means a collection of chosen flowers, although, in a figurative sense, it means an anthology, collection or compilation of selected passages from literary, artistic or scientific works.\n\nThis is a personal collection that dialogues with the whole path proposed by the lab by using the language of plants to compile artistic expressions and make scientific knowledge public.",
  "2024", "", ["Floral Bouquet", "Lavenders", "Candlewick"]),
}
def campo(t, a, b):
    m = re.search(a + r"\s*\n(.+?)(?=\n\s*\n\s*" + b + r"|\Z)", t, flags=re.S); return re.sub(r"[ \t]*\n[ \t]*\n[ \t]*", "\n\n", m.group(1).strip()) if m else ""
def en_leg(c):
    for a, b in [("Bordado por", "Embroidered by"), ("Imagem:", "Image:"), (" por Iara Lima", " by Iara Lima"), ("Fonte: Arquivo pessoal da autora.", "Source: Author's personal archive."), ("Fonte:", "Source:"), ("Foto:", "Photo:"), ("Motivo criado por", "Design created by")]: c = c.replace(a, b)
    return c
for pasta, (sp, se, ordem, ten, sobre_en, ano_en, nota_en, legs_en) in C.items():
    d = E / pasta; md = next(d.glob("*.md")); t = md.read_text(encoding="utf8").replace("\r", "")
    nome = campo(t, "Nome da coleção:", "Sobre:"); sobre = campo(t, "Sobre:", "Ano de criação:"); ano = campo(t, "Ano de criação:", r"(Nota:|\\-)")
    nota = re.search(r"Nota:\s*(.+)", t); nota = nota.group(1).strip().replace("\\_", "_") if nota else ""
    url = re.search(r"https?://\S+", nota); url = url.group(0) if url else ""
    nota_pt = f"Acesse o catálogo [aqui]({url})." if url else ""
    legs = {int(n): re.sub(r"\s+", " ", c).strip() for n, c in re.findall(r"\\\[Nome do arquivo: (\d+)\] - Legenda --> (.+?)(?=\n\n\n\n\\\[|\n*\Z)", t, flags=re.S)}
    imgs = []
    for k in sorted(legs):
        im = Image.open(d / f"{k}.webp").convert("RGB"); im.thumbnail((1400, 1400), Image.LANCZOS)
        im.save(R / "static/assets/images/acervo" / f"{sp}-{k}.webp", "WEBP", quality=80, method=6); imgs.append(f"/assets/images/acervo/{sp}-{k}.webp")
    for lang, en in (("pt-br", False), ("en-us", True)):
        gal = []
        for i, k in enumerate(sorted(legs)):
            c = legs[k] if not en else en_leg(legs[k]).replace(re.sub(r"^Imagem: (.+?) por Iara Lima.*", r"\1", legs[k]), legs_en[i]) if lang == "en-us" and "Floril" not in nome and "Candlewick" not in legs[k] else en_leg(legs[k])
            gal.append({"img": imgs[i], "caption": c})
        if en and pasta == "florilegio":
            for g, nm in zip(gal, legs_en): g["caption"] = g["caption"].replace(re.sub(r"^Image: (.+?) by Iara Lima.*", r"\1", g["caption"]), nm)
        fm = {"title": ten if en else nome, "translationKey": sp, "type": "acervo", "weight": ordem, "ano": ano_en if en else ano, "img": imgs[0], "galeria": gal}
        n = (nota_en.format(url=url) if url else "") if en else nota_pt
        if n: fm["nota"] = n
        body = (sobre_en if en else sobre) + "\n"
        if not n: body += "\n[//]: # (Quando o link existir, acrescente no topo deste arquivo, entre aspas, a linha:  \"nota\": \"Acesse a pesquisa [aqui](ENDEREÇO).\" )\n"
        pasta_c = R / "content" / lang / ("collection" if en else "acervo") / (se if en else sp); pasta_c.mkdir(parents=True, exist_ok=True)
        (pasta_c / "index.md").write_text(json.dumps(fm, ensure_ascii=False, indent=1) + "\n\n" + body, encoding="utf8"); print(lang, pasta_c.name, len(gal))
