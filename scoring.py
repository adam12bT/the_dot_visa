import re
import pandas as pd
from config import ColumnConfig


class RowAccessor:
    """Helper for safely reading cell values from a DataFrame row."""

    def __init__(self, row: pd.Series):
        self._row = row

    def get(self, key: str) -> str:
        col = ColumnConfig.COLUMNS.get(key)
        if col and col in self._row:
            val = self._row[col]
            if pd.isna(val):
                return ""
            return str(val).strip()
        return ""

    @staticmethod
    def is_oui(val: str) -> bool:
        return str(val).strip().lower() in ["oui", "yes", "true", "1", "vrai"]


class EligibilityChecker:
    """
    Hard eligibility gates — binary pass/fail, not scored.
    Source: 'Methode de scoring' sheet — Critères d'éligibilité.
    """

    OFFICIAL_DELEGATIONS = [
        "expertise france",
        "fondation tunisie pour le développement",
        "fondation tunisie",
        "giz tunisie",
        "giz",
        "cepex",
        "mtc",
    ]

    def __init__(self, row: pd.Series):
        self._r = RowAccessor(row)

    def check_dot(self) -> bool:
        """Must be a The Dot programme beneficiary."""
        val = self._r.get("dot_prog")
        if not val:
            return False
        return (
            "aucun" not in val.lower()
            and "je n'ai bénéficié d'aucun" not in val.lower()
        )

    def check_passport(self) -> bool:
        """Representative must have a valid passport ≥3 months after June 15 2026."""
        return RowAccessor.is_oui(self._r.get("passport"))

    def check_visa(self) -> bool:
        """Representative must have a valid Schengen visa for Jun 17-20 2026."""
        return RowAccessor.is_oui(self._r.get("visa"))

    def check_not_other_delegation(self) -> bool:
        """
        Must NOT be currently selected to represent Tunisia at VivaTech 2026
        via another official delegation (Expertise France, GIZ, MTC, CEPEX…).

        The 'salon_deleg' field records PAST salon participation with official
        delegations — mentioning GIZ/MTC for a previous Gitex does NOT disqualify.
        Only an explicit reference to VivaTech 2026 / Paris 2026 alongside an
        official delegation body would disqualify.
        """
        val = self._r.get("salon_deleg").lower()
        if not val:
            return True
        # Only flag as conflicted if the entry explicitly mentions going to
        # VivaTech 2026 or Paris 2026 with an official delegation
        vivatech_keywords = ["vivatech 2026", "paris 2026", "vivatech26"]
        has_vivatech = any(k in val for k in vivatech_keywords)
        has_official = any(d in val for d in self.OFFICIAL_DELEGATIONS)
        return not (has_vivatech and has_official)

    def is_eligible(self, require_visa: bool = False) -> bool:
        """
        Returns True if the startup passes all mandatory gates.
        Visa check is optional (controlled by the sidebar toggle).
        """
        passes = self.check_dot() and self.check_passport() and self.check_not_other_delegation()
        if require_visa:
            passes = passes and self.check_visa()
        return passes

    def as_dict(self) -> dict:
        return {
            "e_dot":   self.check_dot(),
            "e_pass":  self.check_passport(),
            "e_visa":  self.check_visa(),
            "e_other": self.check_not_other_delegation(),
        }


