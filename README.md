# egerine-recommandations
Outil Streamlit d’analyse concurrentielle pour Egerine : extraction web, analyse de mots-clés, comparaison des offres et génération de recommandations stratégiques. Basé sur Python, Streamlit, BeautifulSoup, Plotly et Pandas.
# Egerine - Outil d'Analyse Concurrentielle

Outil Streamlit d’analyse concurrentielle pour Egerine : extraction web, analyse de mots-clés, comparaison des offres et génération de recommandations stratégiques.

## Fonctionnalités
- Extraction automatique de textes depuis des sites concurrents.
- Analyse et détection de mots-clés stratégiques.
- Comparaison avec les données internes d'Egerine.
- Génération de recommandations personnalisées.
- Visualisations interactives (tableaux, graphiques).
- Téléchargement des résultats au format Excel.

## Technologies utilisées
- Python
- Streamlit
- BeautifulSoup
- Pandas
- Plotly
- XlsxWriter

## Lancer le projet

```bash
# Cloner le dépôt
git clone https://github.com/TON-UTILISATEUR/TON-REPO.git

# Aller dans le dossier
cd TON-REPO

# Installer les dépendances
pip install streamlit requests beautifulsoup4 pandas plotly openpyxl xlsxwriter

# Lancer l'application
streamlit run recommandation.py
```
## Arborescence du projet
├── recommandation.py
├── Egerine_Stats.xlsx
└── BDD_parametres/
    ├── Accessibilité.txt
    ├── Entretien et maintenance.txt
    ├── impact_ecologique.txt
    ├── Interaction possible.txt
    ├── Kilométrage parcouru.txt
    ├── Prix.txt
    ├── Rayon d'action.txt
    ├── Taille et design des affiches.txt
    ├── Temps (créneaux horaires).txt
    ├── Éclairage ou animations.txt
## Remarques
Assurez-vous que tous les fichiers nécessaires (Egerine_Stats.xlsx et le dossier BDD_parametres/) soient au même niveau que recommandation.py.

Le projet est optimisé pour une exécution locale via Streamlit.
