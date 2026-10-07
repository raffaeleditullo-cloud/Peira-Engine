"""
HEXAD Epistemic Verifier.
Modulo autonomo di fact-checking e consultazione enciclopedica aperta.
Interroga le API pubbliche italiane (Wikipedia) senza LLM,
estrae la tassonomia formale e rileva discrepanze logiche tra la visione
spiegata dall'umano e la tassonomia verificata.

Diviso in due fasi:
- fetch_summary(): l'unica operazione che va online
- analyze():       lavora solo su testo, quindi si può rifare dalla memoria senza ricercare
"""

import urllib.request
import urllib.error
import urllib.parse
import json
import re
import os
from typing import Dict, Any, Optional, List

# Parole "contenitore" che non sono la vera categoria ("un ordine di artropodi" -> "artropodi")
CONTAINER_WORDS = {
    "ordine", "genere", "famiglia", "classe", "tipo", "specie", "sottordine", "gruppo", "insieme",
    "termine", "parola", "tema", "concetto", "nome", "forma", "sorta", "parte", "serie", "modo",
    "regno", "dominio", "phylum", "divisione", "sottofamiglia", "superfamiglia"
}

JUNK_CATEGORY_WORDS = {
    "quella", "quello", "questo", "questa", "questi", "queste", "cosa", "chi", "cui", "ciò",
    "uno", "una", "tutto", "tutti", "qualcosa", "alcuni", "alcune", "molti", "molte", "altro", "altra", "altri", "altre",
    "all", "dell", "nell", "dall", "sull", "tale", "tali", "stesso", "stessa",
    "che", "non", "molto", "anche", "stato", "stata", "stati", "state", "senza", "sopra", "sotto",
    "rappresentano", "rappresenta", "costituiscono", "costituisce", "formano", "forma", "indicati", "indicato", "quando",
    "studiato", "acquisito", "appreso", "spiegato", "cercato", "trovato", "registrato", "formalizzato"
}


# Coppie tassonomiche compatibili in relazione gerarchica di inclusione (iperonimo/iponimo)
COMPATIBLE_HIERARCHIES = {
    frozenset({"animal", "mammifer"}),
    frozenset({"animal", "rettil"}),
    frozenset({"animal", "uccell"}),
    frozenset({"animal", "pesc"}),
    frozenset({"animal", "issett"}),
    frozenset({"animal", "insett"}),
    frozenset({"animal", "aracnid"}),
    frozenset({"animal", "vertebrat"}),
    frozenset({"animal", "invertebrat"}),
    frozenset({"organism", "animal"}),
    frozenset({"organism", "piant"}),
    frozenset({"vertebrat", "mammifer"}),
    frozenset({"vertebrat", "rettil"}),
    frozenset({"vertebrat", "uccell"}),
    frozenset({"vertebrat", "pesc"}),
    frozenset({"invertebrat", "insett"}),
    frozenset({"invertebrat", "aracnid"}),
}


def stem(word: str) -> str:
    """Radice grezza per confronti singolare/plurale (rettile/rettili -> 'rettil')."""
    w = (word or "").lower().strip()
    return w[:-1] if len(w) > 4 else w


def extract_is_a(text: Optional[str]) -> Optional[str]:
    """
    Estrae la categoria tassonomica dalla prima frase:
    - "X è un rettile che..." -> "rettile"
    - "I serpenti sono rettili squamati..." -> "rettili"
    - "un batterio del terreno" -> "batterio"
    - "un regno di organismi..." -> "organismi"
    - "Rappresentano la prima classe di vertebrati..." -> "vertebrati"
    - "Il termine macchina indica un dispositivo..." -> "dispositivo"
    - "un buco nero è un corpo celeste..." -> "corpo celeste"
    """
    if not text:
        return None
    first = re.split(r"(?<=[.!?])\s+", text.strip())[0].lower()

    # 1. Se c'è una copula o verbo predicativo
    m = re.search(
        r"\b(?:è|e'|sono|rappresenta|rappresentano|costituisce|costituiscono|indica|designa|definisce|identifica)\s+"
        r"(?:(?:comunemente|generalmente|spesso|solitamente|tradizionalmente|storicamente|principalmente)\s+)?"
        r"(?:(?:definito|definita|definiti|definite|considerato|considerata|considerati|considerate|noto|nota|noti|note|inteso|intesa|descritto|descritta)(?:\s+come)?\s+)?"
        r"(?:(?:la\s+prima|il\s+primo|una|un|uno|dei|degli|delle|il|lo|la|i|gli|le)\s+|un'|l')?"
        r"([a-zàèéìòù]+)"
        r"(?:\s+(?:di|dei|degli|delle|del|della|d'|su|per)?\s+([a-zàèéìòù]+))?",
        first
    )
    # 2. Se non c'è copula (es. utente ha spiegato 'un batterio del terreno' o 'rettile che striscia')
    if not m:
        m = re.search(
            r"^(?:(?:un|uno|una|dei|degli|delle|il|lo|la|i|gli|le)\s+|un'|l')?"
            r"([a-zàèéìòù]+)"
            r"(?:\s+(?:di|dei|degli|delle|del|della|d'|su|per)?\s+([a-zàèéìòù]+))?",
            first
        )
    if not m:
        return None

    w1, w2 = m.group(1), m.group(2)
    # Filtra avverbi terminanti in -mente
    if w1 and w1.endswith("mente"):
        return None
    # Caso speciale: corpo celeste
    if w1 == "corpo" and w2 in {"celeste", "nero", "umano", "rigido"}:
        return f"{w1} {w2}"
    # Se la prima parola è un contenitore (es. "regno di organismi"), usiamo la seconda
    if w1 in CONTAINER_WORDS and w2 and w2 not in JUNK_CATEGORY_WORDS and not w2.endswith("mente"):
        return w2
    if w1 not in CONTAINER_WORDS and w1 not in JUNK_CATEGORY_WORDS and len(w1) > 2:
        return w1
    return None


