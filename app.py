import streamlit as st

from ui_components import UIComponents
from data_processor import DataProcessor
from tabs import (
    Tab1SelectionFinale,
    Tab2ScoringComplet,
    Tab3DonneesCompletes,
    Tab4Statistiques,
    Tab5FicheDetaillee,
)


class VivaTechApp:
    """
    Main application class — orchestrates page setup, data loading,
    sidebar filters, KPIs, and tab rendering.
    """

    def __init__(self):
        self._df_raw    = None
        self._df_scored = None
        self._df_f      = None
        self._top_df    = None
        self._filters   = {}

    # ── Bootstrap ─────────────────────────────────────────────────────────────

    def setup_page(self) -> None:
        st.set_page_config(
            page_title="VivaTech 2026 – Sélection",
            layout="wide",
            page_icon="🚀",
        )
        UIComponents.inject_css()
        st.title("🚀 VivaTech 2026 – Sélection Automatique des Startups")
        st.caption("Chargez le fichier Excel des candidatures pour lancer le scoring automatique.")

    def upload_file(self):
        uploaded = st.file_uploader("📂 Fichier Excel des candidatures", type=["xlsx"])
        if not uploaded:
            st.info("Veuillez charger le fichier Excel pour continuer.")
            st.stop()
        return uploaded

    # ── Data pipeline ─────────────────────────────────────────────────────────

    def load_and_score(self, uploaded_file) -> None:
        self._df_raw    = DataProcessor.load_raw(uploaded_file)
        self._df_scored = DataProcessor.build_scored(self._df_raw)

    def apply_filters(self) -> None:
        f = self._filters
        self._df_f = DataProcessor.apply_filters(
            self._df_scored,
            req_dot   = f["req_dot"],
            req_pass  = f["req_pass"],
            req_other = f["req_other"],
            req_visa  = f["req_visa"],
            min_score = f["min_score"],
            secteur   = f["secteur"],
        )
        top_n = int(f["top_n"])
        self._top_df = self._df_f.head(top_n).reset_index(drop=True)
        self._top_df.index += 1

    # ── Render ────────────────────────────────────────────────────────────────

    def render(self) -> None:
        self.setup_page()
        uploaded = self.upload_file()
        self.load_and_score(uploaded)

        # Sidebar filters (must come before apply_filters)
        self._filters = UIComponents.render_sidebar(self._df_scored)
        self.apply_filters()

        # KPI strip
        UIComponents.render_kpis(
            n_total    = len(self._df_raw),
            n_eligible = len(self._df_f),
            top_n      = self._filters["top_n"],
            df_eligible= self._df_f,
            top_df     = self._top_df,
        )
        st.divider()

        # Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🏆 Sélection Finale",
            "📊 Scoring Complet",
            "📋 Toutes les Données",
            "📈 Statistiques",
            "🔍 Fiche Détaillée",
        ])

        with tab1:
            Tab1SelectionFinale(
                self._top_df, self._df_f, self._df_scored, self._filters["top_n"]
            ).render()
        with tab2:
            Tab2ScoringComplet(self._df_scored, self._df_f).render()
        with tab3:
            Tab3DonneesCompletes(self._df_scored).render()
        with tab4:
            Tab4Statistiques(self._df_f, self._df_scored).render()
        with tab5:
            Tab5FicheDetaillee(self._df_scored).render()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    VivaTechApp().render()
