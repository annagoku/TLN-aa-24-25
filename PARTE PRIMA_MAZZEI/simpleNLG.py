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


# Costruisce una frase con solo un attributo
# es. sp.build_phrase("Good morning") --> "Good morning"
def build_phrase(complemento):
    phrase = init()

    phrase.setFeature(featureName=simplenlg.Feature.FORM, featureValue=simplenlg.ABC)
    phrase.setTense(simplenlg.Tense.PRESENT)

    phrase.setComplement(complemento)
    return realize_output(phrase)

# Costruisce una frase normale completa
# es. sp.build_phrase_complete("I", "be", "Lara Croft")
def build_phrase_complete(soggetto, verbo, complemento):
    phrase = init()

    phrase.setFeature(featureName=simplenlg.Feature.FORM, featureValue=simplenlg.ABC)
    phrase.setTense(simplenlg.Tense.PRESENT)

    phrase.setVerb(verbo)
    phrase.setSubject(soggetto)
    phrase.setComplement(complemento)

    return realize_output(phrase)

# Costruisce una frase di tipo interrogativo, usato per chiedere un nome proprio
# es. (sp.ask_info("name") --> "What is your name?"
def ask_info(complemento):
    phrase = init()

    phrase.setVerb("be")
    phrase.setObject("your")

    phrase.setFeature(featureName=simplenlg.Feature.INTERROGATIVE_TYPE,
                      featureValue=simplenlg.InterrogativeType.WHAT_SUBJECT)
    phrase.setTense(simplenlg.Tense.PRESENT)
    phrase.setComplement(complemento)

    return realize_output(phrase)

# Costruisce una frase relativa a una mancata o scorretta risposta da parte dell'utente.
# usato per ripetere all'utente di inserire il nome
# es. sp.no_answer("your", "name") --> "You must tell me your name."
def no_answer(obj, complmentent):
    phrase = init()

    phrase.setFeature(featureName=simplenlg.Feature.MODAL, featureValue="must")
    phrase.setVerb("tell")
    phrase.setObject(obj)
    phrase.setSubject("you")
    phrase.setComplement(complmentent)
    phrase.setIndirectObject("me")

    return realize_output(phrase)

# Costruisce una frase di tipo interrogativo con un verbo e un soggetto
# es. sp.verb_subj("study", "you") --> "Did you study?"
def verb_subj(verb, subject):
    phrase = init()

    phrase.setFeature(featureName=simplenlg.Feature.INTERROGATIVE_TYPE, featureValue=simplenlg.InterrogativeType.YES_NO)
    phrase.setTense(simplenlg.Tense.PAST)
    phrase.setVerb(verb)
    phrase.setSubject(subject)

    return realize_output(phrase)


# Costruisce la frase che da inizio all'interrogazione
#  I'll ask you for 3 questions about my character
def start_exam():
    lexicon = simplenlg.Lexicon.getDefaultLexicon()
    nlgFactory = simplenlg.NLGFactory(lexicon)

    # Creazione della frase
    np_questions = nlgFactory.createNounPhrase("question")
    np_questions.setPlural(True)  # "questions"
    np_questions.addPreModifier("3")  # "3 questions"

    np_complement = nlgFactory.createNounPhrase("about", "character")  # "my character"
    np_complement.addPreModifier("my")  # "about my character"

    proposition = nlgFactory.createClause("I", "ask for", np_questions)  
    proposition.addComplement(np_complement)  # "...about my character"
    proposition.setFeature(simplenlg.Feature.TENSE, simplenlg.Tense.FUTURE)  # Futuro

    output = realize_output(proposition)
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



