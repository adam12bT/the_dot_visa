import pandas as pd
import streamlit as st
from io import BytesIO

from config import ColumnConfig
from scoring import RowAccessor, EligibilityChecker, Scorer, DisplayFields


class DataProcessor:
    """
    Loads the raw Excel data and builds the fully scored DataFrame.
    All column mapping, eligibility checks, and score computation happen here.
    """

    SHEET_NAME = "Réponses au formulaire 1"

    @staticmethod
    @st.cache_data
    def load_raw(file) -> pd.DataFrame:
        return pd.read_excel(file, sheet_name=DataProcessor.SHEET_NAME, header=0)

    @staticmethod
    def _resolve_startup_name(r: "RowAccessor") -> str:
        """
        The form has two versions with conflicting column usage:
          - Early submissions (form v1): 'nom_startup' = contact family name,
            'nom_startup2' = actual startup name.
          - Later submissions (form v2): 'nom_startup' = actual startup name,
            'nom_startup2' is empty.

        Priority: prefer nom_startup2 (always the real name when present),
        then fall back to nom_startup.
        """
        return r.get("nom_startup2") or r.get("nom_startup") or "N/A"

    @staticmethod
    def build_scored(df_raw: pd.DataFrame) -> pd.DataFrame:
        rows = []
        # Filter out legend/empty rows at bottom of the Excel sheet
        horodateur_col = ColumnConfig.COLUMNS.get("horodateur", "Horodateur")
        if horodateur_col in df_raw.columns:
            valid = df_raw[horodateur_col].apply(
                lambda v: pd.notna(v) and hasattr(v, 'year') or (
                    pd.notna(v) and str(v).strip() not in ("", "nan")
                    and not any(str(v).strip().startswith(x) for x in
                                ["Code", "Candidature", "N'ont", "Ne font"])
                )
            )
            df_raw = df_raw[valid].reset_index(drop=True)

        for _, row in df_raw.iterrows():
            r       = RowAccessor(row)
            elig    = EligibilityChecker(row)
            scorer  = Scorer(row)
            display = DisplayFields(row)

            # FIX: nom_startup2 takes priority — it is always the real startup
            # name when present; nom_startup in early rows holds the contact surname.
            name = DataProcessor._resolve_startup_name(r)

            e = elig.as_dict()
            s = scorer.as_dict()

            rows.append({
                # ── Identity ────────────────────────────────────────────────
                "Startup":                        name,
                "Horodateur":                     r.get("horodateur"),
                "Email formulaire":               r.get("email_form"),
                "Contact (nom)":                  r.get("nom_contact"),
                "Email contact":                  r.get("email"),
                "Téléphone contact":              r.get("tel"),
                "Position dans startup":          r.get("position"),
                # ── Profile ─────────────────────────────────────────────────
                "Secteur":                        r.get("secteur"),
                "Site web / LinkedIn":            r.get("website"),
                "Pitch Deck":                     r.get("pitch"),
                "Âge startup":                    r.get("age"),
                "Région":                         r.get("region"),
                "Nb employés":                    r.get("employes"),
                "Stade produit":                  r.get("stade"),
                "Description produit":            r.get("description"),
                # ── Programme & Label ────────────────────────────────────────
                "Programme The Dot":              r.get("dot_prog"),
                "Label Startup Act (info)":       display.label_startup_act(),
                # ── Finances ─────────────────────────────────────────────────
                "Génère un CA":                   r.get("ca_yn"),
                "CA 2025 (déclaré)":              r.get("ca_val"),
                "CA 2025 (TND)":                  r.get("ca_tnd"),
                "Traction locale":                r.get("traction"),
                # ── Fundraising ──────────────────────────────────────────────
                "Levée fonds (equity)":           r.get("fonds_yn"),
                "Montant levée (equity)":         r.get("fonds_amnt"),
                "Levée fonds (quasi-equity)":     r.get("fonds_yn2"),
                "Montant levée (quasi-equity)":   r.get("fonds_amnt2"),
                # ── International ────────────────────────────────────────────
                "Présence internationale":        r.get("intl_yn"),
                "Pays / marchés ciblés":          r.get("intl_pays"),
                "Clients / partenaires intl":     r.get("intl_clients"),
                "CA ou contrats à l'étranger":    r.get("intl_ca"),
                # ── Product / GTM ────────────────────────────────────────────
                "Utilisateurs pilotes":           r.get("users_pilot"),
                "État avancement / GTM":          r.get("gtm"),
                # ── Events & Objectives (display only) ──────────────────────
                "Salon intl passé (info)":        display.salon_international(),
                "Salon(s) précédent(s)":          r.get("salon_nom"),
                "Salon + délégation officielle":  r.get("salon_deleg"),
                "Objectifs VivaTech (qualitatif)":display.objectifs(),
                "Détail objectifs":               r.get("obj_detail"),
                # ── Paris representative ─────────────────────────────────────
                "Représentant (nom)":             r.get("rep_nom"),
                "Représentant (fonction)":        r.get("rep_func"),
                "Représentant (email)":           r.get("rep_mail"),
                "Représentant (tél)":             r.get("rep_tel"),
                # ── Administrative ───────────────────────────────────────────
                "Femme co-fondatrice":            r.get("femme"),
                "Passport valide":                r.get("passport"),
                "Visa Schengen valide":           r.get("visa"),
                "Engagement éval. post-event":    r.get("eval_post"),
                "Droit à l'image":                r.get("droit_image"),
                # ── Eligibility flags ────────────────────────────────────────
                "✅ Bénéficiaire The Dot":        e["e_dot"],
                "✅ Passport valide":             e["e_pass"],
                "✅ Visa valide":                 e["e_visa"],
                "✅ Non sélec. autre déleg.":     e["e_other"],
                "ELIGIBLE":                       elig.is_eligible(),
                # ── Scores (formula: Region+Genre+Age+Employes+CA+Fonds+IntlYn+IntlEU) ──
                "S: Région hors Gd Tunis (0-1)":  s["s_reg"],
                "S: Femme co-fond. (0-1)":         s["s_gen"],
                "S: Âge ≥2 ans (0-1)":            s["s_age"],
                "S: Nb employés (0-3)":            s["s_emp"],
                "S: CA existant (0-1)":            s["s_ca"],
                "S: Levée fonds (0-1)":            s["s_fond"],
                "S: Présence intl (0-1)":          s["s_intl"],
                "S: Marché européen (0-1)":        s["s_eu"],
                "SCORE TOTAL /10":                 s["total"],
            })

        df = pd.DataFrame(rows)

        # De-duplicate: when the same startup submitted multiple times, keep the
        # best single submission. Priority: eligible first (eligible > ineligible),
        # then highest score, then most recent timestamp. This matches what the
        # human Excel scorer did (e.g. CHITELIX submitted twice — the eligible
        # submission with visa is kept even if the other has a higher raw score).
        df = (
            df.sort_values(
                ["ELIGIBLE", "SCORE TOTAL /10"],
                ascending=[False, False],
            )
            .drop_duplicates(subset=["Startup"], keep="first")
            .sort_values("SCORE TOTAL /10", ascending=False)
            .reset_index(drop=True)
        )

        return df

    @staticmethod
    def apply_filters(
        df: pd.DataFrame,
        req_dot: bool,
        req_pass: bool,
        req_other: bool,
        req_visa: bool,
        min_score: int,
        secteur: str,
    ) -> pd.DataFrame:
        """Apply sidebar filters and return the filtered, sorted DataFrame."""
        out = df.copy()
        if req_dot:   out = out[out["✅ Bénéficiaire The Dot"]]
        if req_pass:  out = out[out["✅ Passport valide"]]
        if req_other: out = out[out["✅ Non sélec. autre déleg."]]
        if req_visa:  out = out[out["✅ Visa valide"]]
        if secteur != "Tous":
            out = out[out["Secteur"].str.contains(secteur, na=False)]
        return out[out["SCORE TOTAL /10"] >= min_score].sort_values(
            "SCORE TOTAL /10", ascending=False
        )

    @staticmethod
    def make_excel(top: pd.DataFrame, eligible: pd.DataFrame, full: pd.DataFrame) -> bytes:
        """Build a three-sheet Excel workbook and return its bytes."""
        out = BytesIO()
        score_cols = ColumnConfig.SCORE_COLS
        with pd.ExcelWriter(out, engine="openpyxl") as w:
            top[[c for c in score_cols if c in top.columns]].to_excel(
                w, sheet_name="Sélection Finale", index=True
            )
            eligible[[c for c in score_cols if c in eligible.columns]].to_excel(
                w, sheet_name="Tous les Éligibles", index=False
            )
            full.to_excel(w, sheet_name="Scoring Complet", index=False)
        return out.getvalue()