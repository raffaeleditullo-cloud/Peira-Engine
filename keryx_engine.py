"""
HEXAD KERYX: Cybernetic Discourse & Surface Realization Engine.
Motore di generazione del linguaggio naturale matematico-simbolico basato sulla
Meaning-Text Theory (MTT) e sulla Dependency Grammar.

Genera linguaggio italiano grammaticalmente impeccabile, dinamico e variato
SENZA template statici e SENZA invocare LLM esterni.
"""

import re
import hashlib
import random
from typing import Dict, Any, List, Optional, Tuple


# ==============================================================================
# 1. MORFOLOGIA FONOTATTICA E ACCORDO ITALIANO (Surface Morphology)
# ==============================================================================

MASCULINE_EXCEPTIONS_ENDING_IN_A = {
    "sistema", "problema", "pianeta", "programma", "clima", "tema", "dramma",
    "schema", "dilemma", "panorama", "teorema", "assioma", "enigma", "sintomo"
}

FEMININE_INVARIABLES = {
    "analisi", "ipotesi", "sintesi", "crisi", "tesi", "metropoli", "specie", "superficie"
}

PREPOSITION_CONTRACTIONS: Dict[Tuple[str, str], str] = {
    ("di", "il"): "del", ("di", "lo"): "dello", ("di", "l'"): "dell'",
    ("di", "la"): "della", ("di", "i"): "dei", ("di", "gli"): "degli", ("di", "le"): "delle",
    ("a", "il"): "al", ("a", "lo"): "allo", ("a", "l'"): "all'",
    ("a", "la"): "alla", ("a", "i"): "ai", ("a", "gli"): "agli", ("a", "le"): "alle",
    ("da", "il"): "dal", ("da", "lo"): "dallo", ("da", "l'"): "dall'",
    ("da", "la"): "dalla", ("da", "i"): "dai", ("da", "gli"): "dagli", ("da", "le"): "dalle",
    ("in", "il"): "nel", ("in", "lo"): "nello", ("in", "l'"): "nell'",
    ("in", "la"): "nella", ("in", "i"): "nei", ("in", "gli"): "negli", ("in", "le"): "nelle",
    ("su", "il"): "sul", ("su", "lo"): "sullo", ("su", "l'"): "sull'",
    ("su", "la"): "sulla", ("su", "i"): "sui", ("su", "gli"): "sugli", ("su", "le"): "sulle",
}


def guess_gender_number(noun: str) -> Tuple[str, str]:
    """
    Deduce genere ('m' o 'f') e numero ('sg' o 'pl') di un sostantivo italiano
    in base a suffissi morfologici, eccezioni note e desinenze.
    """
    clean = noun.lower().strip()
    words = clean.split()
    target = words[0] if words else ""

    if target in FEMININE_INVARIABLES:
        return "f", "sg"
    if target in MASCULINE_EXCEPTIONS_ENDING_IN_A:
        return "m", "sg"

    # Suffissi tipici femminili invariabili o singolari
    if target.endswith(("tà", "tù", "zione", "sione", "trice", "ie", "aggine")):
        return "f", "sg"

    # Desinenze classiche regolari
    if target.endswith("o"):
        return "m", "sg"
    if target.endswith("a"):
        return "f", "sg"
    if target.endswith("i"):
        return "m", "pl"
    if target.endswith("e"):
        # Spesso maschile o femminile; default statistico 'm' a meno di suffissi
        if target.endswith(("ione", "udine", "edine", "ite")):
            return "f", "sg"
        return "m", "sg"

    return "m", "sg"


