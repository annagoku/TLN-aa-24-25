import simplenlg

lexicon=""
nlgFactory=""
phrase=""
"""
Lista di tutti i metodi implementati con la libreria SimpleNLG per stampare le risposte di Lara
"""

# inizializza la frase con la libreria SimpleNLG
def init():
    global lexicon, nlgFactory, phrase
    lexicon = simplenlg.Lexicon.getDefaultLexicon()
    nlgFactory = simplenlg.NLGFactory(lexicon)
    phrase = simplenlg.SPhraseSpec(nlgFactory)
    return phrase

# Metodo che stampa la frase costruita in uno dei metodi precedenti
def realize_output(phrase):
    realizer = simplenlg.Realiser()
    output = realizer.realiseSentence(phrase)
    return output

def generate_when_question(subject, complement, verb):
    """
    Genera una domanda temporale ("When") come:
    - "When was Lara Croft born?"
    - "When did the first videogame of Lara Croft release?"
    
    :param subject: Il soggetto principale della domanda (es. "Lara Croft")
    :param complement: Il complemento (es. "the first videogame")
    :param verb: Il verbo principale (es. "be", "release", "born")
    :return: Stringa con la frase interrogativa generata
    """
    
    subject = subject.title()
    phrase = init()
    phrase = nlgFactory.createClause()

    # Crea soggetto
    subject_np = nlgFactory.createNounPhrase(subject)
    
    # Se esiste un complemento, aggiungilo come post-modificatore
    if complement:
        complement_np = nlgFactory.createNounPhrase(complement)
        pp = nlgFactory.createPrepositionPhrase()
        pp.setPreposition("of")
        pp.setObject(subject_np)
        complement_np.addPostModifier(pp)
        phrase.setSubject(complement_np)
    else:
        phrase.setSubject(subject_np)

    # Gestione speciale per "be" e "born"
    if verb.lower() in ["be", "was", "is"] or "born" in verb.lower():
        phrase.setVerb("be")
        phrase.setFeature(simplenlg.Feature.TENSE, simplenlg.Tense.PAST)
        phrase.setFeature(featureName=simplenlg.Feature.INTERROGATIVE_TYPE, featureValue=simplenlg.InterrogativeType.YES_NO)
        phrase.setComplement("born")
    else:
        phrase.setVerb(verb)
        phrase.setFeature(simplenlg.Feature.TENSE, simplenlg.Tense.PAST)
        phrase.setFeature(featureName=simplenlg.Feature.INTERROGATIVE_TYPE, featureValue=simplenlg.InterrogativeType.YES_NO)

    # Realizza la frase
    sentence = realize_output(phrase)

    # Assicura che inizi con "When"
    if not sentence.lower().startswith("when"):
        sentence = "When " + sentence[0].lower() + sentence[1:]

    # Assicura il punto interrogativo
    if not sentence.endswith("?"):
        sentence += "?"

    return sentence

print(generate_when_question("Lara Croft", "", "born"))
# Output: When was Lara Croft born?

print(generate_when_question("Lara Croft", "the first videogame", "release"))
# Output: When did the first videogame of Lara Croft release?
