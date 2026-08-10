from PIL import Image, ImageDraw, ImageFont, ImageFilter
import argparse, json, os, random, wave
import numpy as np

W, H = 1080, 1920
GOLD = (212, 166, 72)
GOLD2 = (255, 221, 143)
BLACK = (4, 5, 7)
FONT_B = '/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'
FONT_SB = '/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf'
FONT_M = '/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf'
FA = '/usr/share/fonts/opentype/font-awesome/FontAwesome.otf'

ITEMS = [
    ('PARRUCCHIERE', 'Eleganza, stile e prenotazioni online', ['Prenotazioni online', 'Servizi e listino', 'Contatto WhatsApp'], '\uf0c4'),
    ('GIOIELLERIA', 'Eleganza che continua anche online', ['Collezioni in vetrina', 'Richieste personalizzate', 'Contatto diretto'], '\uf219'),
    ('PALESTRA', 'Trasforma visite in nuovi iscritti', ['Corsi e orari', 'Prova gratuita', 'Contatti immediati'], '\uf21e'),
    ('RISTORANTE', 'Un sito che apre l’appetito', ['Menu digitale', 'Prenotazioni', 'Mappa e contatti'], '\uf0f5'),
    ('IDRAULICO', 'Fatti trovare quando servi davvero', ['Richiesta intervento', 'Zone servite', 'Contatto rapido'], '\uf0ad'),
    ('ELETTRICISTA', 'Professionalità già dal primo click', ['Servizi chiari', 'Preventivo rapido', 'Contatto immediato'], '\uf0e7'),
    ('OFFICINA CNC', 'Precisione anche nella presenza online', ['Lavorazioni', 'Parco macchine', 'Richiesta preventivo'], '\uf085'),
    ('DENTISTA', 'Fiducia prima ancora della visita', ['Trattamenti', 'Prenotazione', 'Studio e contatti'], '\uf0fe'),
    ('OFFICINA AUTO', 'Porta più clienti in officina', ['Servizi e tagliandi', 'Prenotazione', 'Contatto veloce'], '\uf1b9'),
    ('CENTRO ESTETICO', 'La tua immagine merita un sito premium', ['Trattamenti', 'Prenotazioni', 'Promo e contatti'], '\uf0d0'),
    ('TATUATORE', 'Mostra il tuo stile prima dell’appuntamento', ['Portfolio', 'Richiesta tattoo', 'Prenotazioni'], '\uf1fc'),
    ('BAR & CAFFETTERIA', 'Fatti scegliere prima ancora di entrare', ['Menu e specialità', 'Orari aggiornati', 'Mappa e contatti'], '\uf0f4'),
    ('PASTICCERIA', 'Il primo assaggio deve essere visivo', ['Vetrina prodotti', 'Ordini e richieste', 'Contatti rapidi'], '\uf1fd'),
    ('PANIFICIO', 'Tradizione con una presenza moderna', ['Prodotti del giorno', 'Orari e punti vendita', 'Contatto diretto'], '\uf291'),
    ('HOTEL & B&B', 'Più richieste dirette, meno passaggi', ['Camere e servizi', 'Richiesta disponibilità', 'Mappa e contatti'], '\uf236'),
    ('AGENZIA IMMOBILIARE', 'Gli immobili meritano una vetrina forte', ['Schede immobili', 'Richieste visita', 'Contatto agente'], '\uf015'),
    ('AVVOCATO', 'Autorevolezza, chiarezza, contatto', ['Aree di competenza', 'Richiesta consulenza', 'Contatti studio'], '\uf24e'),
    ('COMMERCIALISTA', 'Servizi chiari per clienti più sereni', ['Consulenze', 'Documenti e contatti', 'Richiesta appuntamento'], '\uf1ec'),
    ('ARCHITETTO', 'Il progetto inizia dalla tua immagine', ['Portfolio', 'Servizi', 'Richiesta progetto'], '\uf040'),
    ('FOTOGRAFO', 'Il tuo portfolio deve parlare da solo', ['Gallery', 'Servizi fotografici', 'Richiesta preventivo'], '\uf030'),
    ('FALEGNAME', 'Artigianato raccontato bene', ['Lavori realizzati', 'Su misura', 'Richiesta preventivo'], '\uf1bb'),
    ('IMPRESA EDILE', 'Più credibilità, più richieste', ['Cantieri e servizi', 'Preventivo', 'Contatto diretto'], '\uf1ad'),
    ('SERRAMENTISTA', 'Mostra qualità e soluzioni', ['Prodotti', 'Installazione', 'Richiesta sopralluogo'], '\uf009'),
    ('CLIMATIZZAZIONE', 'Comfort e assistenza a portata di click', ['Installazione', 'Manutenzione', 'Richiesta intervento'], '\uf2dc'),
    ('VETERINARIO', 'Fiducia per chi ama gli animali', ['Servizi', 'Prenotazione', 'Contatti urgenti'], '\uf1b0'),
    ('FISIOTERAPISTA', 'Fatti trovare da chi cerca sollievo', ['Trattamenti', 'Prenotazioni', 'Contatto diretto'], '\uf21e'),
    ('NEGOZIO ABBIGLIAMENTO', 'Porta il tuo stile anche online', ['Nuovi arrivi', 'Catalogo', 'Contatto negozio'], '\uf290'),
    ('E-COMMERCE ARTIGIANO', 'Dal laboratorio al cliente', ['Catalogo prodotti', 'Ordini online', 'Brand su misura'], '\uf07a'),
    ('WEDDING & EVENTI', 'Ogni evento parte da un’emozione', ['Portfolio', 'Pacchetti', 'Richiesta informazioni'], '\uf004'),
]