class EpistemicVerifier:
    def __init__(self, user_agent: str = "HEXAD-Cybernetic-Learner/1.0 (Autonomous Epistemic Bot)"):
        self.headers = {
            "User-Agent": user_agent,
            "Accept": "application/json"
        }
        self.env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        self._load_env()

    def _load_env(self):
        if os.path.exists(self.env_path):
            with open(self.env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        if k.strip() not in os.environ:
                            os.environ[k.strip()] = v.strip()

    @staticmethod
    def distill_epistemic_text(md: str, desc: str, concept: str) -> str:
        """Estrae una definizione enciclopedica pura, fluida e autorevole, eliminando scorie da dizionario."""
        c_lower = concept.lower().strip()

        # 1. Cerca nel markdown la riga di definizione primaria o enciclopedica
        best_line = None
        if md:
            for line in md.split("\n"):
                l = line.strip()
                if not l or l.startswith(("#", "[Salta", "[Scarica", "!", "|", "---")):
                    continue
                if "**1.**" in l or " 1. " in l or "s. f." in l or "s. m." in l or "essenza" in l.lower() or "indica" in l.lower() or "ente" in l.lower():
                    best_line = l
                    break

        raw = best_line or desc or ""

        # 2. Rimuovi convenzioni da dizionario cartaceo / web
        if "**1.**" in raw:
            raw = raw.split("**1.**", 1)[1]
        elif " 1. " in raw:
            raw = raw.split(" 1. ", 1)[1]
        elif "]" in raw and ("lat" in raw.lower() or "etim" in raw.lower() or "der." in raw.lower()):
            raw = raw.split("]", 1)[1]

        # Taglia alla seconda accezione per mantenere concisione
        if "**2.**" in raw:
            raw = raw.split("**2.**", 1)[0]
        elif " 2. " in raw:
            raw = raw.split(" 2. ", 1)[0]

        # Rimuovi link markdown preservando il testo: [informatica](url) -> informatica
        raw = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", raw)
        raw = re.sub(r"\([^\)]*https?:\/\/[^\)]*\)", "", raw)
        raw = re.sub(r"\[\[[^\]]+\]\]", "", raw)
        raw = re.sub(r"\[\d+\]", "", raw)
        raw = re.sub(r"[*_#`\\]", "", raw)
        raw = re.sub(r"^(?:Coletti\s+)?Definizione\s+di\s+[^\n:]+[:–\-]?\s*", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"^(?:Dizionario|Vocabolario|Treccani|Wikipedia|Corriere\.it|Significato|Etimologia)[^\n:]*[:–\-]\s*", "", raw, flags=re.IGNORECASE)

        # Rimuovi intestazione ripetuta del concetto
        raw = re.sub(r"^(?:" + re.escape(concept) + r")\s*[:–\-]?\s*", "", raw, flags=re.IGNORECASE)

        # Espansione abbreviazioni dizionariali
        raw = re.sub(r"\bCon sign\. concr\.,?", "In senso concreto,", raw)
        raw = re.sub(r"\bcome sinon\. di\b", "come sinonimo di", raw)
        raw = re.sub(r"\bspec\. in\b", "specialmente in", raw)
        raw = re.sub(r"\bl['’\u2019\?]?e\.\b", f"l'{c_lower}", raw)
        raw = re.sub(r"\bdall['’\u2019\?]?e\.\b", f"dall'{c_lower}", raw)
        raw = re.sub(r"\bun['’\u2019\?]?e\.\b", f"un'{c_lower}", raw)
        raw = re.sub(r"\bquest['’\u2019\?]?e\.\b", f"quest'{c_lower}", raw)
        raw = re.sub(r"\be\.\b", c_lower, raw)
        raw = re.sub(r"\bsec\.\b", "", raw)
        raw = re.sub(r"[…\.]+", ".", raw)
        raw = re.sub(r"[:;,]\s*\.", ".", raw)
        raw = re.sub(r"\s+", " ", raw).strip(" :;,-")

        if raw and not raw[0].isupper():
            raw = raw[0].upper() + raw[1:]
        if raw and not raw.endswith((".", "!", "?")):
            raw += "."
        return raw

    def resolve_url_entity(self, input_url: str) -> Dict[str, Any]:
        """
        Risolve URL e unshortener (es. share.google/..., maps.app.goo.gl/..., bit.ly/...),
        segue i redirect HTTP 301/302, ed estrae il vero nome dell'entità/azienda target e il dominio.
        Evita che il protocollo 'https' o il dominio vengano confusi per la ragione sociale.
        """
        if not input_url or not re.match(r"^https?://", input_url.strip(), re.IGNORECASE):
            return {}

        clean_url = input_url.strip()
        req = urllib.request.Request(
            clean_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        try:
            with urllib.request.urlopen(req, timeout=7.0) as resp:
                final_url = resp.geturl()
                parsed = urllib.parse.urlparse(final_url)
                qs = urllib.parse.parse_qs(parsed.query)

                target_name = None
                # Se è un redirect di Google Search / Maps (share.google o maps)
                if "google." in parsed.netloc:
                    if "q" in qs and qs["q"]:
                        target_name = qs["q"][0]
                    elif "kgmid" in qs and "q" in qs:
                        target_name = qs["q"][0]

                # Leggi titolo HTML per fallback o conferma
                html = resp.read(16384).decode("utf-8", errors="ignore")
                m_title = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
                raw_title = m_title.group(1).strip() if m_title else ""

                if not target_name and raw_title:
                    # Rimuovi suffissi come ' - Google Maps', ' | Home', ecc.
                    t = re.sub(r"\s*[-|–]\s*(?:Google Search|Google Maps|Home|Sito Ufficiale|Official Website).*$", "", raw_title, flags=re.IGNORECASE).strip()
                    if t and t.lower() not in ["google search", "google maps", "accesso", "login", "home", "https"]:
                        target_name = t

                domain = parsed.netloc.lower()
                if domain.startswith("www."):
                    domain = domain[4:]

                if not target_name and domain and not any(skip in domain for skip in ["google.", "bit.ly", "t.co", "tinyurl"]):
                    # Deduci brand name dal dominio (es. apaspa.com -> APA SpA)
                    parts = domain.split(".")
                    if parts:
                        target_name = parts[0].upper()

                return {
                    "input_url": clean_url,
                    "final_url": final_url,
                    "target_name": target_name,
                    "domain": domain,
                    "title": raw_title
                }
        except Exception as e:
            print(f"[URL RESOLVER] Errore unshortening per {clean_url}: {e}")
            return {"input_url": clean_url, "error": str(e)}

    def search_duckduckgo_lite(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Motore di ricerca web open-source e gratuito basato su DuckDuckGo Lite.
        Zero crediti, zero API key, zero tracciamento.
        """
        clean_q = query.strip()
        data = urllib.parse.urlencode({"q": clean_q}).encode("utf-8")
        req = urllib.request.Request(
            "https://lite.duckduckgo.com/lite/",
            data=data,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        results = []
        try:
            with urllib.request.urlopen(req, timeout=6.0) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                raw_links = re.findall(r'<a[^>]+rel=[\'"]nofollow[\'"][^>]+href=[\'"]([^\'"]+)[\'"][^>]*>(.*?)</a>', html, re.DOTALL)
                raw_snippets = re.findall(r'<td[^>]+class=[\'"]result-snippet[\'"][^>]*>(.*?)</td>', html, re.DOTALL)
                
                for i in range(min(len(raw_links), len(raw_snippets), limit)):
                    raw_url = raw_links[i][0]
                    real_url = raw_url
                    if "uddg=" in raw_url:
                        parsed = urllib.parse.parse_qs(urllib.parse.urlsplit(raw_url).query)
                        if "uddg" in parsed:
                            real_url = parsed["uddg"][0]
                    
                    title = re.sub(r"<[^>]+>", "", raw_links[i][1]).strip()
                    snip = re.sub(r"<[^>]+>", "", raw_snippets[i]).strip()
                    if title or snip:
                        results.append({
                            "title": title,
                            "url": real_url,
                            "description": snip
                        })
        except Exception as e:
            print(f"[OPEN OSINT] Errore DuckDuckGo Lite: {e}")
        return results

    def extract_webpage_markdown(self, url: str, timeout: float = 4.0) -> Optional[str]:
        """
        Scarica e distilla il contenuto di una pagina web in puro Markdown o testo leggibile.
        Combina Trafilatura con fallback euristico sul DOM (meta tags, JSON-LD, footer).
        """
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                
                # 1. Prova con Trafilatura
                try:
                    import trafilatura
                    extracted = trafilatura.extract(html, output_format="markdown")
                    if extracted and len(extracted) > 120:
                        return extracted[:3500].strip()
                except Exception:
                    pass

                # 2. Fallback Forense su DOM: Meta tag, Titolo, Descrizione e Footer
                parts = []
                m_title = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
                if m_title:
                    parts.append(f"# {re.sub(r'<[^>]+>', '', m_title.group(1)).strip()}")

                m_desc = re.search(r'<meta[^>]+(?:name|property)=["\'](?:description|og:description)["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
                if m_desc:
                    parts.append(f"Descrizione Ufficiale: {m_desc.group(1).strip()}")

                # Estrazione JSON-LD per entità Organization / LocalBusiness
                m_jsonld = re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.IGNORECASE | re.DOTALL)
                for j_raw in m_jsonld[:2]:
                    try:
                        clean_j = j_raw.strip()
                        if "address" in clean_j or "legalName" in clean_j or "vatID" in clean_j:
                            parts.append(f"Dati Strutturati JSON-LD: {clean_j[:600]}")
                    except Exception:
                        pass

                # Estrazione Footer per dati societari
                m_foot = re.search(r"<footer[^>]*>(.*?)</footer>", html, re.IGNORECASE | re.DOTALL)
                if m_foot:
                    foot_clean = re.sub(r"<[^>]+>", " ", m_foot.group(1))
                    foot_clean = " ".join(foot_clean.split())
                    if foot_clean:
                        parts.append(f"Footer Societario: {foot_clean[:800]}")

                # Estrazione testo visibile (rimuovendo script, style, svg)
                no_scripts = re.sub(r"<(?:script|style|svg|noscript)[^>]*>.*?</(?:script|style|svg|noscript)>", " ", html, flags=re.IGNORECASE | re.DOTALL)
                clean_body = re.sub(r"<[^>]+>", " ", no_scripts)
                clean_body = " ".join(clean_body.split())
                if clean_body and len(clean_body) > 60:
                    parts.append(f"Contenuto Pagina: {clean_body[:1800]}")

                # 3. Estrazione Forense da Bundle SPA (React / Vite / Lovable / Next.js)
                spa_intel = self.extract_spa_bundle_intel(url, html)
                if spa_intel:
                    if spa_intel.get("headquarters"):
                        parts.append(f"Headquarters Ufficiale: {spa_intel['headquarters']}")
                    if spa_intel.get("maps_location"):
                        parts.append(f"Geolocalizzazione Mappa: {spa_intel['maps_location']}")
                    if spa_intel.get("controller_and_hq"):
                        parts.append(f"Titolare Trattamento: {spa_intel['controller_and_hq']}")
                    if spa_intel.get("governing_law"):
                        parts.append(f"Quadro Normativo: {spa_intel['governing_law']}")

                if parts:
                    return "\n\n".join(parts).strip()
        except Exception:
            pass
        return None

    def extract_spa_bundle_intel(self, base_url: str, html: str, timeout: float = 3.5) -> Dict[str, Any]:
        """
        ANALISI FORENSE BUNDLE SPA (React/Vite/Next.js/Lovable):
        Se il sito è un'applicazione client-side, scansiona i file .js caricati nel DOM
        per estrarre: Headquarters, Google Maps embedded, titolare del trattamento (Controller)
        e leggi di protezione dati applicabili (es. UAE PDPL, GDPR).
        """
        intel = {}
        scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
        for s in scripts:
            if any(k in s.lower() for k in ['index-', 'main.', 'app.', 'bundle.', 'chunk-', 'vendor.']):
                s_url = urllib.parse.urljoin(base_url, s)
                try:
                    req = urllib.request.Request(s_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                    with urllib.request.urlopen(req, timeout=timeout) as resp:
                        code = resp.read().decode('utf-8', errors='ignore')
                        
                        # 1. Google Maps iframe target
                        m_map = re.search(r'google\.com/maps\?q=([^&"\'<>]+)', code)
                        if m_map:
                            intel['maps_location'] = urllib.parse.unquote(m_map.group(1)).replace('+', ' ').strip()
                        
                        # 2. Headquarters label
                        m_hq = re.search(r'(?:label:["\']Headquarters["\'],value:["\']([^"\']+)["\']|Headquarters[:\s]+([^"\'\n\r]{5,80}))', code)
                        if m_hq:
                            intel['headquarters'] = (m_hq.group(1) or m_hq.group(2)).strip()
                            
                        # 3. Data controller & registered office
                        m_ctrl = re.search(r'([A-Za-z0-9\s\,\.\&\-]+,\s*headquartered\s+in\s+[^,]+,\s*[^,]+,\s*[A-Za-z\s]+)', code, re.IGNORECASE)
                        if m_ctrl:
                            intel['controller_and_hq'] = m_ctrl.group(1).strip()
                        
                        # 4. Law & Regulations
                        m_law = re.search(r'(Federal\s+Decree-Law\s+No\.\s*[0-9]+\s+of\s+[0-9]+[^\n\r"\'\.\;]*)', code, re.IGNORECASE)
                        if m_law:
                            intel['governing_law'] = m_law.group(1).strip()
                except Exception:
                    pass
        return intel

    def crawl_legal_anchors(self, base_url: str, timeout: float = 3.5) -> Dict[str, Any]:
        """
        CRAWLER FORENSE DEI FOGLI LEGALI:
        Scansiona la pagina target per individuare e scaricare pagine /terms, /privacy, /legal, /about.
        Estrae: sede legale, numero registrazione (CRN / P.IVA), legge applicabile e fori competenti.
        Se assenti, rileva e segnala lo stato di OPACITÀ SOCIETARIA.
        """
        result = {
            "has_legal_pages": False,
            "legal_urls": [],
            "registered_office_extracted": None,
            "company_number_extracted": None,
            "governing_law_extracted": None,
            "opacita_rilevata": False,
            "note_legali": ""
        }
        if not base_url or not base_url.startswith("http"):
            return result

        try:
            req = urllib.request.Request(
                base_url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                html = resp.read().decode("utf-8", errors="ignore")

            # 1. Prova estrazione forense immediata da bundle SPA (React/Vite/Next)
            spa_intel = self.extract_spa_bundle_intel(base_url, html, timeout=timeout)
            if spa_intel:
                result["has_legal_pages"] = True
                if spa_intel.get("headquarters") or spa_intel.get("maps_location"):
                    result["registered_office_extracted"] = spa_intel.get("headquarters") or spa_intel.get("maps_location")
                if spa_intel.get("governing_law"):
                    result["governing_law_extracted"] = spa_intel.get("governing_law")
                result["opacita_rilevata"] = False
                result["note_legali"] = f"Dati legali e sede estratti dal bundle SPA: Sede/HQ={result['registered_office_extracted']} | Normativa={result['governing_law_extracted']}"

            # 2. Cerca link legali o anagrafici tradizionali
            found_links = set()
            for m in re.finditer(r'href=["\']([^"\']+)["\']', html, re.IGNORECASE):
                href = m.group(1).strip()
                if any(k in href.lower() for k in ["privacy", "terms", "condizioni", "legal", "note-legali", "imprint", "terms-and-conditions"]):
                    full_link = urllib.parse.urljoin(base_url, href)
                    found_links.add(full_link)

            result["legal_urls"] = list(found_links)[:3]

            # Piè di pagina della homepage: i siti italiani vi riportano P.IVA e sede (art. 35 DPR 633/72)
            home_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
            m_home_piva = re.search(r"(?:p\.?\s*iva|partita\s+iva|c\.?\s*f\.?\s*/?\s*p\.?\s*iva|codice\s+fiscale)[\s:.]*(?:IT)?\s*([0-9]{11})\b", home_text, re.IGNORECASE)
            if m_home_piva:
                result["company_number_extracted"] = m_home_piva.group(1)
            m_home_sede = re.search(r"sede\s+(?:legale|nazionale|centrale)\s*[:\-]?\s*([A-Za-zÀ-ÿ0-9][^|<>\n]{8,100}?)(?=\s*(?:[-|•]|p\.?\s*iva|c\.?\s*f\.|tel|email|$))", home_text, re.IGNORECASE)
            if m_home_sede:
                result["registered_office_extracted"] = m_home_sede.group(1).strip(" ,.-")

            if not found_links and not spa_intel and not (m_home_piva or m_home_sede):
                # Nessuna pagina legale rintracciata
                result["opacita_rilevata"] = True
                result["note_legali"] = "Nessuna pagina di Termini di Servizio, Note Legali o Privacy rinvenuta nel portale ufficiale."
                return result

            if found_links:
                result["has_legal_pages"] = True
                # Scarica e analizza la prima pagina legale trovata
                for l_url in list(found_links)[:2]:
                    l_text = self.extract_webpage_markdown(l_url, timeout=timeout) or ""
                    if l_text:
                        # Estrazione Legge Applicabile / Foro
                        m_law = re.search(r"(?:governed\s+by|governing\s+law|jurisdiction|disciplinat[ao]\s+da(?:lla)?|foro\s+competente)[:\s]+([^.\n\r;]{10,120})", l_text, re.IGNORECASE)
                        if m_law and not result["governing_law_extracted"]:
                            result["governing_law_extracted"] = m_law.group(1).strip()

                        # Estrazione Sede Legale
                        m_reg_off = re.search(r"(?:registered\s+office|sede\s+legale|registered\s+address)[:\s]+([^.\n\r;]{10,120})", l_text, re.IGNORECASE)
                        if m_reg_off and not result["registered_office_extracted"]:
                            result["registered_office_extracted"] = m_reg_off.group(1).strip()

                        # Estrazione Company Number
                        m_cnum = re.search(r"(?:company\s+(?:number|no|registration)|registration\s+no|crn|p\.?\s*iva)[:\s]+([A-Za-z0-9\-]+)", l_text, re.IGNORECASE)
                        if m_cnum and not result["company_number_extracted"]:
                            result["company_number_extracted"] = m_cnum.group(1).strip()

            if not result["registered_office_extracted"] and not result["company_number_extracted"]:
                # Pagine legali esistenti ma testo non riconosciuto dall'estrattore: limite nostro, non opacità dell'ente
                result["note_legali"] = "Pagine legali presenti; sede e identificativi non estratti automaticamente (verifica manuale)."
            else:
                result["note_legali"] = f"Identificativi legali estratti: Office={result['registered_office_extracted']}, Reg={result['company_number_extracted']}"

        except Exception as e:
            # Timeout o errore di rete: la verifica non è avvenuta, non è una prova di opacità
            result["error"] = str(e)
            result["verifica_fallita"] = True
            result["note_legali"] = f"Verifica delle pagine legali non riuscita ({type(e).__name__}): nessuna conclusione."

        return result

    def analyze_domain_forensics(self, target_url_or_domain: str) -> Dict[str, Any]:
        """
        RECON TECNICA & FORENSE SULL'INFRASTRUTTURA:
        Estrae: Risoluzione IP, Reverse DNS (Hosting Stack / CDN), Data di Registrazione RDAP, Anzianità dominio in giorni.
        Genera 'Chicche Forensi' deterministiche per smascherare discrepanze tra età dichiarata e realtà digitale.
        """
        import socket
        from datetime import datetime

        if "://" in target_url_or_domain:
            domain = urllib.parse.urlsplit(target_url_or_domain).netloc
        else:
            domain = target_url_or_domain.split("/")[0]
        domain = re.sub(r"^www\.", "", domain).strip().lower()

        res = {
            "domain": domain,
            "ip": None,
            "reverse_dns": None,
            "hosting_provider": "Non determinato",
            "created_date": None,
            "domain_age_days": None,
            "chicche": []
        }

        if not domain or "." not in domain:
            return res

        # 1. DNS & Reverse DNS
        try:
            ip = socket.gethostbyname(domain)
            res["ip"] = ip
            try:
                rev_host, _, _ = socket.gethostbyaddr(ip)
                res["reverse_dns"] = rev_host
                if "lovable" in rev_host.lower():
                    res["hosting_provider"] = "Lovable.dev (AI App Builder / Prototipo)"
                elif "vercel" in rev_host.lower():
                    res["hosting_provider"] = "Vercel Cloud Platform"
                elif "cloudflare" in rev_host.lower():
                    res["hosting_provider"] = "Cloudflare Proxy / CDN"
                elif "aws" in rev_host.lower() or "amazon" in rev_host.lower():
                    res["hosting_provider"] = "Amazon Web Services (AWS)"
                elif "azure" in rev_host.lower() or "microsoft" in rev_host.lower():
                    res["hosting_provider"] = "Microsoft Azure"
                elif "hetzner" in rev_host.lower():
                    res["hosting_provider"] = "Hetzner Online"
                else:
                    res["hosting_provider"] = rev_host
            except Exception:
                res["reverse_dns"] = "N/D"
        except Exception:
            pass

        # 2. RDAP Query (Data di Registrazione del Dominio)
        try:
            req = urllib.request.Request(
                f"https://rdap.org/domain/{domain}",
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                events = data.get("events", [])
                for ev in events:
                    if ev.get("eventAction") == "registration" and ev.get("eventDate"):
                        d_str = ev.get("eventDate")[:10]
                        res["created_date"] = d_str
                        try:
                            d_obj = datetime.strptime(d_str, "%Y-%m-%d")
                            delta = (datetime.now() - d_obj).days
                            res["domain_age_days"] = delta
                        except Exception:
                            pass
        except Exception:
            pass

        # 3. Generazione automatica di Chicche Forensi
        if res["hosting_provider"] and "Lovable" in res["hosting_provider"]:
            res["chicche"].append("Infrastruttura Web basata su prototipo rapido Lovable AI (lovable-app-cd-1-4.p.l5e.io).")
        if res["domain_age_days"] is not None:
            if res["domain_age_days"] < 365:
                res["chicche"].append(f"Dominio registrato di recente il {res['created_date']} ({res['domain_age_days']} giorni di attività web).")
            else:
                anni = res["domain_age_days"] // 365
                res["chicche"].append(f"Dominio storico registrato il {res['created_date']} ({anni} anni di presenza web).")

        return res

    def fetch_open_osint(self, query: str, limit: int = 5, deep_scrape: bool = True) -> List[Dict[str, Any]]:
        """
        Pipeline di intelligence open-source ad alta fedeltà a costo zero:
        1. Ricerca aperta su DuckDuckGo Lite (gratuito al 100%).
        2. Fallback su Firecrawl se la ricerca locale non produce risultati.
        3. Deep-Scraping con Trafilatura + DOM Fallback sul link principale per acquisire il testo completo.
        4. Esecuzione Forense automatica su fogli legali (/terms, /privacy) e infrastruttura di dominio (IP, RDAP).
        """
        items = self.search_duckduckgo_lite(query, limit=limit)
        if not items:
            items = self.fetch_firecrawl_osint(query, limit=limit)

        if deep_scrape and items:
            first_url = items[0].get("url")
            if first_url and not any(skip in first_url.lower() for skip in ["youtube.com", "facebook.com", "instagram.com", ".pdf"]):
                full_md = self.extract_webpage_markdown(first_url, timeout=4.0)
                if full_md:
                    items[0]["deep_content"] = full_md
                
                # Esecuzione automatica dei due moduli forensi sul sito target
                items[0]["forensic_domain"] = self.analyze_domain_forensics(first_url)
                items[0]["forensic_legal"] = self.crawl_legal_anchors(first_url, timeout=3.5)

        return items

    def fetch_firecrawl_osint(self, query: str, limit: int = 4) -> List[Dict[str, Any]]:
        """
        Esegue ricerche con Firecrawl API (fallback di riserva se configurato).
        """
        self._load_env()
        api_key = os.environ.get("FIRECRAWL_API_KEY")
        if not api_key:
            return []
        clean_q = query.strip()
        try:
            url = "https://api.firecrawl.dev/v1/search"
            payload = json.dumps({
                "query": clean_q,
                "limit": limit
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            })
            with urllib.request.urlopen(req, timeout=7.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    items = data.get("data", [])
                    results = []
                    for it in items:
                        t = (it.get("title") or "").strip()
                        u = (it.get("url") or "").strip()
                        d = (it.get("description") or "").strip()
                        if t or d:
                            results.append({
                                "title": t,
                                "url": u,
                                "description": d
                            })
                    return results
        except Exception as e:
            print(f"[SHERLOCK OSINT] Errore Firecrawl search: {e}")
        return []

    def fetch_firecrawl(self, query: str) -> Optional[Dict[str, Any]]:
        """Interroga Firecrawl API per estrarre definizioni pulite per l'ontologia di base."""
        self._load_env()
        api_key = os.environ.get("FIRECRAWL_API_KEY")
        if not api_key:
            return None
        clean_q = query.strip()
        # Per concetti da vocabolario a parola singola, possiamo orientare verso enciclopedia,
        # ma senza distruggere i nomi composti o entità
        if len(clean_q.split()) == 1 and not clean_q.isupper():
            search_query = f"{clean_q} enciclopedia definizione"
        else:
            search_query = clean_q
        try:
            url = "https://api.firecrawl.dev/v1/search"
            payload = json.dumps({
                "query": search_query,
                "limit": 3
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            })
            with urllib.request.urlopen(req, timeout=8.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    items = data.get("data", [])
                    if items:
                        selected_item = items[0]
                        title = selected_item.get("title") or query
                        desc = (selected_item.get("description") or "").strip()
                        summary = desc
                        if summary and len(summary) > 20:
                            return {"found": True, "title": title, "summary": summary, "source": "firecrawl"}
        except Exception:
            pass
        return None

    def fetch_summary(self, concept_name: str) -> Dict[str, Any]:
        """Ricerca con fallback gerarchico: Firecrawl (web aperto pulito) -> Wikipedia REST API."""
        clean_name = concept_name.lower().strip()
        fc_res = self.fetch_firecrawl(clean_name)
        if fc_res and fc_res.get("found"):
            return fc_res

        # 1. Prova slug diretto con underscore
        slug = clean_name.replace(" ", "_")
        url = f"https://it.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(slug)}"
        out = {"found": False, "title": "", "summary": ""}
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    summary_text = (data.get("extract") or "").strip()
                    if summary_text and len(summary_text) > 10:
                        out["found"] = True
                        out["title"] = data.get("title", clean_name)
                        out["summary"] = summary_text
                        return out
        except Exception:
            pass

        # 2. Se fallisce, usa opensearch per trovare il titolo canonico esatto
        try:
            search_url = f"https://it.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(clean_name)}&limit=1&namespace=0&format=json"
            req = urllib.request.Request(search_url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                if resp.status == 200:
                    s_data = json.loads(resp.read().decode("utf-8"))
                    titles = s_data[1] if len(s_data) > 1 else []
                    if titles:
                        canonical_title = titles[0].replace(" ", "_")
                        can_url = f"https://it.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(canonical_title)}"
                        req2 = urllib.request.Request(can_url, headers=self.headers)
                        with urllib.request.urlopen(req2, timeout=5.0) as resp2:
                            if resp2.status == 200:
                                d2 = json.loads(resp2.read().decode("utf-8"))
                                summary_text = (d2.get("extract") or "").strip()
                                if summary_text and len(summary_text) > 10:
                                    out["found"] = True
                                    out["title"] = d2.get("title", clean_name)
                                    out["summary"] = summary_text
                                    return out
        except Exception as e:
            out["error"] = str(e)

        out["not_found"] = True
        return out

    def analyze(self, concept_name: str, summary: str, human_explanation: Optional[str] = None) -> Dict[str, Any]:
        """Analisi puramente testuale: categorie, 'è un', divergenze. Nessuna rete."""
        lower_ext = (summary or "").lower()
        clues = []
        if "aracnid" in lower_ext:
            clues.append("aracnide")
        elif "insetto" in lower_ext or "insetti" in lower_ext:
            clues.append("insetto")
        elif "mammifero" in lower_ext:
            clues.append("mammifero")
        elif "rettile" in lower_ext or "rettili" in lower_ext:
            clues.append("rettile")
        elif "pianta" in lower_ext or "vegetale" in lower_ext:
            clues.append("botanica")

        is_a_web = extract_is_a(summary)
        is_a_human = extract_is_a(human_explanation)

        # Rileva se l'umano descrive un termine linguistico, colloquiale o slang
        is_human_slang = bool(human_explanation and re.search(
            r"\b(?:termine|slang|gergo|modo\s+di\s+dire|espressione|abbreviazione|significa|vuol\s+dire|usato\s+dai|usato\s+per|parola\s+per)\b",
            human_explanation.lower()
        ))
        
        # Filtra allucinazioni da disambiguazione Wikipedia (band musicali, singoli, album per parole comuni come 'yes', 'woow')
        music_disambig = bool(re.search(
            r"\b(?:gruppo\s+musicale|singolo\s+de[li]|album\s+in\s+studio|brano\s+musicale|canzone|band\s+britannic[ao]|cantante|discografia)\b",
            lower_ext
        ))

        disambiguation_conflict = False
        if is_human_slang and music_disambig:
            # L'omonimia musicale della rete non deve sovrascrivere lo slang del Creatore
            disambiguation_conflict = True
            is_a_web = None
            clues = ["slang"]

        divergence = None
        if human_explanation and not disambiguation_conflict:
            h_lower = human_explanation.lower()
            if "insetto" in h_lower and "aracnid" in lower_ext:
                divergence = (
                    "Descritto comunemente come insetto, ma la biologia formale "
                    "lo classifica come aracnide (caratterizzato da 8 zampe e assenza di antenne)."
                )
            elif (is_a_human and is_a_web and stem(is_a_human) != stem(is_a_web)
                  and stem(is_a_human) not in lower_ext):
                # Se è una specificazione gerarchica compatibile (es. animale vs mammifero), NON è una divergenza!
                pair = frozenset({stem(is_a_human), stem(is_a_web)})
                if pair not in COMPATIBLE_HIERARCHIES:
                    divergence = (
                        f"Tu me l'hai descritto come '{is_a_human}', ma la fonte lo classifica come '{is_a_web}'."
                    )

        return {
            "category_clues": clues,
            "is_a_web": is_a_web,
            "is_a_human": is_a_human,
            "divergence": divergence,
            "disambiguation_conflict": disambiguation_conflict,
        }

    def verify_concept_online(self, concept_name: str, human_explanation: Optional[str] = None) -> Dict[str, Any]:
        """Compatibilità: ricerca online + analisi."""
        fetched = self.fetch_summary(concept_name)
        result = {
            "concept": concept_name.lower().strip(),
            "found": fetched["found"],
            "title": fetched.get("title", ""),
            "verified_summary": fetched.get("summary", ""),
            "source": "web",
        }
        if "error" in fetched:
            result["error"] = fetched["error"]
        result.update(self.analyze(concept_name, result["verified_summary"], human_explanation))
        return result