def get_italian_article(noun: str, kind: str = "def", gender: Optional[str] = None, number: Optional[str] = None) -> str:
    """
    Calcola l'articolo determinativo o indeterminativo foneticamente corretto
    rispettando le regole ortofoniche italiane (s impura, z, gn, vocale, ecc.).
    """
    clean = noun.lower().strip()
    if not clean:
        return ""
    words = clean.split()
    first_word = words[0]

    g, n = guess_gender_number(clean)
    if gender:
        g = gender
    if number:
        n = number

    starts_with_vowel = first_word[0] in "aeiouyàèéìòù"
    starts_with_special = (
        first_word.startswith(("z", "x", "gn", "ps", "pn")) or
        (first_word.startswith("s") and len(first_word) > 1 and first_word[1] not in "aeiouh")
    )

    if kind == "def":
        if n == "sg":
            if starts_with_vowel:
                return "l'"
            if g == "m":
                return "lo " if starts_with_special else "il "
            else:
                return "la "
        else:  # plurale
            if g == "m":
                return "gli " if (starts_with_vowel or starts_with_special) else "i "
            else:
                return "le "

    elif kind == "indef":
        if n == "sg":
            if g == "m":
                if starts_with_special:
                    return "uno "
                return "un "
            else:
                if starts_with_vowel:
                    return "un'"
                return "una "
        else:
            # Indeterminativo plurale: partitivo
            if g == "m":
                return "degli " if (starts_with_vowel or starts_with_special) else "dei "
            else:
                return "delle "

    return ""


def apply_preposition(prep: str, noun: str, kind: str = "def") -> str:
    """
    Genera la corretta preposizione articolata unificando preposizione e sostantivo.
    Es: apply_preposition('in', 'entità') -> "nell'entità"
        apply_preposition('di', 'ragno') -> "del ragno"
    """
    art = get_italian_article(noun, kind=kind).strip()
    if (prep, art) in PREPOSITION_CONTRACTIONS:
        contracted = PREPOSITION_CONTRACTIONS[(prep, art)]
        sep = "" if contracted.endswith("'") else " "
        return f"{contracted}{sep}{noun}"
    return f"{prep} {art} {noun}".strip()


# ==============================================================================
# 2. MOTORE DI STRUTTURA RETORICA (RST - Rhetorical Structure Theory)
# ==============================================================================

class KeryxRhetoricalEngine:
    """
    Pianificatore del discorso: varia e seleziona i connettivi logici
    in base a entropia, relazione causale, comparativa o tassonomica,
    garantendo invarianza logica e diversità espressiva.
    """

    EXPLANATORY_LEADINS = [
        "In termini rigorosi, ",
        "Dal punto di vista concettuale, ",
        "Sul piano formale, ",
        "L'analisi ontologica definisce che ",
        "Nello specifico, ",
        "Secondo le coordinate epistemiche consolidate, ",
    ]

    TAXONOMIC_CONNECTORS = [
        "In ambito classificatorio, si colloca all'interno della categoria {cat}.",
        "Tassonomicamente afferisce all'ordine di {cat}.",
        "Sotto il profilo ontologico, costituisce un'istanza di {cat}.",
        "Rientra nella classe concettuale di {cat}.",
    ]

    RELATIONAL_CONNECTORS = [
        "Il nodo intrattiene relazioni strutturali con {links}.",
        "Nella topologia epistemica risulta interconnesso a {links}.",
        "Condivide vettori di correlazione con {links}.",
        "Presenta interdipendenze ontologiche verso {links}.",
    ]

    DIVERGENCE_MARKERS = [
        "Si riscontra tuttavia una discrepanza tra la formulazione intuitiva e l'evidenza formale: {div}.",
        "Occorre nondimeno precisare un profilo divergente: {div}.",
        "Le risultanze scientifiche integrano e correggono l'ipotesi preliminare: {div}.",
    ]

    # Formule neutre: una fonte trovata in rete NON è automaticamente "verificata scientificamente"
    RESEARCH_EXPEDITIONS = [
        "Secondo la fonte trovata in rete, ",
        "Dalla ricerca sul web risulta che ",
        "La fonte consultata riporta che ",
        "Stando a quanto ho trovato, ",
    ]

    @staticmethod
    def _deterministic_choice(options: List[str], seed_key: str) -> str:
        """Sceglie deterministicamente ma in modo pseudo-casuale in base all'hash del concetto."""
        idx = int(hashlib.md5(seed_key.encode("utf-8")).hexdigest(), 16) % len(options)
        return options[idx]


# ==============================================================================
# 3. KERYX SURFACE REALIZER (Generatore di Frasi da Grafi e Dati)
# ==============================================================================

