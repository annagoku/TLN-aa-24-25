import pdfplumber
import re
from deep_translator import GoogleTranslator
from collections import Counter

import pdfplumber

def estrai_testo_due_colonne(pdf_path, start_page=1):
    testo_per_pagina = []
    with pdfplumber.open(pdf_path) as pdf:
        start_idx = max(0, start_page - 1)

        for i in range(start_idx, len(pdf.pages)):
            pagina = pdf.pages[i]
            width = pagina.width
            height = pagina.height

            # Dividi in due colonne
            colonna_sinistra = pagina.within_bbox((0, 0, width / 2, height))
            colonna_destra = pagina.within_bbox((width / 2, 0, width, height))

            testo_sinistra = estrai_righe_da_blocchi(colonna_sinistra)
            testo_destra = estrai_righe_da_blocchi(colonna_destra)

            righe = testo_sinistra + testo_destra
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

def pulisci_testo(testo_per_pagina, piedipagina):
    testo_completo = ""
    paragrafi_visti = set()  # memorizza i titoli/paragrafi già visti

    for pagina in testo_per_pagina:
        righe_pulite = []
        skip_next = False
        i = 0
        while i < len(pagina):
            riga = pagina[i].strip()

            # ⛔️ Intestazione
            if i == 0 and riga.lower() == "manuale di equitazione":
                i += 1
                continue

            if skip_next:
                skip_next = False
                i += 1
                continue

            # ⛔️ Piè di pagina
            if riga in piedipagina:
                i += 1
                continue

            # ⚠️ Trattamento speciale per righe brevi
            parole = riga.split()
            if (
                len(parole) <= 7
                and not riga.endswith((".", "!", "?"))
                and not re.match(r'^\d+(\.\d+)*\s+', riga)  # non è titolo numerato
            ):
                # Se già vista sopra come inizio paragrafo, salta (probabile didascalia)
                if riga in paragrafi_visti:
                    i += 1
                    continue

            # Salviamo la riga come paragrafo significativo se contiene ':' o è seguita da frase
            if ":" in riga or (i + 1 < len(pagina) and len(pagina[i + 1].strip()) > 40):
                paragrafi_visti.add(riga)

            # ⛔️ Didascalie classiche
            if len(riga) < 20:
                i += 1
                continue
            if re.search(r'^(Figura|Fig\.|Tabella|Immagine)', riga, re.IGNORECASE):
                i += 1
                continue

            # 🔗 Parole spezzate con trattino
            if riga.endswith("-") and i + 1 < len(pagina):
                next_line = pagina[i + 1].strip()
                riga = riga[:-1] + next_line
                skip_next = True

            righe_pulite.append(riga)
            i += 1

        testo_completo += "\n" + "\n".join(righe_pulite)
    return testo_completo

def correggi_parole_spezzate(testo):
    # Rimuove trattino seguito da spazio e parola → "caccia- tori" → "cacciatori"
    testo = re.sub(r'-\s+', '', testo)
    return testo



def spezza_in_frasi(testo):
    righe = testo.split("\n")
    frasi = []
    buffer = ""

    for riga in righe:
        riga = riga.strip()
        if not riga:
            continue

        # Se è un titolo numerato (es. 1. Titolo o 2.3. Titolo)
        if re.match(r'^\d+(\.\d+)*\s+', riga):
            if buffer:
                # Aggiungi eventuale frase precedente completata
                frasi.extend(re.findall(r'[A-ZÀ-Ú][^.!?]*[.!?]', buffer))
                buffer = ""
            frasi.append(riga)  # Mantieni titolo intero
        else:
            buffer += " " + riga

    # Ultimo buffer
    if buffer:
        frasi.extend(re.findall(r'[A-ZÀ-Ú][^.!?]*[.!?]', buffer))

    return [f.strip() for f in frasi]
def filtra_didascalie_residue(frasi):
    frasi_filtrate = []
    for frase in frasi:
        parole = frase.strip().split()

        # Rimuove frasi molto brevi e senza verbi
        if len(parole) <= 3 and not re.search(r"\b(è|ha|sono|era|si|vede|hanno|c'è|ci sono|appare|presenta)\b", frase, re.IGNORECASE):
            continue

        # Rimuove frasi di 2 parole, entrambe capitalizzate, senza punteggiatura finale
        if (
            len(parole) == 2
            and all(p[0].isupper() for p in parole)
            and not frase.endswith(('.', '!', '?'))
        ):
            continue

        # Esclude frasi che sembrano etichette brevi
        if (
            frase.istitle()
            and not frase.endswith(('.', '!', '?'))
            and len(parole) <= 4
        ):
            continue

        frasi_filtrate.append(frase)

    return frasi_filtrate


def traduci_frasi(frasi):
    traduttore = GoogleTranslator(source='it', target='en')
    tradotte = []
    for frase in frasi:
        try:
            tradotte.append(traduttore.translate(frase))
        except Exception as e:
            tradotte.append(f"[TRANSLATION ERROR] {frase}")
    return tradotte

def salva_txt(frasi_tradotte, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        for frase in frasi_tradotte:
            f.write(frase + "\n")

def processa_pdf(pdf_path, output_txt_path, start_page=1):
    print(f"Estrazione testo da pagina {start_page} in poi...")
    testo_per_pagina = estrai_testo_due_colonne(pdf_path, start_page=start_page)

    print("Rilevamento piè di pagina...")
    piedipagina = rileva_piedipagina(testo_per_pagina)

    print("Pulizia testo...")
    testo_pulito = pulisci_testo(testo_per_pagina, piedipagina)

    # ✅ Corregge spezzature come "caccia- tori"
    testo_pulito = correggi_parole_spezzate(testo_pulito)

    print("Divisione in frasi...")
    frasi = spezza_in_frasi(testo_pulito)

    print("Filtro delle didascalie residue...")
    frasi = filtra_didascalie_residue(frasi)

    #print("Traduzione in inglese...")
    #frasi_tradotte = traduci_frasi(frasi)

    print("Salvataggio file TXT...")
    #salva_txt(frasi_tradotte, output_txt_path)
    salva_txt(frasi, output_txt_path)
    print(f"✅ Fatto! File salvato in: {output_txt_path}")

# ESEMPIO DI UTILIZZO
if __name__ == "__main__":
    pdf_input = "Manuale FISE.pdf"
    output_txt = "Horse_book_v2.txt"
    pagina_iniziale = int(input("Da quale pagina iniziare? (1-based index): "))
    processa_pdf(pdf_input, output_txt, start_page=pagina_iniziale)