def generate_list_question(quantity,subject, context=None):
    """
    Genera una domanda interrogativa per elenchi usando simpleNLG.
    
    :param quantity: Quantità minima richiesta (es. "two")
    :param items: Oggetto della domanda (es. "weapons")
    :param context: Contesto specifico (es. "of Lara Croft", "of the movie Tomb Raider: The Cradle of Life")
    :return: Una frase interrogativa ben formata.
    """
    # Crea la frase principale
    phrase = init()
    phrase = nlgFactory.createClause()
    object_to_list=nlgFactory.createNounPhrase(subject)
    object_to_list.setPlural(True)
    object_to_list.addPreModifier(quantity)
    phrase.setSubject(object_to_list)  # Es. "at least two weapons"
    phrase.setVerb("be")  # Imposta "are"
    phrase.setFeature(simplenlg.Feature.NUMBER, simplenlg.NumberAgreement.PLURAL)

    # Aggiunge il contesto (se esiste)
    if context:
        context_np = nlgFactory.createNounPhrase(context)
        pp = nlgFactory.createPrepositionPhrase()
        pp.setPreposition("of")
        pp.setObject(context_np)
        object_to_list.addPostModifier(pp)

    # Imposta la domanda con "What"
    phrase.setFeature(simplenlg.Feature.INTERROGATIVE_TYPE, simplenlg.InterrogativeType.WHAT_OBJECT)

    # Realize the sentence (convert it to text)
    output = realize_output(phrase)
    return output

def generate_name_question(entity):
    """
    Genera una domanda per chiedere il nome di una persona o entità.

    :param entity: Il soggetto terza persona della domanda (es.  "Lara Croft's father")
    :return: Frase interrogativa ben formata.
    """
    # Crea la frase principale
    phrase = init()
    phrase.setSubject(entity + "'s name")  # "Lara Croft's father's name"
    phrase.setVerb("be")  # Imposta "is"

    # Imposta la domanda con "What"
    phrase.setFeature(simplenlg.Feature.INTERROGATIVE_TYPE, simplenlg.InterrogativeType.WHAT_OBJECT)

    # Realize the sentence (convert it to text)
    output = realize_output(phrase)
    return output

def generate_how_many_question(subject, entity):
    """
    Genera una domanda "How many ... have been made about ...?" in modo parametrico.
    :param entity: L'entità di cui si vuole sapere la quantità (es. "film")
    :param subject: L'argomento della domanda (es. "Lara Croft")
    :return: Stringa con la frase generata
    """
    
    phrase=init()
    # Creazione della frase principale
    phrase=nlgFactory.createClause()
    # Crea il NounPhrase (frase nominale) con il subject
    sub=nlgFactory.createNounPhrase(subject)
    
     # Imposta il plurale per il sostantivo se necessario
    sub.setPlural(True)  
    phrase.setSubject(sub)
    phrase.setVerb("be")
    phrase.setFeature(simplenlg.Feature.TENSE, simplenlg.Tense.PRESENT)
    
    
    # Aggiungi complemento
    comp=nlgFactory.createNounPhrase(entity)
    comp.addPreModifier("there about")
    phrase.addComplement(comp)
    
    # Imposta la frase come interrogativa e aggiunge "How many"
    phrase.setFeature(simplenlg.Feature.INTERROGATIVE_TYPE, simplenlg.InterrogativeType.HOW_MANY)
    
    # Realizza la frase (la converte in testo)
    output = realize_output(phrase)
    return output


def generate_true_false_question(subject, verb, complement):
    """
    Genera una domanda vero/falso in modo parametrico.
    :param subject: Il soggetto principale della domanda (es. "Lara Croft")
    :param location: Il luogo o complemento della frase (es. "an archeologist")
    :param verb: L'azione compiuta dal soggetto (es. "be")
    :return: Stringa con la domanda generata
    """
    phrase=init()
    
    # Imposta la domanda vero/falso in forma più semplice
    phrase.setSubject(subject)
    phrase.setVerb(verb)
    phrase.setFeature(simplenlg.Tense.PRESENT, True)
    phrase.addComplement(complement)
    phrase.setFeature(simplenlg.Feature.INTERROGATIVE_TYPE, simplenlg.InterrogativeType.YES_NO)
    
     # Realize the sentence (convert it to text)
    output = realize_output(phrase)
    return output