class Scorer:
    """
    Scoring logic — exact formula from the 'Evaluation' sheet: I+J+L+M+N+O+R+S
    = Region + Genre + Age + Employes + CA + Fonds + IntlYn + IntlEU  (max 10 pts).

    NOT included in formula (display-only):
      - Label Startup Act (col K)
      - Participation salon (col P)
      - Objectifs (col Q) — qualitative, human review only
    """

    EU_KEYWORDS = [
        "france", "allemagne", "germany", "italie", "italy", "espagne", "spain",
        "belgique", "belgium", "portugal", "europe", "european", "uk", "united kingdom",
        "pays-bas", "netherlands", "suède", "sweden", "suisse", "switzerland",
        "autriche", "austria", "pologne", "poland", "luxembourg", "danemark", "denmark",
        "norvège", "norway", "finlande", "finland", "grèce", "greece",
        "irlande", "ireland", "tchèque", "czech", "roumanie", "romania",
        "hongrie", "hungary", "slovaquie", "slovakia", "croatie", "croatia", "dach",
    ]

    GRAND_TUNIS = ["tunis", "ariana", "ben arous", "manouba"]

    def __init__(self, row: pd.Series):
        self._r = RowAccessor(row)

    def score_region(self) -> int:
        """Région hors Grand Tunis → 1 pt; Grand Tunis → 0 pt."""
        val = self._r.get("region").lower()
        return 0 if any(g in val for g in self.GRAND_TUNIS) else 1

    def score_genre(self) -> int:
        """Femme parmi les co-fondateurs → 1 pt; Aucune → 0 pt."""
        return 1 if RowAccessor.is_oui(self._r.get("femme")) else 0

    def score_age(self) -> int:
        """Âge ≥ 2 ans → 1 pt; Moins de 2 ans → 0 pt."""
        val = self._r.get("age")
        if not val:
            return 0
        vl = val.lower()

        # Explicit month pattern e.g. "18 mois"
        months_match = re.search(r'(\d+(?:[.,]\d+)?)\s*mois', vl)
        if months_match:
            months = float(months_match.group(1).replace(',', '.'))
            return 1 if months >= 24 else 0

        # Combined "X ans, Y mois"
        combo = re.search(r'(\d+)\s*ans?\s*[,\s]+(\d+)\s*mois', vl)
        if combo:
            total_months = int(combo.group(1)) * 12 + int(combo.group(2))
            return 1 if total_months >= 24 else 0

        # Plain number (assume years)
        nums = re.findall(r'\d+(?:[.,]\d+)?', vl)
        if nums:
            n = float(nums[0].replace(',', '.'))
            if n < 2:
                return 0
            if n > 11 and "an" not in vl and "year" not in vl:
                return 1 if n >= 24 else 0
            return 1

        NEG = ["3 mois", "6 mois", "1 an", "one year", "1 year", "moins de 2", "un an"]
        if any(x in vl for x in NEG):
            return 0

        return 1

    def score_employes(self) -> int:
        """0–1 → 0 pt | 2–4 → 1 pt | 5–9 → 2 pt | 10+ → 3 pt  (max 3)."""
        val = self._r.get("employes")
        if not val:
            return 0
        try:
            n = int(float(str(val).replace(',', '.')))
            if n <= 1:  return 0
            if n <= 4:  return 1
            if n <= 9:  return 2
            return 3
        except Exception:
            return 0

    def score_ca(self) -> int:
        """Génère un CA → 1 pt; Non → 0 pt."""
        return 1 if RowAccessor.is_oui(self._r.get("ca_yn")) else 0

    def score_fonds(self) -> int:
        """A levé des fonds (equity OU quasi-equity) → 1 pt; Aucune → 0 pt."""
        return 1 if (
            RowAccessor.is_oui(self._r.get("fonds_yn"))
            or RowAccessor.is_oui(self._r.get("fonds_yn2"))
        ) else 0

    def score_intl_yn(self) -> int:
        """Présence sur marché international → 1 pt; Non → 0 pt."""
        return 1 if RowAccessor.is_oui(self._r.get("intl_yn")) else 0

    def score_intl_eu(self) -> int:
        """Présence spécifiquement sur marché EUROPÉEN → 1 pt; Absent → 0 pt."""
        if not RowAccessor.is_oui(self._r.get("intl_yn")):
            return 0
        pays_text = " ".join([
            self._r.get("intl_pays"),
            self._r.get("intl_clients"),
            self._r.get("intl_ca"),
            self._r.get("gtm"),
            self._r.get("objectifs"),
        ]).lower()
        return 1 if any(k in pays_text for k in self.EU_KEYWORDS) else 0

    def total(self) -> int:
        """Sum of all scored criteria (max 10)."""
        return (
            self.score_region()
            + self.score_genre()
            + self.score_age()
            + self.score_employes()
            + self.score_ca()
            + self.score_fonds()
            + self.score_intl_yn()
            + self.score_intl_eu()
        )

    def as_dict(self) -> dict:
        return {
            "s_reg":  self.score_region(),
            "s_gen":  self.score_genre(),
            "s_age":  self.score_age(),
            "s_emp":  self.score_employes(),
            "s_ca":   self.score_ca(),
            "s_fond": self.score_fonds(),
            "s_intl": self.score_intl_yn(),
            "s_eu":   self.score_intl_eu(),
            "total":  self.total(),
        }


class DisplayFields:
    """
    Fields shown for human review only — NOT part of the scoring formula.
    Source: confirmed from the Evaluation sheet (cols K, P, Q).
    """

    def __init__(self, row: pd.Series):
        self._r = RowAccessor(row)

    def label_startup_act(self) -> str:
        return "Oui" if RowAccessor.is_oui(self._r.get("label_sa")) else "Non"

    def salon_international(self) -> str:
        return "Oui" if RowAccessor.is_oui(self._r.get("salon_yn")) else "Non"

    def objectifs(self) -> str:
        return self._r.get("objectifs")