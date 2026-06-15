import pandas as pd
import streamlit as st
from io import BytesIO

from config import ColumnConfig


class UIComponents:
    """Reusable UI rendering helpers shared across tabs."""

    # ── Styling ───────────────────────────────────────────────────────────────

    @staticmethod
    def inject_css() -> None:
        st.markdown("""<style>
.field-label{font-size:.72em;color:#888;text-transform:uppercase;letter-spacing:.05em;margin-top:6px}
.field-value{font-size:.93em;margin-bottom:4px}
</style>""", unsafe_allow_html=True)

    @staticmethod
    def score_color(val):
        """Cell highlight style for SCORE TOTAL column."""
        if isinstance(val, (int, float)):
            if val >= 8: return "background:#d4edda;color:#155724;font-weight:bold"
            if val >= 5: return "background:#fff3cd;color:#856404;font-weight:bold"
            if val >= 0: return "background:#f8d7da;color:#721c24"
        return ""

    @staticmethod
    def score_badge(score: int) -> str:
        """Return a coloured emoji based on score."""
        if score >= 8: return "🟢"
        if score >= 5: return "🟡"
        return "🔴"

    # ── KPI row ───────────────────────────────────────────────────────────────

    @staticmethod
    def render_kpis(
        n_total: int,
        n_eligible: int,
        top_n: int,
        df_eligible: pd.DataFrame,
        top_df: pd.DataFrame,
    ) -> None:
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("📋 Candidatures", n_total)
        k2.metric("✅ Éligibles", n_eligible)
        k3.metric("🏆 Sélectionnées", min(int(top_n), n_eligible))
        k4.metric(
            "📊 Score moyen",
            f"{df_eligible['SCORE TOTAL /10'].mean():.1f}" if n_eligible else "—",
        )
        n_f = int(top_df["S: Femme co-fond. (0-1)"].sum()) if len(top_df) else 0
        k5.metric("👩 Femmes / Top N", f"{n_f}/{min(int(top_n), n_eligible)}")

    # ── Sidebar ───────────────────────────────────────────────────────────────

    @staticmethod
    def render_sidebar(df_scored: pd.DataFrame) -> dict:
        """Render the sidebar and return the current filter values as a dict."""
        st.sidebar.header("⚙️ Filtres de sélection")

        filters = {
            "req_dot":   st.sidebar.checkbox("Bénéficiaires The Dot uniquement", True),
            "req_pass":  st.sidebar.checkbox("Passport valide uniquement", True),
            "req_other": st.sidebar.checkbox("Exclure sélectionnés autre délégation", True),
            "req_visa":  st.sidebar.checkbox("Visa Schengen valide uniquement", False),
            "min_score": st.sidebar.slider("Score minimum", 0, 10, 0),
            "top_n":     st.sidebar.number_input("Top N à sélectionner", 1, 50, 10),
        }

        secs_all = ["Tous"] + sorted(
            [s for s in df_scored["Secteur"].dropna().unique() if s]
        )
        filters["secteur"] = st.sidebar.selectbox("Secteur", secs_all)

        st.sidebar.divider()
        st.sidebar.markdown("**Matrice de scoring (10 pts max)**")
        st.sidebar.markdown("""
| Critère | Pts |
|---|---|
| Région hors Grand Tunis | 0–1 |
| Femme co-fondatrice | 0–1 |
| Âge ≥ 2 ans | 0–1 |
| Nb employés (0-1 / 2-4 / 5-9 / 10+) | 0–3 |
| CA existant | 0–1 |
| Levée de fonds (equity ou quasi) | 0–1 |
| Présence internationale | 0–1 |
| Marché européen spécifiquement | 0–1 |

*Label SA, Salon intl et Objectifs sont affichés pour revue humaine mais ne sont pas comptabilisés dans le score.*
""")

        return filters

    # ── Score breakdown bar ───────────────────────────────────────────────────

    @staticmethod
    def render_score_breakdown(row: pd.Series, score_map: list) -> None:
        """Render a visual bar breakdown of individual score criteria."""
        st.markdown("**📊 Score détaillé**")
        for lbl, col, mx in score_map:
            s = int(row[col])
            bar = "🟩" * s + "⬜" * (mx - s)
            st.markdown(
                f"<small>{lbl}</small> {bar} **{s}/{mx}**",
                unsafe_allow_html=True,
            )
        st.markdown("---")
        st.markdown(
            f"<small>Label SA</small> **{row['Label Startup Act (info)']}** *(non scoré)*",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<small>Salon intl</small> **{row['Salon intl passé (info)']}** *(non scoré)*",
            unsafe_allow_html=True,
        )
        st.markdown("<small>Objectifs</small> *(revue humaine)*", unsafe_allow_html=True)
        st.caption(row["Objectifs VivaTech (qualitatif)"])

    # ── Startup card (expander) ───────────────────────────────────────────────

    @staticmethod
    def render_startup_card(i: int, row: pd.Series) -> None:
        sc = int(row["SCORE TOTAL /10"])
        emoji = UIComponents.score_badge(sc)
        with st.expander(
            f"{emoji} #{i} — **{row['Startup']}** | Score {sc}/10 | {row['Secteur']}"
        ):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**👤 Contact :** {row['Contact (nom)']}")
                st.markdown(f"**📧** {row['Email contact']}")
                st.markdown(f"**📞** {row['Téléphone contact']}")
                st.markdown(f"**🏷️ The Dot :** {row['Programme The Dot']}")
                st.markdown(f"**🌍 Région :** {row['Région']}")
                st.markdown(f"**🏢 Stade :** {row['Stade produit']}")
            with c2:
                st.markdown(
                    f"**✈️ Représentant :** {row['Représentant (nom)']} — {row['Représentant (fonction)']}"
                )
                st.markdown(f"**📧** {row['Représentant (email)']}")
                st.markdown(f"**📞** {row['Représentant (tél)']}")
                dot = "✅" if row["✅ Bénéficiaire The Dot"]  else "❌"
                pas = "✅" if row["✅ Passport valide"]        else "❌"
                vis = "✅" if row["✅ Visa valide"]             else "❌"
                oth = "✅" if row["✅ Non sélec. autre déleg."] else "❌"
                st.markdown(f"{dot} The Dot &nbsp; {pas} Passport &nbsp; {vis} Visa &nbsp; {oth} Non-délég.")
                st.markdown(f"**CA 2025 :** {row['CA 2025 (TND)']} TND")
                st.markdown(
                    f"**Levée (equity) :** {row['Levée fonds (equity)']} / {row['Montant levée (equity)']}"
                )
                st.markdown(
                    f"**Levée (quasi) :** {row['Levée fonds (quasi-equity)']} / {row['Montant levée (quasi-equity)']}"
                )
                st.markdown(f"**🏷️ Label SA :** {row['Label Startup Act (info)']} *(info)*")
                st.markdown(f"**🎪 Salon passé :** {row['Salon intl passé (info)']} *(info)*")
            with c3:
                UIComponents.render_score_breakdown(row, ColumnConfig.SCORE_MAP)

    # ── Field display (detail tab) ────────────────────────────────────────────

    @staticmethod
    def render_field(label: str, value: str) -> None:
        if value and value not in ["nan", "NaN", ""]:
            st.markdown(
                f"<div class='field-label'>{label}</div><div class='field-value'>{value}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div class='field-label'>{label}</div>"
                f"<div class='field-value' style='color:#ccc'>—</div>",
                unsafe_allow_html=True,
            )
