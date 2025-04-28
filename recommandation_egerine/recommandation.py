import os
import streamlit as st
import requests, re, ast, hashlib, io
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import pandas as pd
from collections import Counter
import plotly.express as px

# =============================
#          NOUVEAU CODE
# =============================

# 1) Définition de répertoires relatifs
BASE_DIR = os.path.dirname(__file__)  # dossier où se trouve ce script
BDD_DIR = os.path.join(BASE_DIR, "BDD_parametres")  # dossier où se trouvent tes fichiers .txt

# 2) Petite fonction utilitaire pour lire les mots-clés
def load_keywords(file_path):
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read().strip()
        if content.startswith("[") and content.endswith("]"):
            return ast.literal_eval(content)
        return [line.strip() for line in content.splitlines() if line.strip()]
    except Exception as e:
        st.error(f"Erreur de lecture pour {file_path}: {e}")
        return []

# =============================
#  FIN NOUVEAU CODE
# =============================

# Définition du set de stopwords custom en français
custom_stopwords = {
    'ils', 'et', 'du', 'as', 'nos', 'sur', 'fut', 'ayants', 'auriez', 'j', 'eurent', 'l', 'ses', 'eues', 'eux',
    'aurais', 'fussions', 'eussiez', 'avaient', 's', 'dans', 'furent', 'fussiez', 'son', 'aie', 'était', 'mes',
    'on', 'eu', 'été', 'sont', 'ton', 'suis', 'le', 'aurait', 'serait', 'auront', 'vos', 'mon', 'ayante', 'eûmes',
    'te', 'tes', 'leur', 'je', 'étées', 'même', 'étante', 'es', 'serons', 'tu', 'sera', 'nous', 'ne', 'aies',
    'ayons', 'seront', 'avons', 'des', 'ma', 'fusses', 'serai', 'pas', 'une', 'un', 'par', 'ou', 'serez', 'lui',
    'est', 'd', 'toi', 'eut', 'aux', 'avions', 'fût', 'ait', 'ont', 'sa', 'étais', 'y', 'aurez', 'mais', 'à',
    'aurions', 'fussent', 'avec', 'qu', 'de', 'au', 'en', 'aurons', 'avait', 'la', 'aurai', 'qui', 'aient', 'fusse',
    'eût', 'fûmes', 'que', 'étée', 'votre', 'n', 't', 'seraient', 'eusses', 'notre', 'il', 'ta', 'eus', 'êtes',
    'eue', 'soyons', 'fus', 'étant', 'vous', 'ce', 'étants', 'les', 'ayant', 'avez', 'serions', 'eusse', 'étés',
    'eussions', 'eussent', 'pour', 'étions', 'étiez', 'auraient', 'me', 'seriez', 'auras', 'se', 'elle', 'eûtes',
    'ayantes', 'moi', 'ayez', 'soyez', 'soit', 'c', 'm', 'seras', 'aviez', 'étaient', 'avais', 'sommes', 'fûtes',
    'sois', 'serais', 'aura', 'ces', 'soient', 'étantes', 'ai', 'the'
}

# Configuration de la page
st.set_page_config(page_title="EGERINE Let’s Glow", page_icon="✨", layout="wide")

# ========= Zone d'ajout d'entreprises personnalisées optimisée =========
if "custom_companies" not in st.session_state:
    st.session_state["custom_companies"] = {}

with st.sidebar.form(key="company_form", clear_on_submit=True):
    st.markdown("<h3 style='color:#F8B195;'>Ajouter une entreprise</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Nom", placeholder="Ex: Ma Société")
    with col2:
        company_url = st.text_input("URL", placeholder="https://www.monsite.com")
    submit = st.form_submit_button("Ajouter", help="Cliquez pour ajouter l'entreprise")
    if submit:
        if company_name and company_url:
            st.session_state["custom_companies"][company_name] = company_url
            st.success(f"L'entreprise '{company_name}' a été ajoutée.")
        else:
            st.error("Veuillez renseigner le nom et l'URL de l'entreprise.")

