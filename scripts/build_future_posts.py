from pathlib import Path
import json, importlib.util, re
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'scripts' / 'kairon_monthly.py'
OUT = ROOT / 'scheduled_posts'
OUT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location('kairon_monthly', SOURCE)
km = importlib.util.module_from_spec(spec)
spec.loader.exec_module(km)

# The parrucchiere is today's approved item. Build the following 29 future images.
future = list(range(1, len(km.ITEMS)))
km.ITEMS.append(('PIZZERIA', 'Un sito che apre l’appetito e vende', ['Menu e delivery', 'Prenotazioni', 'Ordini e contatti'], '\uf0f5'))
future.append(len(km.ITEMS) - 1)


def slug(text):
    text = text.lower().replace('&', 'e')
    text = re.sub(r'[^a-z0-9]+', '_', text).strip('_')
    return text


def to_feed(src, dst):
    img = Image.open(src).convert('RGB')
    W, H = 1080, 1350
    # blurred full-bleed background
    ratio = max(W / img.width, H / img.height)
    bg = img.resize((round(img.width * ratio), round(img.height * ratio)), Image.LANCZOS)
    left = (bg.width - W) // 2
    top = (bg.height - H) // 2
    bg = bg.crop((left, top, left + W, top + H)).filter(ImageFilter.GaussianBlur(24))
    # full original composition in front, so no headline/CTA is cut
    fg_h = H
    fg_w = round(img.width * fg_h / img.height)
    fg = img.resize((fg_w, fg_h), Image.LANCZOS)
    bg.paste(fg, ((W - fg_w) // 2, 0))
    bg.save(dst, 'JPEG', quality=92, optimize=True, progressive=True)


manifest = []
for day, idx in enumerate(future, start=2):
    title = km.ITEMS[idx][0]
    vertical = OUT / '_tmp_vertical.jpg'
    meta = km.render(idx, str(vertical))
    filename = f'{day:02d}_{slug(title)}.jpg'
    target = OUT / filename
    to_feed(vertical, target)
    vertical.unlink(missing_ok=True)
    manifest.append({
        'day': day,
        'title': title,
        'file': filename,
        'format': '1080x1350',
        'caption': meta.get('caption', '') if isinstance(meta, dict) else ''
    })

(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Generated {len(manifest)} future posts in {OUT}')
