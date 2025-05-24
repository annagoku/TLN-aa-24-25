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

def generate_when_question(subject, event): # funzionante ma può essere generalizzato meglio
    """
    Genera una domanda del tipo "When did Lara Croft start her adventure?"
    :param event: L'azione che si vuole interrogare (es. "start her adventure")
    :param subject: Il soggetto principale della domanda (es. "Lara Croft")
    :return: Stringa con la frase generata
    """
   
    subject=subject.title()
    phrase = init()
    phrase=nlgFactory.createClause()

    noun = nlgFactory.createNounPhrase(subject)  # Crea il nome
    noun.setFeature(simplenlg.Feature.PERSON, True)  # Indica che è un nome proprio
    
    phrase.setSubject(noun)  # Imposta il nome proprio come soggetto

    # Imposta il verbo
    phrase.setVerb("be")  # Necessario per le domande al passato
    phrase.setFeature(simplenlg.Feature.TENSE, simplenlg.Tense.PAST)
    #phrase.setFeature(simplenlg.Feature.PASSIVE, True)
    phrase.addComplement(event)

    # Trasforma in una domanda
    phrase.setFeature(featureName=simplenlg.Feature.INTERROGATIVE_TYPE, featureValue=simplenlg.InterrogativeType.YES_NO)

    # Realizza la frase base
    sentence = realize_output(phrase)

    # Aggiungi manualmente "When" davanti
    output = f"When {sentence.lower()}"

    return output



def generate_list_question(quantity,subject, context):
    """
    Genera una domanda interrogativa per elenchi usando simpleNLG.
    
    :param quantity: Quantità minima richiesta (es. "two")
    :param items: Oggetto della domanda (es. "weapons")
    :param context: Contesto specifico (es. "used by Lara Croft", "of the movie Tomb Raider: The Cradle of Life")
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
        phrase.addComplement(context)  # Es. "used by Lara Croft"

    # Imposta la domanda con "What"
    phrase.setFeature(simplenlg.Feature.INTERROGATIVE_TYPE, simplenlg.InterrogativeType.WHAT_OBJECT)

    # Realize the sentence (convert it to text)
    output = realize_output(phrase)
    return output

def generate_name_question(entity):
    """
    Genera una domanda per chiedere il nome di una persona o entità.

    :param entity: Il soggetto della domanda (es. "you", "Lara Croft's father")
    :return: Frase interrogativa ben formata.
    """
    # Crea la frase principale
    phrase = init()
    phrase.setSubject(entity + "'s name")  # Es. "your name", "Lara Croft's father's name"
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


def generate_true_false_question(subject, complement, action):
    """
    Genera una domanda vero/falso in modo parametrico.
    :param subject: Il soggetto principale della domanda (es. "London")
    :param location: Il luogo o complemento della frase (es. "the place")
    :param action: L'azione compiuta dal soggetto (es. "where Lara Croft looked for her father")
    :return: Stringa con la domanda generata
    """
    phrase=init()
    
    # Imposta la domanda vero/falso in forma più semplice
    phrase.setSubject(subject)
    phrase.setVerb("be")
    phrase.setFeature(simplenlg.Tense.PRESENT, True)
    phrase.addComplement(complement + " " + action)
    phrase.setFeature(simplenlg.Feature.INTERROGATIVE_TYPE, simplenlg.InterrogativeType.YES_NO)
    
     # Realize the sentence (convert it to text)
    output = realize_output(phrase)
    return output


