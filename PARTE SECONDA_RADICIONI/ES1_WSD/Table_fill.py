import nltk
from nltk.wsd import lesk
from nltk.corpus import semcor
from nltk.corpus.reader.wordnet import Lemma
import random as r
import re  #modulo regex
from nltk.corpus import wordnet as wn
from rich.console import Console
from rich.table import Table 
import util as u
import LeskAlgorithm as la

def populate_results_table(terms, N_WORDS):
    # Crea l'oggetto Console (per stampare nella console)
    console = Console()

    # Crea una tabella con il titolo
    table = Table(title="Risultati Disambiguazione", caption="Comparazione tra 'Defined_LESK' e 'nltk_LESK'")

    # Aggiungi colonne alla tabella
    table.add_column("Termine", style="cyan", no_wrap=True)
    table.add_column("Synset (SemCor)", style="magenta")
    table.add_column("Synset (Defined_LESK)", style="green")
    table.add_column("Synset (nltk_LESK)", style="yellow")
    table.add_column("Defined_LESK Corretto", style="bold green")
    table.add_column("nltk_LESK Corretto", style="bold red")

    # Variabili per tenere traccia delle correttezze
    code_correct_wsd = 0
    ntlk_correct_wds = 0

    # Aggiungi le righe alla tabella per ogni termine
    for elem in terms:
        # Esegui l'analisi di disambiguazione
        code_disambiguation = la.lesk_algorithm(elem[0], elem[2])  # LESK defined
        nltk_disambiguation = lesk(elem[2], elem[0], 'n')  # LESK NLTK

                # Confronti sicuri
        if code_disambiguation is None or elem[1] is None:
            code_result = "❌"
        else:
            code_result = "✔️" if code_disambiguation == elem[1] else "❌"

        if nltk_disambiguation is None or elem[1] is None:
            nltk_result = "❌"
        else:
            nltk_result = "✔️" if nltk_disambiguation == elem[1] else "❌"

        # Aggiunta riga alla tabella
        table.add_row(
            elem[0],
            str(elem[1]),
            str(code_disambiguation) if code_disambiguation else "Nessun risultato",
            str(nltk_disambiguation) if nltk_disambiguation else "Nessun risultato",
            code_result,
            nltk_result
        )


        # Conta i termini corretti
        code_correct_wsd = code_correct_wsd + 1 if elem[1] == code_disambiguation else code_correct_wsd
        ntlk_correct_wds = ntlk_correct_wds + 1 if (nltk_disambiguation is not None and elem[1] == nltk_disambiguation) else ntlk_correct_wds

    # Aggiungi le righe finali con le statistiche di accuratezza
    table.add_row("", "", "", "", "", "")
    table.add_row(
        "", 
        "Correttezza:", 
        f"{code_correct_wsd} su {N_WORDS}", 
        f"{ntlk_correct_wds} su {N_WORDS}",
        f"{int((code_correct_wsd / N_WORDS) * 100)}%", 
        f"{int((ntlk_correct_wds / N_WORDS) * 100)}%"
    )

    # Stampa la tabella
    console.print(table)

    return code_correct_wsd, ntlk_correct_wds