# ========= CSS et Header =========
st.markdown(
    """
    <a href="#main-content" class="skip-link" style="position: absolute; top: -40px; left: 0; background: #F8B195; color: white; padding: 8px; z-index: 100; transition: top 0.3s;">
      Skip to content
    </a>
    <style>
      .skip-link:focus { top: 0; }
    </style>
    """, unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&family=Merriweather:wght@700&display=swap');
    html, body, [class*="css"] {
        background: linear-gradient(to bottom, #FFFFFF, #F4F4F4) !important;
        color: #333 !important;
        font-family: 'Lato', sans-serif;
        margin: 0;
        padding: 0;
    }
    button:focus, a:focus {
        outline: 3px solid #F8B195;
    }
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 50px;
        background: linear-gradient(90deg, #A8E6CF, #F8B195);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        border-radius: 0 0 25px 25px;
        margin-bottom: 40px;
    }
    .logo-container {
        display: flex;
        align-items: center;
    }
    .logo {
        font-size: 40px;
        font-family: 'Merriweather', serif;
        color: #FFF;
    }
    .menu a {
        margin-left: 30px;
        text-decoration: none;
        color: #FFF;
        font-size: 20px;
        transition: color 0.3s ease;
    }
    .menu a:hover {
        color: #EDEDED;
    }
    .center-block {
        text-align: center;
        padding: 70px 20px;
        margin-bottom: 50px;
    }
    .center-block .main-title {
        font-size: 64px;
        font-family: 'Merriweather', serif;
        color: #F8B195;
        margin-bottom: 20px;
    }
    .center-block .subtitle {
        font-size: 32px;
        color: #666;
        margin-bottom: 30px;
    }
    .center-block img {
        width: 150px;
        transition: transform 0.3s ease;
    }
    .center-block img:hover {
        transform: scale(1.08);
    }
    button {
        background-color: #F8B195 !important;
        color: #FFF !important;
        border: none;
        padding: 18px 36px;
        border-radius: 12px;
        font-size: 22px;
        cursor: pointer;
        transition: transform 0.3s ease, opacity 0.3s ease;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    button:hover {
        opacity: 0.9;
        transform: scale(1.05);
    }
    @media only screen and (max-width: 768px) {
        .header { padding: 15px 20px; flex-direction: column; }
        .logo { font-size: 32px; }
        .menu a { margin-left: 15px; font-size: 16px; }
        .center-block { padding: 40px 10px; }
        .center-block .main-title { font-size: 48px; }
        .center-block .subtitle { font-size: 24px; }
        button { font-size: 18px; padding: 12px 24px; }
    }
    .stTabs > div { margin-top: 30px; }
    .plotly-graph-div {
        transition: transform 0.3s ease;
    }
    .plotly-graph-div:hover {
        transform: scale(1.03);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ========= Header avec logo Egerine dans un petit cadre =========
st.markdown(
    """
    <div class="header" role="navigation" aria-label="Menu principal">
      <div class="logo-container">
         <div style="border: 1px solid #ccc; padding: 5px; border-radius: 8px; display: inline-block;">
           <img src="http://www.egerine.com/assets/img/Egerine.png" alt="Logo Egerine" style="height: 60px;">
         </div>
         <div class="logo" style="margin-left: 10px;">EGERINE Let’s Glow</div>
      </div>
      <div class="menu">
        <a href="#">Accueil</a>
        <a href="#">Solutions</a>
        <a href="#">Contact</a>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div id="main-content" class="center-block">
        <div class="main-title">La Publicité Réinventée</div>
        <div class="subtitle">Recommandations d’Amélioration pour Egerine</div>
        <img src="https://images.emojiterra.com/openmoji/v14.0/1024px/1f6b2.png" alt="Icône de vélo sans fond décoratif"/>
    </div>
    """,
    unsafe_allow_html=True
)

# ========= Bouton principal =========
if st.button("Vérifier les mises à jour"):
    st.write("L'extraction et l'analyse sont en cours...")

    # =====================
    #  CHANGEMENT ICI:
    #  Chemins relatifs
    # =====================
    keyword_files = {
        "Accessibilité": os.path.join(BDD_DIR, "Accessibilité.txt"),
        "Éclairage ou animations": os.path.join(BDD_DIR, "Éclairage ou animations.txt"),
        "Entretien et maintenance": os.path.join(BDD_DIR, "Entretien et maintenance.txt"),
        "Impact écologique": os.path.join(BDD_DIR, "impact_ecologique.txt"),
        "Interaction possible": os.path.join(BDD_DIR, "Interaction possible.txt"),
        "Kilométrage parcouru": os.path.join(BDD_DIR, "Kilométrage parcouru.txt"),
        "Prix": os.path.join(BDD_DIR, "Prix.txt"),
        "Rayon d'action": os.path.join(BDD_DIR, "Rayon d'action.txt"),
        "Taille et design des affiches": os.path.join(BDD_DIR, "Taille et design des affiches.txt"),
        "Temps (créneaux horaires)": os.path.join(BDD_DIR, "Temps (créneaux horaires).txt")
    }
    default_keywords = {param: load_keywords(path) for param, path in keyword_files.items()}

    # Configuration par défaut pour les entreprises non prédéfinies
    default_site_config = {
        "Kilométrage parcouru": {"keywords": default_keywords.get("Kilométrage parcouru", []), "default": "non spécifié", "strip_spaces": True},
        "Impact écologique": {"keywords": default_keywords.get("Impact écologique", []), "default": "non spécifié"},
        "Temps (créneaux horaires)": {"keywords": default_keywords.get("Temps (créneaux horaires)", []), "default": "non spécifié"},
        "Entretien et maintenance": {"keywords": default_keywords.get("Entretien et maintenance", []), "default": "non spécifié"},
        "Accessibilité": {"keywords": default_keywords.get("Accessibilité", []), "default": "non spécifié"},
        "Éclairage ou animations": {"keywords": default_keywords.get("Éclairage ou animations", []), "default": "non spécifié"},
        "Interaction possible": {"keywords": default_keywords.get("Interaction possible", []), "default": "non spécifié"},
        "Taille et design des affiches": {"keywords": default_keywords.get("Taille et design des affiches", []), "default": "non spécifié"},
        "Prix": {"keywords": default_keywords.get("Prix", []), "default": "non spécifié"}
    }

    def scrape_all_text(url):
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = session.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.get_text(separator=" ", strip=True)
        except Exception as e:
            st.error(f"Erreur lors du scraping de {url}: {e}")
            return ""

    def build_pattern(keywords):
        return r"(?:" + "|".join(map(re.escape, keywords)) + r")\s*(?:[:\-]?\s*)(.+?)(?=[\.,;\n]|$)"

    def clean_extracted_value(value):
        value = value.strip()
        value = re.sub(r'\s+', ' ', value)
        value = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', value)
        for wrong, right in {"kilom": "km", "tCO": "tCO2e", "no co2": "NO CO2"}.items():
            value = re.sub(r'\b' + re.escape(wrong) + r'\b', right, value, flags=re.IGNORECASE)
        return value

    def extract_sentence(text, pos):
        sentence_endings = ".?!"
        start = pos
        while start > 0 and text[start-1] not in sentence_endings:
            start -= 1
        end = pos
        while end < len(text) and text[end] not in sentence_endings:
            end += 1
        if end < len(text):
            end += 1
        return text[start:end].strip()

    def extract_parameters(text, config):
        params = {}
        for param, conf in config.items():
            keywords = conf.get("keywords", [])
            default = conf.get("default", "non spécifié")
            strip_spaces = conf.get("strip_spaces", False)
            match = re.search(build_pattern(keywords), text, re.IGNORECASE)
            if match:
                sentence = extract_sentence(text, match.start())
                if strip_spaces:
                    sentence = sentence.replace(" ", "")
                params[param] = clean_extracted_value(sentence)
            else:
                params[param] = default
        return params

    # Dictionnaire des configurations par site prédéfinis
    site_configs = {
        "Rainbooh": {
            "Kilométrage parcouru": {"keywords": default_keywords.get("Kilométrage parcouru", []), "default": "non spécifié", "strip_spaces": True},
            "Impact écologique": {"keywords": default_keywords.get("Impact écologique", []), "default": "non spécifié"},
            "Temps (créneaux horaires)": {"keywords": default_keywords.get("Temps (créneaux horaires)", []), "default": "non spécifié"},
            "Entretien et maintenance": {"keywords": default_keywords.get("Entretien et maintenance", []), "default": "Service clé en main avec chauffeur inclus"},
            "Accessibilité": {"keywords": default_keywords.get("Accessibilité", []), "default": "Couvre les principales zones touristiques de Paris"},
            "Éclairage ou animations": {"keywords": default_keywords.get("Éclairage ou animations", []), "default": "non spécifié"},
            "Interaction possible": {"keywords": default_keywords.get("Interaction possible", []), "default": "non spécifié"},
            "Taille et design des affiches": {"keywords": default_keywords.get("Taille et design des affiches", []), "default": "non spécifié"},
            "Prix": {"keywords": default_keywords.get("Prix", []), "default": "non spécifié"}
        },
        "Ecostudevents": {
            "Temps (créneaux horaires)": {"keywords": default_keywords.get("Temps (créneaux horaires)", []), "default": "non spécifié"},
            "Kilométrage parcouru": {"keywords": default_keywords.get("Kilométrage parcouru", []), "default": "non spécifié", "strip_spaces": True},
            "Entretien et maintenance": {"keywords": default_keywords.get("Entretien et maintenance", []), "default": "Transport aller-retour et service clé en main"},
            "Accessibilité": {"keywords": default_keywords.get("Accessibilité", []), "default": "Circuits dédiés (nombre de zones non précisé)"},
            "Impact écologique": {"keywords": default_keywords.get("Impact écologique", []), "default": "Support mobile éco-responsable"},
            "Éclairage ou animations": {"keywords": default_keywords.get("Éclairage ou animations", []), "default": "non spécifié"},
            "Interaction possible": {"keywords": default_keywords.get("Interaction possible", []), "default": "non spécifié"},
            "Taille et design des affiches": {"keywords": default_keywords.get("Taille et design des affiches", []), "default": "non spécifié"},
            "Prix": {"keywords": default_keywords.get("Prix", []), "default": "non spécifié"}
        },
        "Streetdispatch": {
            "Temps (créneaux horaires)": {"keywords": default_keywords.get("Temps (créneaux horaires)", []), "default": "non spécifié"},
            "Kilométrage parcouru": {"keywords": default_keywords.get("Kilométrage parcouru", []), "default": "non spécifié", "strip_spaces": True},
            "Accessibilité": {"keywords": default_keywords.get("Accessibilité", []), "default": "Média de proximité pour zones piétonnes"},
            "Impact écologique": {"keywords": default_keywords.get("Impact écologique", []), "default": "Moyen de communication écologique"},
            "Éclairage ou animations": {"keywords": default_keywords.get("Éclairage ou animations", []), "default": "non spécifié"},
            "Interaction possible": {"keywords": default_keywords.get("Interaction possible", []), "default": "non spécifié"},
            "Taille et design des affiches": {"keywords": default_keywords.get("Taille et design des affiches", []), "default": "non spécifié"},
            "Prix": {"keywords": default_keywords.get("Prix", []), "default": "non spécifié"}
        },
        "Cominvader": {
            "Temps (créneaux horaires)": {"keywords": default_keywords.get("Temps (créneaux horaires)", []), "default": "non spécifié"},
            "Kilométrage parcouru": {"keywords": default_keywords.get("Kilométrage parcouru", []), "default": "non spécifié", "strip_spaces": True},
            "Entretien et maintenance": {"keywords": default_keywords.get("Entretien et maintenance", []), "default": "Inclus dans l'offre globale, service réactif"},
            "Accessibilité": {"keywords": default_keywords.get("Accessibilité", []), "default": "Excellente mobilité pour zones inaccessibles"},
            "Impact écologique": {"keywords": default_keywords.get("Impact écologique", []), "default": "0 pollution, démarche green"},
            "Éclairage ou animations": {"keywords": default_keywords.get("Éclairage ou animations", []), "default": "non spécifié"},
            "Interaction possible": {"keywords": default_keywords.get("Interaction possible", []), "default": "non spécifié"},
            "Taille et design des affiches": {"keywords": default_keywords.get("Taille et design des affiches", []), "default": "Entièrement personnalisable (dimensions non spécifiées)"},
            "Prix": {"keywords": default_keywords.get("Prix", []), "default": "non spécifié"}
        },
        "Bikecom": {
            "Temps (créneaux horaires)": {"keywords": default_keywords.get("Temps (créneaux horaires)", []), "default": "non spécifié"},
            "Kilométrage parcouru": {"keywords": default_keywords.get("Kilométrage parcouru", []), "default": "non spécifié", "strip_spaces": True},
            "Entretien et maintenance": {"keywords": default_keywords.get("Entretien et maintenance", []), "default": "Structure légère en aluminium, maintenance non détaillée"},
            "Accessibilité": {"keywords": default_keywords.get("Accessibilité", []), "default": "Optimisé pour circulation en zones piétonnes et urbaines"},
            "Impact écologique": {"keywords": default_keywords.get("Impact écologique", []), "default": "Communication NO CO2"},
            "Éclairage ou animations": {"keywords": default_keywords.get("Éclairage ou animations", []), "default": "non spécifié"},
            "Interaction possible": {"keywords": default_keywords.get("Interaction possible", []), "default": "non spécifié"},
            "Taille et design des affiches": {"keywords": default_keywords.get("Taille et design des affiches", []), "default": "non spécifié"},
            "Prix": {"keywords": default_keywords.get("Prix", []), "default": "non spécifié"}
        },
        "tapagemedias": {
            "Temps (créneaux horaires)": {"keywords": default_keywords.get("Temps (créneaux horaires)", []), "default": "Adaptable en fonction de la zone ciblée"},
            "Kilométrage parcouru": {"keywords": default_keywords.get("Kilométrage parcouru", []), "default": "non spécifié", "strip_spaces": True},
            "Entretien et maintenance": {"keywords": default_keywords.get("Entretien et maintenance", []), "default": "non spécifié"},
            "Accessibilité": {"keywords": default_keywords.get("Accessibilité", []), "default": "Positionné au cœur de la ville"},
            "Impact écologique": {"keywords": default_keywords.get("Impact écologique", []), "default": "Utilisation de vélos (approche éco-responsable)"},
            "Éclairage ou animations": {"keywords": default_keywords.get("Éclairage ou animations", []), "default": "non spécifié"},
            "Interaction possible": {"keywords": default_keywords.get("Interaction possible", []), "default": "non spécifié"},
            "Taille et design des affiches": {"keywords": default_keywords.get("Taille et design des affiches", []), "default": "Support de 2 m², design personnalisable"},
            "Prix": {"keywords": default_keywords.get("Prix", []), "default": "non spécifié"}
        },
        "Velopub": {
            "Rayon d'action": {"keywords": default_keywords.get("Rayon d'action", []), "default": "non spécifié"},
            "Temps (créneaux horaires)": {"keywords": default_keywords.get("Temps (créneaux horaires)", []), "default": "non spécifié"},
            "Kilométrage parcouru": {"keywords": default_keywords.get("Kilométrage parcouru", []), "default": "non spécifié", "strip_spaces": True},
            "Entretien et maintenance": {"keywords": default_keywords.get("Entretien et maintenance", []), "default": "non spécifié"},
            "Accessibilité": {"keywords": default_keywords.get("Accessibilité", []), "default": "Adapté pour couvrir plusieurs points de vente"},
            "Impact écologique": {"keywords": default_keywords.get("Impact écologique", []), "default": "Vélo électrique, démarche écologique"},
            "Éclairage ou animations": {"keywords": default_keywords.get("Éclairage ou animations", []), "default": "non spécifié"},
            "Interaction possible": {"keywords": default_keywords.get("Interaction possible", []), "default": "non spécifié"},
            "Taille et design des affiches": {"keywords": default_keywords.get("Taille et design des affiches", []), "default": "Personnalisable (personnalisation via film plastique sur le carénage et les roues)"},
            "Prix": {"keywords": default_keywords.get("Prix", []), "default": "non spécifié"}
        }
    }

    # ========= Définition des sites concurrents =========
    competitor_sites = {
        "Rainbooh": "https://www.rainbooh.com/velos-publicitaires-street-marketing",
        "Ecostudevents": "https://ecostudevents.com/velo-publicitaire/",
        "Streetdispatch": "https://streetdispatch.com/street-marketing/velo-publicitaire-pour-affichage-urbain/",
        "Cominvader": "https://cominvader.net/velos-publicitaires/",
        "Bikecom": "https://bikecom.fr/les-formats-du-bikecom/",
        "tapagemedias": "https://www.tapagemedias.com/velo-publicitaire-affichage-mobile/",
        "Velopub": "https://www.comhic.com/fr/streetmarketing/velo-publicitaire/"
    }
    # Intégration des entreprises personnalisées ajoutées par l'utilisateur
    competitor_sites.update(st.session_state.get("custom_companies", {}))

    def aggregate_competitor_text(urls):
        aggregated_text = ""
        for name, url in urls.items():
            aggregated_text += " " + scrape_all_text(url)
        return aggregated_text

    def compute_hash(text):
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def compute_word_counts(text):
        tokens = re.findall(r'\b\w+\b', text.lower())
        words = [
            token for token in tokens 
            if token.isalpha() and token not in custom_stopwords and len(token) > 2
        ]
        return Counter(words)

    def main_extraction():
        extraction_results = {}
        progress_bar = st.progress(0)
        total_sites = len(competitor_sites)
        
        for i, (site, url) in enumerate(competitor_sites.items(), start=1):
            text = scrape_all_text(url)
            # Utilisation de la configuration spécifique si existante, sinon config par défaut
            config = site_configs.get(site, default_site_config)
            params = extract_parameters(text, config) if text else {}
            for key, value in params.items():
                if not value or value.isspace():
                    params[key] = "non spécifié"
            extraction_results[site] = params
            progress_bar.progress(i / total_sites)
            st.write(f"Scrapping de {site} terminé.")
        
        data = []
        for site, params in extraction_results.items():
            entry = {"Entreprise": site, "URL": competitor_sites[site]}
            entry.update(params)
            data.append(entry)
        df_extraction = pd.DataFrame(data)
        
        numeric_columns = ["Kilométrage parcouru", "Prix", "Rayon d'action"]
        param_columns = [col for col in df_extraction.columns if col not in ["Entreprise", "URL"]]
        
        def extract_numeric(value):
            m = re.search(r"(\d+(\.\d+)?)", str(value))
            if m:
                num_str = m.group(1)
                return float(num_str) if '.' in num_str else int(num_str)
            return 0
        
        for col in param_columns:
            if col in numeric_columns:
                df_extraction[col] = df_extraction[col].apply(extract_numeric)
            else:
                df_extraction[col] = df_extraction[col].apply(
                    lambda x: 1 if str(x).strip().lower() not in ["non spécifié", "non specifie", "nan", ""] else 0
                )
        
        excel_buffer = io.BytesIO()
        writer = pd.ExcelWriter(excel_buffer, engine='xlsxwriter')
        df_extraction.to_excel(writer, sheet_name='Extraction', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Extraction']
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9D9D9',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        for col_num, value in enumerate(df_extraction.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        red_format = workbook.add_format({
            'bg_color': '#FFC7CE',
            'font_color': '#9C0006',
            'text_wrap': True,
            'border': 1
        })
        green_format = workbook.add_format({
            'bg_color': '#C6EFCE',
            'font_color': '#006100',
            'text_wrap': True,
            'border': 1
        })
        for row in range(1, len(df_extraction) + 1):
            worksheet.set_row(row, 40)
            for col in range(len(df_extraction.columns)):
                col_name = df_extraction.columns[col]
                cell_value = df_extraction.iloc[row-1, col]
                if col_name in ["Entreprise", "URL"]:
                    worksheet.write(row, col, cell_value)
                else:
                    worksheet.write(row, col, cell_value, green_format if cell_value == 1 else red_format)
        
        for col_num, col_name in enumerate(df_extraction.columns):
            column_data = df_extraction[col_name].astype(str)
            max_length = max(column_data.map(len).max(), len(str(col_name))) + 2
            worksheet.set_column(col_num, col_num, max_length)
        
        writer.close()
        excel_data = excel_buffer.getvalue()
        
        aggregated_text = aggregate_competitor_text(competitor_sites)
        text_hash = compute_hash(aggregated_text)
        word_counts = compute_word_counts(aggregated_text)
        top_words = word_counts.most_common(10)
        
        return df_extraction, excel_data, text_hash, top_words, extraction_results

    df_extraction, excel_data, text_hash, top_words, extraction_results = main_extraction()
    
    # ========= Organisation en onglets =========
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Résultats", "Analyse du Texte", "Recommandations", "Schéma du Processus", "Autres Schémas"])
    
    with tab1:
        st.subheader("Résultats d'extraction")
        st.dataframe(df_extraction, height=400)
        st.download_button(
            label="Télécharger le fichier Excel",
            data=excel_data,
            file_name="resultats_extraction.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with tab2:
        st.subheader("Analyse de l'agrégation du texte")
        st.write(f"**Hash SHA256** de l'agrégation : {text_hash}")
        st.write("**Top 10 mots les plus fréquents** :")
        for word, count in top_words:
            st.write(f"- {word}: {count}")
        fig = px.bar(x=[w for w, c in top_words], y=[c for w, c in top_words],
                     labels={'x': "Mots", 'y': "Fréquence"},
                     title="Top 10 des mots les plus fréquents",
                     template="plotly_white")
        st.plotly_chart(fig)
        
        binary_columns = [col for col in df_extraction.columns if col not in ["Entreprise", "URL"] and col not in ["Kilométrage parcouru", "Prix", "Rayon d'action"]]
        param_presence = {col: int(df_extraction[col].sum()) for col in binary_columns}
        fig2 = px.bar(x=list(param_presence.keys()), y=list(param_presence.values()),
                      labels={'x': "Paramètre", 'y': "Nombre de concurrents"},
                      title="Présence des paramètres chez les concurrents",
                      template="plotly_white")
        st.plotly_chart(fig2)
        
        if "Kilométrage parcouru" in df_extraction.columns:
            fig3 = px.bar(df_extraction, x="Entreprise", y="Kilométrage parcouru",
                          title="Kilométrage parcouru par entreprise",
                          labels={"Kilométrage parcouru": "Km parcourus"},
                          template="plotly_white")
            st.plotly_chart(fig3)
    
    with tab3:
        st.subheader("Paramètres manquants chez Egerine & Recommandations")
        missing_dict = {}
        rec_dict = {}  # Dictionnaire pour stocker les recommandations dynamiques
        param_columns = [col for col in df_extraction.columns if col not in ["Entreprise", "URL"]]
        
        # =====================
        #  CHANGEMENT ICI:
        #  Chemin relatif pour Egerine_Stats.xlsx
        # =====================
        excel_egerine_path = os.path.join(BASE_DIR, "Egerine_Stats.xlsx")
        
        try:
            df_egerine = pd.read_excel(excel_egerine_path)
            df_egerine.columns = df_egerine.columns.str.strip()
            if "Entreprise" not in df_egerine.columns:
                st.warning("La colonne 'Entreprise' est introuvable dans Egerine_Stats.xlsx.")
            else:
                df_egerine["Entreprise"] = df_egerine["Entreprise"].astype(str).str.strip().str.lower()
                df_egerine_filtered = df_egerine[df_egerine["Entreprise"].str.contains("egerine", na=False)]
                if df_egerine_filtered.empty:
                    st.warning("Aucune entrée pour 'Egerine' dans Egerine_Stats.xlsx.")
                else:
                    egerine_row = df_egerine_filtered.iloc[0].copy()
                    for col in df_extraction.columns:
                        if col not in ["Entreprise", "URL"]:
                            try:
                                egerine_row[col] = float(egerine_row[col])
                            except:
                                egerine_row[col] = 0
                    for col in param_columns:
                        if float(egerine_row[col]) == 0:
                            sites_with_1 = df_extraction.loc[df_extraction[col] == 1, "Entreprise"].tolist()
                            if sites_with_1:
                                missing_dict[col] = sites_with_1
                    if missing_dict:
                        st.write("### Paramètres manquants chez Egerine")
                        for param, sites in missing_dict.items():
                            sites_str = ", ".join(sites)
                            st.write(f"- **{param}** : présent chez {sites_str} (0 chez Egerine)")
                    else:
                        st.write("Aucun paramètre manquant chez Egerine par rapport aux concurrents.")
                    
                    st.markdown("### Recommandations")
                    for param in missing_dict:
                        if param.lower().startswith("accessibilité"):
                            recommendation = "Ajoutez une section dédiée pour faciliter l'accès et mettre en avant la couverture des zones clés."
                        elif param.lower().startswith("temps"):
                            recommendation = "Affichez clairement vos créneaux horaires pour informer sur la disponibilité de vos services."
                        elif param.lower().startswith("kilométrage"):
                            recommendation = "Mettez en avant le kilométrage parcouru pour démontrer l'efficacité de vos déplacements."
                        elif param.lower().startswith("entretien"):
                            recommendation = "Détaillez votre politique d'entretien et de maintenance pour rassurer sur la qualité de vos offres."
                        elif param.lower().startswith("impact"):
                            recommendation = "Valorisez vos initiatives écologiques en expliquant l'impact environnemental positif."
                        elif param.lower().startswith("éclairage") or param.lower().startswith("animations"):
                            recommendation = "Proposez des animations ou un éclairage attractif pour dynamiser votre offre."
                        elif param.lower().startswith("interaction"):
                            recommendation = "Intégrez des fonctionnalités interactives pour favoriser l'engagement client."
                        elif param.lower().startswith("taille"):
                            recommendation = "Personnalisez le design de vos supports publicitaires pour mieux refléter votre image."
                        elif param.lower().startswith("prix"):
                            recommendation = "Présentez vos tarifs de manière transparente pour faciliter la comparaison."
                        elif param.lower().startswith("rayon"):
                            recommendation = "Définissez clairement votre rayon d'action pour démontrer votre couverture géographique."
                        else:
                            recommendation = f"Pour le paramètre '{param}', ajoutez une section dédiée pour mieux le valoriser."
                        rec_dict[param] = recommendation
                        st.write(f"- **{param}** : {recommendation}")
                    
                    if rec_dict:
                        dynamic_schema = "digraph Guidelines {\n"
                        dynamic_schema += "  rankdir=TB;\n"
                        dynamic_schema += '  Main [shape=box, style=filled, color=lightgreen, label="Points à Améliorer"];\n'
                        for param, rec in rec_dict.items():
                            node_name = param.replace(" ", "_")
                            safe_rec = rec.replace('"', "'")
                            dynamic_schema += f'  {node_name} [shape=box, style=filled, color=lightblue, label="{param}: {safe_rec}"];\n'
                            dynamic_schema += f'  Main -> {node_name};\n'
                        dynamic_schema += "}"
                        st.markdown("#### Schéma interactif des Recommandations")
                        st.graphviz_chart(dynamic_schema)
                        
                        missing_counts = {param: len(sites) for param, sites in missing_dict.items()}
                        fig_missing = px.bar(
                            x=list(missing_counts.keys()),
                            y=list(missing_counts.values()),
                            labels={'x': "Paramètres manquants", 'y': "Nombre de concurrents"},
                            title="Fréquence des paramètres manquants chez Egerine",
                            template="plotly_white"
                        )
                        st.plotly_chart(fig_missing)
                        
                        # --- Nouvelle section modifiée ---
                        st.markdown("### Extraits de textes des concurrents pour les paramètres manquants")
                        for param, sites in missing_dict.items():
                            st.write(f"#### {param}")
                            for site in sites:
                                with st.expander(f"Concurrent: {site}"):
                                    competitor_text = extraction_results.get(site, {}).get(param, "Texte non disponible")
                                    st.write(competitor_text)
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier Egerine_Stats.xlsx: {e}")
    
    with tab4:
        st.subheader("Schéma du Processus")
        flow_chart = """
        digraph {
            rankdir=LR;
            Extraction [shape=box, style=filled, color=lightblue, label="Extraction des Données"];
            Analyse [shape=box, style=filled, color=lightgreen, label="Analyse du Texte"];
            Comparaison [shape=box, style=filled, color=orange, label="Comparaison avec Egerine"];
            Recommandations [shape=box, style=filled, color=yellow, label="Génération des Recommandations"];
            Extraction -> Analyse;
            Extraction -> Comparaison;
            Comparaison -> Recommandations;
        }
        """
        st.graphviz_chart(flow_chart)
    
    with tab5:
        st.subheader("Autres Schémas")
        rec_flow = """
        digraph {
            rankdir=TB;
            A [shape=ellipse, style=filled, color=lightgrey, label="Analyse des Paramètres"];
            B [shape=box, style=filled, color=lightpink, label="Détection des Manquants"];
            C [shape=box, style=filled, color=lightblue, label="Génération des Recommandations"];
            D [shape=ellipse, style=filled, color=lightgreen, label="Mise à jour du Site"];
            A -> B;
            B -> C;
            C -> D;
        }
        """
        st.graphviz_chart(rec_flow)
        st.markdown(
            "<div style='text-align: center; margin-top: 20px;'>"
            "<img src='https://images.emojiterra.com/openmoji/v14.0/1024px/1f6b2.png' style='width:200px;' alt='Icône de vélo sans fond décoratif'/>"
            "</div>",
            unsafe_allow_html=True
        )
    st.write("Extraction terminée.")