def font(path, size):
    return ImageFont.truetype(path, size)

def gradient_bg():
    y = np.arange(H)[:, None]
    x = np.arange(W)[None, :]
    base = np.zeros((H, W, 3), dtype=np.float32)
    base[:] = np.array(BLACK)
    for cx, cy, strength, radius in [(840, 300, 1.0, 720), (180, 1540, .5, 800)]:
        dist = np.sqrt((x-cx)**2 + (y-cy)**2)
        aa = np.clip(1-dist/radius, 0, 1)**2 * strength
        for k, c in enumerate((120, 70, 16)):
            base[:, :, k] += aa*c
    base[:, :, 2] += np.clip((x/W)*10, 0, 10)
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), 'RGB')

def glow_text_layer(text, ft, xy, fill=GOLD2, anchor='mm', blur=18):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.text(xy, text, font=ft, fill=(*GOLD, 180), anchor=anchor, stroke_width=2, stroke_fill=(255, 210, 90, 140))
    glow = lay.filter(ImageFilter.GaussianBlur(blur))
    sharp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sharp)
    ds.text(xy, text, font=ft, fill=(*fill, 255), anchor=anchor)
    return Image.alpha_composite(glow, sharp)

def rounded_gradient(size, c1, c2, r=36):
    w, h = size
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    for yy in range(h):
        aa = yy/max(1, h-1)
        col = [int(c1[i]*(1-aa)+c2[i]*aa) for i in range(3)]
        arr[yy, :, 0:3] = col
        arr[yy, :, 3] = 255
    im = Image.fromarray(arr, 'RGBA')
    mask = Image.new('L', (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, w-1, h-1), r, fill=255)
    im.putalpha(mask)
    return im

