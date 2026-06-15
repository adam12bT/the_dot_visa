import pandas as pd
import streamlit as st
from io import BytesIO

from config import ColumnConfig
from data_processor import DataProcessor
from excel_generator import ExcelGenerator
from ui_components import UIComponents


class Tab1SelectionFinale:
    """🏆 Tab 1 — Final selection: top-N ranked startups with download."""

    def __init__(self, top_df: pd.DataFrame, df_f: pd.DataFrame, df_scored: pd.DataFrame, top_n: int):
        self._top_df   = top_df
        self._df_f     = df_f
        self._df_scored = df_scored
        self._top_n    = top_n

    def render(self) -> None:
        st.subheader(f"🏆 Top {self._top_n} Startups Sélectionnées")
        if len(self._top_df) == 0:
            st.warning("Aucune startup ne correspond aux critères. Ajustez les filtres.")
            return

        score_cols = ColumnConfig.SCORE_COLS
        disp = self._top_df[[c for c in score_cols if c in self._top_df.columns]]
        st.dataframe(
            disp.style.applymap(UIComponents.score_color, subset=["SCORE TOTAL /10"]),
            use_container_width=True,
            height=400,
        )

        xlsx_bytes = ExcelGenerator.generate(self._df_scored)
        st.download_button(
            "📥 Télécharger le fichier Excel complet (4 feuilles)",
            data=xlsx_bytes,
            file_name="vivatech_2026_selection.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

        st.divider()
        st.markdown("### 📜 Classement détaillé")
        for i, (_, row) in enumerate(self._top_df.iterrows(), 1):
            UIComponents.render_startup_card(i, row)


class Tab2ScoringComplet:
    """📊 Tab 2 — Full scoring table for all (or eligible-only) candidates."""

    def __init__(self, df_scored: pd.DataFrame, df_f: pd.DataFrame):
        self._df_scored = df_scored
        self._df_f      = df_f

    def render(self) -> None:
        st.subheader("📊 Tableau de Scoring — Toutes les candidatures")
        show_all = st.checkbox("Inclure les non-éligibles", True)
        base = self._df_scored if show_all else self._df_f
        score_cols = ColumnConfig.SCORE_COLS
        tbl = (
            base[[c for c in score_cols if c in base.columns]]
            .sort_values("SCORE TOTAL /10", ascending=False)
            .reset_index(drop=True)
        )
        tbl.index += 1
        st.dataframe(
            tbl.style.applymap(UIComponents.score_color, subset=["SCORE TOTAL /10"]),
            use_container_width=True,
            height=600,
        )

        out = BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as w:
            tbl.to_excel(w, sheet_name="Scoring", index=True)
        col_a, col_b = st.columns(2)
        with col_a:
            st.download_button(
                "📥 Télécharger ce tableau (simple)",
                data=out.getvalue(),
                file_name="vivatech_scoring.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        with col_b:
            full_bytes = ExcelGenerator.generate(self._df_scored)
            st.download_button(
                "📥 Télécharger le fichier complet (4 feuilles)",
                data=full_bytes,
                file_name="vivatech_2026_complet.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )


class Tab3DonneesCompletes:
    """📋 Tab 3 — Raw data browser with column group selector and full export."""

    def __init__(self, df_scored: pd.DataFrame):
        self._df_scored = df_scored

    def render(self) -> None:
        st.subheader("📋 Données Brutes — Tous les Champs")
        search = st.text_input("🔍 Rechercher une startup", "")
        base = self._df_scored.copy()
        if search:
            base = base[base["Startup"].str.contains(search, case=False, na=False)]

        groups = ColumnConfig.DATA_GROUPS
        sel_grps = st.multiselect(
            "Groupes à afficher", list(groups.keys()), default=list(groups.keys())
        )
        show_cols = []
        for g in sel_grps:
            show_cols += [c for c in groups[g] if c in base.columns]
        show_cols = list(dict.fromkeys(show_cols))

        st.dataframe(base[show_cols].reset_index(drop=True), use_container_width=True, height=600)

        out = BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as w:
            self._df_scored.to_excel(w, sheet_name="Données Complètes", index=False)
        st.download_button(
            "📥 Export complet (tous champs)",
            data=out.getvalue(),
            file_name="vivatech_2026_complet.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


class Tab4Statistiques:
    """📈 Tab 4 — Visual statistics for eligible candidates."""

    def __init__(self, df_f: pd.DataFrame, df_scored: pd.DataFrame):
        self._df_f      = df_f
        self._df_scored = df_scored

    def render(self) -> None:
        st.subheader("📈 Statistiques")
        if len(self._df_f) == 0:
            st.warning("Aucun éligible avec les filtres actuels.")
            return

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Distribution des scores (éligibles)**")
            st.bar_chart(self._df_f["SCORE TOTAL /10"].value_counts().sort_index())
        with c2:
            st.markdown("**Top secteurs (éligibles)**")
            st.bar_chart(self._df_f["Secteur"].value_counts().head(10))

        c3, c4 = st.columns(2)
        with c3:
            st.markdown("**Critères d'éligibilité (toutes candidatures)**")
            st.bar_chart(pd.Series({
                "The Dot":        int(self._df_scored["✅ Bénéficiaire The Dot"].sum()),
                "Passport":       int(self._df_scored["✅ Passport valide"].sum()),
                "Visa":           int(self._df_scored["✅ Visa valide"].sum()),
                "Non autre dél.": int(self._df_scored["✅ Non sélec. autre déleg."].sum()),
                "ÉLIGIBLES":      int(self._df_scored["ELIGIBLE"].sum()),
            }))
        with c4:
            st.markdown("**Score moyen par critère (éligibles)**")
            s_cols = [c for c in self._df_f.columns if c.startswith("S: ")]
            avg = self._df_f[s_cols].mean().rename(
                lambda x: x.replace("S: ", "").split(" (")[0]
            )
            st.bar_chart(avg)

        c5, c6 = st.columns(2)
        with c5:
            st.markdown("**Répartition régions (éligibles)**")
            st.bar_chart(self._df_f["Région"].value_counts())
        with c6:
            st.markdown("**Stade produit (éligibles)**")
            st.bar_chart(self._df_f["Stade produit"].value_counts())


class Tab5FicheDetaillee:
    """🔍 Tab 5 — Full detail view for a single selected startup."""

    def __init__(self, df_scored: pd.DataFrame):
        self._df_scored = df_scored

    def render(self) -> None:
        st.subheader("🔍 Fiche Détaillée d'une Startup")
        sel = st.selectbox("Choisir une startup", sorted(self._df_scored["Startup"].tolist()))
        row = self._df_scored[self._df_scored["Startup"] == sel].iloc[0]
        sc  = int(row["SCORE TOTAL /10"])
        badge = UIComponents.score_badge(sc)

        st.markdown(f"## {badge} {row['Startup']} — Score **{sc} / 10**")

        ce1, ce2, ce3, ce4, ce5 = st.columns(5)
        ce1.markdown(f"{'✅' if row['✅ Bénéficiaire The Dot']   else '❌'} **The Dot**")
        ce2.markdown(f"{'✅' if row['✅ Passport valide']         else '❌'} **Passport**")
        ce3.markdown(f"{'✅' if row['✅ Visa valide']              else '❌'} **Visa**")
        ce4.markdown(f"{'✅' if row['✅ Non sélec. autre déleg.']  else '❌'} **Non autre déleg.**")
        ce5.markdown(
            f"{'🟢 **ÉLIGIBLE**' if row['ELIGIBLE'] else '🔴 **NON ÉLIGIBLE**'}"
        )

        st.divider()

        for sec_title, fields in ColumnConfig.DETAIL_SECTIONS.items():
            with st.expander(sec_title, expanded=True):
                for label, col in fields:
                    val = str(row.get(col, "")) if col in row else ""
                    UIComponents.render_field(label, val)

        st.divider()
        st.markdown("### 📊 Détail du score")
        st.caption("Formule exacte : Région + Genre + Âge + Employés + CA + Fonds + IntlYn + IntlEU (max 10)")

        sdf = pd.DataFrame([
            {
                "Critère": lbl,
                "Score":   int(row[col]),
                "Max":     mx,
                "Barre":   "🟩" * int(row[col]) + "⬜" * (mx - int(row[col])),
            }
            for lbl, col, mx in ColumnConfig.SCORE_MAP_DETAIL
        ])
        sdf["Score/Max"] = sdf["Score"].astype(str) + "/" + sdf["Max"].astype(str)
        st.dataframe(sdf[["Critère", "Barre", "Score/Max"]], use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("### 📝 Champs qualitatifs (revue humaine — non scorés)")
        qi1, qi2, qi3 = st.columns(3)
        with qi1:
            st.markdown("**Label Startup Act**")
            st.info(row["Label Startup Act (info)"])
        with qi2:
            st.markdown("**Participation salon intl**")
            st.info(row["Salon intl passé (info)"])
        with qi3:
            st.markdown("**Objectifs VivaTech**")
            st.info(row["Objectifs VivaTech (qualitatif)"] or "—")