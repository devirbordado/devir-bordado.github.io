"""Gera as miniaturas de capa do Herbário: recorta cada foto ao redor do bastidor, sem a área vazia.
Uso: python tools/capas_herbario.py PASTA_COM_AS_FOTOS_ORIGINAIS   (arquivos 'nome bordado.webp')
Para corrigir um recorte à mão, coloque em tools/capas_manual.json: {"slug": [x0, y0, x1, y1]} em frações de 0 a 1."""
import re, sys, json, unicodedata
from pathlib import Path
import numpy as np
from PIL import Image
R = Path(__file__).resolve().parent.parent
ENT = Path(sys.argv[1])
manual = json.loads((R / "tools/capas_manual.json").read_text()) if (R / "tools/capas_manual.json").exists() else {}
def slug(s): return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().replace(" ", "-")
def caixa(im):
    a = np.asarray(im.convert("RGB").resize((400, round(400 * im.height / im.width)))).astype(float)
    h, w, _ = a.shape; p = max(8, w // 25)
    cantos = np.concatenate([a[:p, :p].reshape(-1, 3), a[:p, -p:].reshape(-1, 3), a[-p:, :p].reshape(-1, 3), a[-p:, -p:].reshape(-1, 3)])
    d = np.abs(a - np.median(cantos, axis=0)).max(axis=2) > 38
    ys, xs = np.where(d); lin = d.mean(axis=1); col = d.mean(axis=0)
    y = np.where(lin > 0.04)[0]; x = np.where(col > 0.04)[0]
    if len(x) < 5 or len(y) < 5: return (0, 0, 1, 1)
    return (x[0] / w, y[0] / h, (x[-1] + 1) / w, (y[-1] + 1) / h)
for f in sorted(ENT.glob("* bordado.webp")):
    n = f.name[:-len(" bordado.webp")]; s = slug(n); im = Image.open(f).convert("RGB"); W, H = im.size
    x0, y0, x1, y1 = manual.get(s) or caixa(im)
    cx, cy = (x0 + x1) / 2 * W, (y0 + y1) / 2 * H; lado = max((x1 - x0) * W, (y1 - y0) * H) * 1.10
    lado = min(lado, W, H); l = min(max(cx - lado / 2, 0), W - lado); t = min(max(cy - lado / 2, 0), H - lado)
    im.crop((round(l), round(t), round(l + lado), round(t + lado))).resize((800, 800), Image.LANCZOS).save(R / "static/assets/images/herbario" / f"{s}-capa.webp", "WEBP", quality=80, method=6)
    print(s, [round(v, 2) for v in (x0, y0, x1, y1)])