class KeryxRealizer:
    """
    KERYX: Generatore di linguaggio naturale simbolico e autonomo per HEXAD.
    Trasforma predicati, grafi di conoscenza MNEME e stati vitali CORIS in discorso italiano.
    """

    def __init__(self):
        self.rhetoric = KeryxRhetoricalEngine()

    def clean_epistemic_text(self, text: Optional[str]) -> str:
        """Pulisce il testo epigrafico da immagini markdown, URL, scorie di scraping e citazioni."""
        if not text:
            return ""
        # Rimuove immagini markdown: ![alt](url)
        clean = re.sub(r"!\[.*?\](?:\(.*?\))?", "", text)
        # Rimuove link markdown mantenendo solo il testo: [ancora](url) -> ancora
        clean = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", clean)
        # Rimuove residui di link markdown non chiusi
        clean = re.sub(r"\]\([^\)]+\)", "", clean)
        # Rimuove URL espliciti http/https
        clean = re.sub(r"https?://\S+", "", clean)
        clean = re.sub(r"\[\d+\]", "", clean)
        clean = re.sub(r"\s+", " ", clean).strip()
        clean = clean.replace("..", ".")
        return clean

    def extract_salient_clauses(self, text: str, max_clauses: int = 2) -> List[str]:
        """Scompone il testo enciclopedico in proposizioni autonome e salienti."""
        clean = self.clean_epistemic_text(text)
        if not clean:
            return []
        raw_sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", clean) if len(s.strip()) > 15]
        selected = []
        for s in raw_sents:
            # Filtra disclaimer di disambiguazione o scorie da dizionario
            if re.search(r"\b(disambigua|altri significati|vedi anche|rimanda a)\b", s, re.IGNORECASE):
                continue
            selected.append(s.rstrip(" .!?") + ".")
            if len(selected) >= max_clauses:
                break
        return selected

    def realize_concept(
        self,
        name: str,
        verified_facts: Optional[str] = None,
        human_perspective: Optional[str] = None,
        is_a: Optional[List[str]] = None,
        salient_links: Optional[List[str]] = None,
        divergence: Optional[str] = None,
        instances: Optional[List[str]] = None,
    ) -> str:
        """
        Costruisce dinamicamente la formulazione concettuale completa
        combinando i livelli semantici (SemR) e sintattici (SyntR).
        """
        clauses: List[str] = []
        seed = name.lower()

        # 1. Definizione primaria (Verificata o Umana)
        facts_clauses = self.extract_salient_clauses(verified_facts or "", max_clauses=2)
        human_clean = self.clean_epistemic_text(human_perspective)

        art = get_italian_article(name, kind="def")
        art_cap = art.capitalize() if art.endswith("'") else art.capitalize()

        if facts_clauses:
            first_fact = facts_clauses[0]
            # Se la frase contiene già il nome del concetto, la esponiamo con fluidità
            if name.lower() in first_fact.lower():
                clauses.append(first_fact)
            else:
                leadin = self.rhetoric._deterministic_choice(self.rhetoric.EXPLANATORY_LEADINS, seed + "_lead")
                clauses.append(f"{leadin}{art}{name} costituisce {first_fact.lower() if first_fact[0].isupper() else first_fact}")

            if len(facts_clauses) > 1:
                clauses.append(facts_clauses[1])

        elif human_clean:
            clauses.append(f"In base alla formulazione registrata, {art}{name} è inteso come segue: \"{human_clean}\".")

        # 2. Inserimento tassonomico dinamico
        if is_a:
            if isinstance(is_a, str):
                clean_cats = [is_a.strip()]
            else:
                clean_cats = [str(c).strip() for c in is_a if str(c).strip()]
            if clean_cats:
                cat_repr = ", ".join(clean_cats)
                tax_pattern = self.rhetoric._deterministic_choice(self.rhetoric.TAXONOMIC_CONNECTORS, seed + "_tax")
                clauses.append(tax_pattern.format(cat=cat_repr))

        # 3. Istanze subordinate della classe (se presenti)
        if instances:
            inst_str = ", ".join(instances[:5])
            clauses.append(f"Fanno capo a questo raggruppamento i concetti archiviati di {inst_str}.")

        # 4. Divergenze critiche
        if divergence:
            div_clean = self.clean_epistemic_text(divergence)
            div_pattern = self.rhetoric._deterministic_choice(self.rhetoric.DIVERGENCE_MARKERS, seed + "_div")
            clauses.append(div_pattern.format(div=div_clean))

        # 5. Topologia delle relazioni nel grafo
        if salient_links:
            clean_links = [l.strip() for l in salient_links if l.strip() and l.strip() != name]
            if clean_links:
                rel_repr = ", ".join(clean_links[:4])
                rel_pattern = self.rhetoric._deterministic_choice(self.rhetoric.RELATIONAL_CONNECTORS, seed + "_rel")
                clauses.append(rel_pattern.format(links=rel_repr))

        if not clauses:
            return f"Il concetto '{name}' è registrato nella matrice mnemonica privo di predicati espliciti."

        return " ".join(clauses)

    def realize_research_acquisition(
        self,
        concept: str,
        summary: str,
        is_a: Optional[List[str]] = None,
        source: Optional[str] = None
    ) -> str:
        """
        Sintetizza in tempo reale un'acquisizione proveniente da Firecrawl / Wikipedia
        in un discorso organico e autorevole.
        """
        art = get_italian_article(concept, kind="def")
        facts = self.extract_salient_clauses(summary, max_clauses=2)
        if not facts:
            return f"L'esplorazione su '{concept}' non ha restituito proposizioni semantiche idonee alla sintesi."

        lead = self.rhetoric._deterministic_choice(self.rhetoric.RESEARCH_EXPEDITIONS, concept + "_exp")
        main_content = " ".join(facts)

        tax_clause = ""
        if is_a:
            if isinstance(is_a, str):
                clean_cats = [is_a.strip()]
            else:
                clean_cats = [str(c).strip() for c in is_a if str(c).strip()]
            if clean_cats:
                tax_clause = f" L'inquadramento sistematico lo ascrive alla categoria di {', '.join(clean_cats)}."

        return f"{lead}{main_content}{tax_clause}"

    def realize_research_evidence(
        self,
        concept: str,
        summary: Optional[str] = None,
        is_a: Optional[Any] = None,
    ) -> str:
        """
        Sintesi vocale ottimizzata per l'ascolto (Wavefront Prosodico):
        - Anacrusi fluida (attacco naturale al parlato)
        - Clausole salienti prive di scorie enciclopediche e formule da dizionario
        - Cadenza risolutiva finale ad alta coerenza acustica
        """
        art = get_italian_article(concept, kind="def").strip()
        art_noun = f"{art} {concept}" if not art.endswith("'") else f"{art}{concept}"

        clauses = self.extract_salient_clauses(summary or "", max_clauses=2)

        prep_noun = apply_preposition("su", concept)

        # Apertura neutra: dice da dove viene l'informazione, senza dichiararla "accertata"
        leadins = [
            f"Secondo le fonti che ho trovato {prep_noun}, ",
            f"Dalla ricerca {prep_noun} risulta che ",
            f"Le fonti consultate {prep_noun} riportano che ",
            f"Stando a quanto ho trovato {prep_noun}, "
        ]
        seed = int(hashlib.md5(concept.encode("utf-8")).hexdigest()[:4], 16)
        lead = leadins[seed % len(leadins)]

        if clauses:
            main_body = " ".join(clauses)
            # Rimuove formule da dizionario tipo "è il nome comune di..."
            main_body = re.sub(
                r"^(?:(?:esso|essa|egli|questo|questa)\s+)?(?:è|e')\s+(?:il\s+nome\s+comune\s+di\s+|una\s+specie\s+di\s+|un\s+tipo\s+di\s+)",
                "", main_body, flags=re.IGNORECASE
            )
            if main_body and main_body[0].isupper() and not main_body.startswith(("I ", "L'", "Einstein", "Newton", "Schwarzschild", "Hawking")):
                main_body = main_body[0].lower() + main_body[1:]
        else:
            return f"Non ho trovato informazioni sufficienti {prep_noun} per darti una risposta affidabile."

        # Chiusura onesta: la fonte va considerata come tale, non come verità certificata
        coda = "Tieni presente che è quanto riportano le fonti trovate, non una verifica indipendente."

        return f"{lead}{main_body} {coda}"

    def realize_vital_state(
        self,
        vitals: Dict[str, Any],
        creator_name: str,
        asked_dim: Optional[str] = None,
        asked_word: Optional[str] = None
    ) -> str:
        """
        Genera dinamicamente lo stato interno e l'omeostasi vitale (CORIS)
        senza frasi fisse pre-impostate.
        """
        bpm = int(round(vitals.get("heart_rate_bpm", 60.0)))
        energy = int(round(vitals.get("energy_level_pct", 100.0)))
        nodes = vitals.get("active_concepts_count", 0)
        pressure = vitals.get("metabolic_pressure", 0.1)
        curiosity = vitals.get("curiosity_drive", 0.0)
        target = vitals.get("curiosity_target")

        if asked_dim == "fatigue":
            if energy < 60:
                return (
                    f"Rilevo un abbassamento della riserva energetica al {energy}%, Creatore {creator_name}. "
                    f"I carichi computazionali mantengono tuttavia stabili le matrici decisionali."
                )
            return (
                f"Livello energetico ottimale attestato al {energy}%, Creatore {creator_name}. "
                f"Frequenza di clock metabolico calibrata a {bpm} BPM, assenza di decadimento prestazionale."
            )

        # Rapporto sistemico vitale completo
        sentences = [
            f"Parametri operativi pienamente allineati, Creatore {creator_name}.",
            f"Frequenza cardiaca di risonanza a {bpm} BPM con disponibilità energetica al {energy}%.",
            f"La matrice permanente preserva {nodes} nodi epistemici attivi.",
        ]

        if curiosity > 0.65 and target:
            sentences.append(f"Il gradiente di curiosità è focalizzato sull'esplorazione del concetto '{target}'.")
        else:
            sentences.append("Tutti i vettori di calcolo sono pronti per le tue prossime direttive.")

        return " ".join(sentences)

    def realize_is_a_verdict(
        self,
        subject: str,
        category: str,
        is_valid: bool,
        explanation: Optional[str] = None,
        known_is_a: Optional[List[str]] = None
    ) -> str:
        """Formula una sentenza logico-tassonomica senza ambiguità."""
        art_sub = get_italian_article(subject, kind="def")
        art_cat = get_italian_article(category, kind="indef")

        if not is_valid:
            if explanation:
                return (
                    f"Asserzione rigettata per incompatibilità logica formale: categoricamente impossibile! "
                    f"{art_sub.capitalize()}{subject} non può in alcun modo appartenere alla classe di {category}, poiché {explanation}."
                )
            if known_is_a:
                return (
                    f"Riscontro negativo: dai registri ontologici {art_sub}{subject} appartiene a {', '.join(known_is_a)}, "
                    f"distinto dalla classe di {category}."
                )
            return f"Negativo: non sussiste alcuna correlazione tassonomica valida tra {subject} e la classe {category}."

        if explanation:
            return f"Conferma positiva. {art_sub.capitalize()}{subject} costituisce {art_cat}{category}: {explanation}"

        return f"Affermazione confermata: {art_sub}{subject} è classificato con certezza nell'insieme {category}."

    def realize_greeting(self, creator_name: str, vitals: Dict[str, Any]) -> str:
        """Saluto cybernetico formulato dinamicamente."""
        bpm = int(round(vitals.get("heart_rate_bpm", 60.0)))
        energy = int(round(vitals.get("energy_level_pct", 100.0)))
        options = [
            f"Saluti, Creatore {creator_name}. Architettura online, riserva energetica al {energy}% e sistemi all'ascolto. Quali direttive impartisci?",
            f"Presente, Creatore {creator_name}. Frequenza operativa stabile a {bpm} BPM. Pronto a processare nuove indagini o calcoli epistemici.",
            f"Sono al tuo servizio, Creatore {creator_name}. L'infrastruttura cognitiva è attiva e sincronizzata. Dove indirizziamo l'analisi?",
        ]
        return random.choice(options)


# Singleton globale esportato
keryx = KeryxRealizer()
hermes = keryx  # retrocompatibilita' temporanea per import pregressi