def draw_device(img, title, icon):
    d = ImageDraw.Draw(img)
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((120, 680, 930, 1295), 38, fill=(0, 0, 0, 210))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(30)))
    d.rounded_rectangle((120, 650, 930, 1265), 38, fill=(18, 19, 23, 255), outline=(185, 145, 65, 210), width=3)
    img.alpha_composite(rounded_gradient((754, 540), (17, 17, 20), (36, 22, 8), 28), (148, 687))
    sd = ImageDraw.Draw(img)
    sd.rounded_rectangle((174, 713, 900, 758), 18, fill=(6, 7, 9, 180))
    for i, c in enumerate([(220, 95, 80), (230, 180, 70), (95, 190, 120)]):
        sd.ellipse((192+i*29, 728, 204+i*29, 740), fill=c)
    sd.text((208, 817), title, font=font(FONT_B, 42), fill=(247, 238, 219), anchor='la')
    sd.text((208, 878), 'PRESENZA DIGITALE SU MISURA', font=font(FONT_M, 16), fill=(218, 180, 99), anchor='la')
    sd.rounded_rectangle((208, 930, 475, 984), 18, fill=(203, 157, 66))
    sd.text((341, 957), 'RICHIEDI UNA DEMO', font=font(FONT_SB, 17), fill=(9, 9, 10), anchor='mm')
    sd.rounded_rectangle((570, 800, 850, 1115), 28, fill=(8, 9, 11, 220), outline=(167, 126, 51, 160), width=2)
    sd.text((710, 933), icon, font=font(FA, 112), fill=(235, 191, 97), anchor='mm')
    for j in range(3):
        yy = 1040+j*52
        sd.rounded_rectangle((220, yy, 490, yy+31), 10, fill=(255, 255, 255, 16), outline=(255, 255, 255, 20))
    sd.polygon([(92, 1263), (958, 1263), (1000, 1315), (47, 1315)], fill=(45, 43, 39), outline=(147, 118, 62))
    sd.rounded_rectangle((420, 1275, 620, 1294), 8, fill=(82, 74, 60))
    pshadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pshadow)
    pd.rounded_rectangle((720, 1020, 955, 1505), 45, fill=(0, 0, 0, 220))
    img.alpha_composite(pshadow.filter(ImageFilter.GaussianBlur(24)))
    sd.rounded_rectangle((715, 1000, 950, 1485), 44, fill=(18, 18, 21), outline=(212, 166, 72), width=3)
    sd.rounded_rectangle((732, 1028, 933, 1454), 30, fill=(15, 12, 9))
    sd.text((832, 1140), icon, font=font(FA, 62), fill=(226, 179, 84), anchor='mm')
    sd.rounded_rectangle((766, 1212, 899, 1248), 12, fill=(203, 157, 66))
    sd.text((832, 1230), 'DEMO', font=font(FONT_B, 13), fill=(10, 10, 10), anchor='mm')

def render(index, out):
    title, sub, benefits, icon = ITEMS[index % len(ITEMS)]
    img = gradient_bg().convert('RGBA')
    d = ImageDraw.Draw(img)
    random.seed(index+220)
    for _ in range(95):
        xx = random.randrange(W); yy = random.randrange(H)
        rr = random.choice([1, 1, 2, 2, 3]); aa = random.randrange(25, 110)
        d.ellipse((xx-rr, yy-rr, xx+rr, yy+rr), fill=(231, 186, 89, aa))
    img.alpha_composite(glow_text_layer('K', font(FONT_B, 155), (112, 125), blur=24))
    d = ImageDraw.Draw(img)
    d.text((225, 95), 'KAIRON LABS', font=font(FONT_B, 31), fill=(246, 238, 222), anchor='la')
    d.text((226, 138), 'STUDIO', font=font(FONT_SB, 21), fill=GOLD2, anchor='la')
    d.line((226, 173, 680, 173), fill=(193, 148, 58, 160), width=2)
    d.text((915, 124), f'{index+1:02d}/29', font=font(FONT_M, 20), fill=(177, 151, 105), anchor='ra')
    d.text((78, 305), 'SITO WEB PER', font=font(FONT_SB, 35), fill=(213, 172, 87), anchor='la')
    fs = 75 if len(title) <= 15 else 60 if len(title) <= 22 else 50
    d.text((78, 365), title, font=font(FONT_B, fs), fill=(249, 244, 234), anchor='la')
    d.rounded_rectangle((78, 470, 430, 478), 4, fill=(215, 167, 70))
    d.text((78, 525), sub, font=font(FONT_M, 31), fill=(211, 202, 184), anchor='la')
    halo = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    hd.ellipse((770, 265, 1040, 535), fill=(200, 147, 48, 35), outline=(224, 181, 90, 100), width=2)
    hd.text((905, 400), icon, font=font(FA, 112), fill=(239, 194, 100, 210), anchor='mm')
    img.alpha_composite(halo)
    draw_device(img, title, icon)
    d = ImageDraw.Draw(img)
    for i, b in enumerate(benefits):
        yy = 1390+i*94
        d.ellipse((84, yy+7, 118, yy+41), fill=(212, 166, 72), outline=(255, 225, 150))
        d.text((101, yy+24), '✓', font=font(FONT_B, 19), fill=(8, 8, 9), anchor='mm')
        d.text((145, yy+23), b, font=font(FONT_SB, 30), fill=(238, 231, 219), anchor='lm')
    d.rounded_rectangle((74, 1710, 1006, 1838), 36, fill=(16, 14, 10, 220), outline=(220, 174, 80, 210), width=3)
    d.text((540, 1752), 'VUOI VEDERE LA TUA IDEA ONLINE?', font=font(FONT_SB, 26), fill=(244, 236, 221), anchor='mm')
    d.text((540, 1800), 'DEMO GRATUITA  •  LINK IN BIO', font=font(FONT_B, 30), fill=GOLD2, anchor='mm')
    d.text((540, 1876), 'KAIRONLABSSTUDIO', font=font(FONT_M, 18), fill=(151, 135, 110), anchor='mm')
    img.convert('RGB').save(out, 'JPEG', quality=92, optimize=True, progressive=True)
    return {
        'index': index,
        'title': title,
        'subtitle': sub,
        'benefits': benefits,
        'caption': f"{sub}. {', '.join(benefits)}. Vuoi vedere una demo gratuita per la tua attività? Scrivici in DM o visita il link in bio. #KaironLabsStudio #SitiWeb #WebDesign #Business #Digitale"
    }

