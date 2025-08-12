import pdfplumber
import re
from deep_translator import GoogleTranslator
from collections import Counter

def estrai_testo_due_colonne(pdf_path, start_page=1):
    testo_per_pagina = []
    with pdfplumber.open(pdf_path) as pdf:
        start_idx = max(0, start_page - 1)
        for i in range(start_idx, len(pdf.pages)):
            pagina = pdf.pages[i]
            width = pagina.width
            height = pagina.height
            colonna_sx = pagina.within_bbox((0, 0, width / 2, height))
            colonna_dx = pagina.within_bbox((width / 2, 0, width, height))
            testo_sx = estrai_righe_da_blocchi(colonna_sx)
            testo_dx = estrai_righe_da_blocchi(colonna_dx)
            righe = testo_sx + testo_dx
            testo_per_pagina.append(righe)
    return testo_per_pagina

def estrai_righe_da_blocchi(page):
    righe = []
    words = page.extract_words()
    words.sort(key=lambda w: (round(w['top'], 1), w['x0']))
    riga_corrente = []
    top_precedente = None
    for word in words:
        top = round(word['top'], 1)
        if top != top_precedente and riga_corrente:
            righe.append(" ".join(riga_corrente))
            riga_corrente = []
        riga_corrente.append(word['text'])
        top_precedente = top
    if riga_corrente:
        righe.append(" ".join(riga_corrente))
    return righe

def rileva_piedipagina(testo_per_pagina, soglia=0.3):
    righe_finali = [pagina[-1].strip() for pagina in testo_per_pagina if len(pagina) >= 1]
    contatore = Counter(righe_finali)
    occorrenze_minime = int(len(testo_per_pagina) * soglia)
    piedipagina = {riga for riga, count in contatore.items() if count >= occorrenze_minime}
    return piedipagina

def is_probabile_titolo(riga):
    parole = riga.strip().split()
    if len(parole) > 10 or riga.endswith(('.', ':', ';', '!', '?')):
        return False
    if re.match(r'^\d+(\.\d+)*\s+.+', riga):  # Titolo numerato
        return True
    if all(p[0].isupper() for p in parole if p.isalpha()):
        return True
    return False

def pulisci_testo(testo_per_pagina, piedipagina):
    testo_completo = ""
    paragrafi_visti = set()

    for pagina in testo_per_pagina:
        righe_pulite = []
        skip_next = False
        i = 0
        while i < len(pagina):
            riga = pagina[i].strip()

            if i == 0 and riga.lower() == "manuale di equitazione":
                i += 1
                continue
            if skip_next:
                skip_next = False
                i += 1
                continue
            if riga in piedipagina:
                i += 1
                continue

            parole = riga.split()
            if len(parole) <= 7 and not riga.endswith((".", "!", "?")) and not re.match(r'^\d+(\.\d+)*\s+', riga):
                if riga in paragrafi_visti:
                    i += 1
                    continue

            if ":" in riga or (i + 1 < len(pagina) and len(pagina[i + 1].strip()) > 40):
                paragrafi_visti.add(riga)

            if len(riga) < 20:
                if re.search(r'^(Figura|Fig\.|Tabella|Immagine)', riga, re.IGNORECASE):
                    i += 1
                    continue

            if riga.endswith("-") and i + 1 < len(pagina):
                next_line = pagina[i + 1].strip()
                riga = riga[:-1] + next_line
                skip_next = True

            righe_pulite.append(riga)
            i += 1

        testo_completo += "\n" + "\n".join(righe_pulite)
    return testo_completo

def correggi_parole_spezzate(testo):
    return re.sub(r'-\s+', '', testo)

def spezza_in_frasi(testo):
    righe = testo.split("\n")
    frasi = []
    buffer = ""
    for riga in righe:
        riga = riga.strip()
        if not riga:
            continue
        if is_probabile_titolo(riga):
            if buffer:
                frasi.extend(re.findall(r'[A-ZÀ-Ú][^.!?]*[.!?]', buffer))
                buffer = ""
            frasi.append(riga)
        else:
            buffer += " " + riga
    if buffer:
        frasi.extend(re.findall(r'[A-ZÀ-Ú][^.!?]*[.!?]', buffer))
    return [f.strip() for f in frasi]

def filtra_didascalie_residue(frasi):
    frasi_filtrate = []
    for frase in frasi:
        parole = frase.strip().split()
        if len(parole) <= 3 and not re.search(r"\b(è|ha|sono|era|si|vede|hanno|c'è|ci sono|appare|presenta)\b", frase, re.IGNORECASE):
            continue
        if len(parole) == 2 and all(p[0].isupper() for p in parole) and not frase.endswith(('.', '!', '?')):
            continue
        if frase.istitle() and not frase.endswith(('.', '!', '?')) and len(parole) <= 4:
            continue
        frasi_filtrate.append(frase)
    return frasi_filtrate

def traduci_frasi(frasi):
    traduttore = GoogleTranslator(source='it', target='en')
    tradotte = []
    for frase in frasi:
        try:
            tradotte.append(traduttore.translate(frase))
        except Exception:
            tradotte.append(f"[TRANSLATION ERROR] {frase}")
    return tradotte

def salva_txt(frasi, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        for frase in frasi:
            f.write(frase + "\n")

def processa_pdf(pdf_path, output_txt_path, start_page=1):
    print(f"Estrazione testo da pagina {start_page} in poi...")
    testo_per_pagina = estrai_testo_due_colonne(pdf_path, start_page=start_page)
    print("Rilevamento piè di pagina...")
    piedipagina = rileva_piedipagina(testo_per_pagina)
    print("Pulizia testo...")
    testo_pulito = pulisci_testo(testo_per_pagina, piedipagina)
    testo_pulito = correggi_parole_spezzate(testo_pulito)
    print("Divisione in frasi...")
    frasi = spezza_in_frasi(testo_pulito)
    print("Filtro delle didascalie residue...")
    frasi = filtra_didascalie_residue(frasi)
    print("Salvataggio file TXT...")
    salva_txt(frasi, output_txt_path)
    print(f"✅ Fatto! File salvato in: {output_txt_path}")

if __name__ == "__main__":
    pdf_input = "Manuale FISE.pdf"
    output_txt = "Manuale_FISE_output.txt"
    pagina_iniziale = int(input("Da quale pagina iniziare? (1-based index): "))
    processa_pdf(pdf_input, output_txt, start_page=pagina_iniziale)