def generate_bravery_sentence():
    # Inizializza la frase
    phrase = nlgFactory.createClause()
    
    # Soggetto: "you"
    phrase.setSubject("you")
    
    # Verbo: "be"
    phrase.setVerb("be")
    
    # Negazione
    phrase.setFeature(simplenlg.Feature.NEGATED, True)

    # Complemento: "brave enough for this challenge"
    brave_adj = nlgFactory.createAdjectivePhrase("brave")
    brave_adj.addPostModifier("enough")
    
    # Preposizione: "for this challenge"
    pp = nlgFactory.createPrepositionPhrase()
    pp.setPreposition("for")
    pp.setObject(nlgFactory.createNounPhrase("this", "challenge"))
    
    # Aggiungi tutto al complemento del verbo
    phrase.addComplement(brave_adj)
    phrase.addComplement(pp)
    
    return realize_output(phrase)

def generate_see_you_sentence():
    # Crea una clausola
    phrase = nlgFactory.createClause()
    
    # Imposta il verbo come imperativo
    phrase.setVerb("see")
    phrase.setFeature(simplenlg.Feature.FORM, simplenlg.Form.IMPERATIVE)

    # Aggiungi l'oggetto diretto "you"
    phrase.setObject("you")

    # Aggiungi il complemento "next time"
    phrase.addComplement("next time")
    
    return realize_output(phrase)

def generate_gain_points_sentence():
    # Crea la frase
    phrase = nlgFactory.createClause()
    
    # Soggetto
    phrase.setSubject("you")
    
    # Verbo
    phrase.setVerb("gain")
    
    # Oggetto: "10 points"
    object_np = nlgFactory.createNounPhrase("point")
    object_np.setPlural(True)
    object_np.addPreModifier("10")
    phrase.setObject(object_np)
    
    return realize_output(phrase)

def generate_0_10_point_sentence():
    # Frase principale: "You lied"
    main_clause = nlgFactory.createClause()
    main_clause.setSubject("you")
    main_clause.setVerb("lie")
    main_clause.setFeature(simplenlg.Feature.TENSE, simplenlg.Tense.PAST)

    # Frase subordinata: "you said you had studied"
    embedded_clause = nlgFactory.createClause()
    embedded_clause.setSubject("you")
    embedded_clause.setVerb("say")
    embedded_clause.setFeature(simplenlg.Feature.TENSE, simplenlg.Tense.PAST)

    # Subordinata oggettiva: "you had studied"
    inner_clause = nlgFactory.createClause()
    inner_clause.setSubject("you")
    inner_clause.setVerb("study")
    inner_clause.setFeature(simplenlg.Feature.TENSE, simplenlg.Tense.PAST)
    #inner_clause.setFeature(simplenlg.Feature.PERFECT, True)

    # Aggiungi "you had studied" come oggetto di "you said"
    embedded_clause.setObject(inner_clause)

    # Inserisci "when you said you had studied" come complemento della principale
    main_clause.addComplement("when " + realize_output(embedded_clause))

    return realize_output(main_clause)

def generate_20_points_sentence():
    # Soggetto: "my adventures"
    subject_np = nlgFactory.createNounPhrase("my", "adventure")
    subject_np.setPlural(True)

    # Frase principale
    clause = nlgFactory.createClause()
    clause.setSubject(subject_np)
    clause.setVerb("be")

    # Predicato: "still too dangerous"
    adj_phrase = nlgFactory.createAdjectivePhrase("dangerous")
    adj_phrase.addPreModifier("still too")
    
    

    # Aggiunge "for you" come complemento
    pp = nlgFactory.createPrepositionPhrase()
    pp.setPreposition("for")
    pp.setObject("you")

    # Assegna il complemento predicativo
    clause.setComplement(adj_phrase)
    clause.addComplement(pp)

    return realize_output(clause)

def generate_30_points_sentence():
   # Crea il soggetto
    subject = nlgFactory.createNounPhrase("you")

    # Crea la frase principale
    clause = nlgFactory.createClause()
    clause.setSubject(subject)
    clause.setVerb("be")
    clause.setComplement("ready")

    # Crea la prepositional phrase: "for my next mission"
    pp = nlgFactory.createPrepositionPhrase()
    pp.setPreposition("for")
    pp.setObject("my next mission")

    # Aggiunge il complemento preposizionale
    clause.addPostModifier(pp)


    return realize_output(clause)