def make_post(reel_path, out):
    src = Image.open(reel_path).convert('RGB')
    pw, ph = 1080, 1350
    bg = src.resize((pw, ph), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(24))
    scale = min(pw/src.width, ph/src.height)
    fg = src.resize((int(src.width*scale), int(src.height*scale)), Image.Resampling.LANCZOS)
    x = (pw-fg.width)//2; y = (ph-fg.height)//2
    bg.paste(fg, (x, y))
    bg.save(out, 'JPEG', quality=92, optimize=True, progressive=True)

def make_audio(out, sr=48000, dur=9.0):
    """Cinematic Kairon ident: deep, epic and deliberately WITHOUT the rising whistle."""
    n = int(sr*dur)
    t = np.arange(n)/sr
    rng = np.random.default_rng(20260810)
    a = np.zeros(n, dtype=np.float64)

    # Dark orchestral bed.
    for freq, amp in [(36.7, .19), (55, .13), (73.4, .08), (110, .035)]:
        phase = 2*np.pi*freq*t
        env = (1-np.exp(-3*t))*np.exp(-0.11*t)
        a += amp*(np.sin(phase)+.20*np.sin(2*phase)+.06*np.sin(3*phase))*env

    # Three low cinematic impacts, no high-frequency sweep.
    for st, gain in [(0.05, .35), (2.55, .42), (5.25, .50)]:
        mask = t >= st
        q = t[mask]-st
        freq = 62*np.exp(-2.2*q)+29
        ph = 2*np.pi*np.cumsum(freq)/sr
        a[mask] += gain*np.sin(ph)*np.exp(-2.2*q)
        noise = rng.normal(0, 1, q.size)
        smooth = np.convolve(noise, np.ones(96)/96, mode='same')
        a[mask] += .035*smooth*np.exp(-5*q)

    # Brass-like low/mid chord after the final hit. Kept below whistle range.
    st = 5.2
    mask = t >= st
    q = t[mask]-st
    for f0, amp in [(82.4, .08), (123.5, .065), (164.8, .045), (247, .018)]:
        sig = np.sin(2*np.pi*f0*q) + .25*np.sin(2*np.pi*2*f0*q)
        a[mask] += amp*sig*np.exp(-.65*q)*(1-np.exp(-12*q))

    # Short room tails.
    wet = a.copy()
    for delay_s, gain in [(.11, .16), (.24, .09), (.42, .045)]:
        dd = int(delay_s*sr)
        wet[dd:] += gain*a[:-dd]
    wet = np.tanh(wet*1.25)
    wet[:int(.04*sr)] *= np.linspace(0, 1, int(.04*sr))
    wet[-int(.8*sr):] *= np.linspace(1, 0, int(.8*sr))
    wet /= max(1e-9, np.max(np.abs(wet)))
    wet *= .58
    right = np.roll(wet, int(.006*sr))*.98
    pcm = (np.stack([wet, right], 1)*32767).astype(np.int16)
    with wave.open(out, 'wb') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(pcm.tobytes())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--index', type=int, default=0)
    ap.add_argument('--outdir', default='generated')
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    make_audio(os.path.join(args.outdir, 'kairon-cinematic-ident.wav'))
    reel_img = os.path.join(args.outdir, 'kairon-daily.jpg')
    meta = render(args.index, reel_img)
    make_post(reel_img, os.path.join(args.outdir, 'kairon-post.jpg'))
    with open(os.path.join(args.outdir, 'meta.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False)
    print(json.dumps(meta, ensure_ascii=False))

if __name__ == '__main__':
    main()
