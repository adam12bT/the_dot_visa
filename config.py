class ColumnConfig:
    """Exact column name mappings from the Google Form export."""

    COLUMNS = {
        "horodateur":   "Horodateur",
        "email_form":   "Adresse e-mail",
        "nom_startup":  "Nom de la start-up ",
        "nom_contact":  "Votre nom et prénom",
        "email":        "Votre e-mail",
        "tel":          "Numéro de téléphone",
        "position":     "Votre position dans la start-up",
        "nom_startup2": "Quel est le nom de votre start-up?",
        "secteur":      "Quel est le secteur d'activité de votre start-up ?",
        "website":      "Le lien du site web ( ou page LinkedIn principale) ",
        "dot_prog":     "De quel programme de The Dot votre start-up a-t-elle bénéficié ? ",
        "label_sa":     "Votre start-up a-t-elle le label Start-up Act ? ",
        "age":          "Quel âge a votre start-up?",
        "region":       "Quelle est votre région d'implantation?",
        "description":  "Décrivez brièvement votre produit/solution (maximum 100 mots)",
        "employes":     "Nombre d'employés à plein temps au sein de l'équipe  ",
        "pitch":        "Lien vers la version la plus récente de votre Pitch Deck ( YouTube, drive...)",
        "ca_yn":        "Votre start-up génère-t-elle un chiffre d\u2019affaires ?",
        "ca_val":       "Quel est le chiffre d'affaire que votre startup a généré en 2025 ? ",
        "traction":     "Traction commerciale sur le marché local ",
        "intl_yn":      "Votre start-up est-elle déjà présente sur le marché européen ou international ? ",
        "intl_pays":    "Si oui, précisez brièvement (Pays cibles, clients majeurs ou CA à l'export)  ",
        "intl_clients": "Si oui, merci de préciser vos principaux clients ou partenaires à l\u2019international.\n",
        "intl_ca":      "Si oui, merci de préciser le chiffre d\u2019affaires estimé ou le nombre de contrats signés à l\u2019étranger",
        "fonds_yn":     "Avez-vous déjà levé des fonds (equity ou quasi-equity)?",
        "fonds_amnt":   "Si oui, quel est le montant total cumulé et l'année de la dernière levée ? ( précisez la devise)",
        "objectifs":    "Quels sont les objectifs prioritaires de votre participation à VivaTech ? (Maximum 2 choix) ",
        "users_pilot":  "Si oui, précisez le nombre d'utilisateurs ayant validé votre solution ",
        "gtm":          "Pouvez-vous préciser l\u2019état d\u2019avancement de votre projet ainsi que votre calendrier de mise sur le marché (go-to-market) ? ",
        "fonds_yn2":    "Avez-vous déjà levé des fonds (equity ou quasi equity)?",
        "fonds_amnt2":  "Si oui, quel est le montant du ticket et l\u2019année d\u2019obtention?",
        "obj_detail":   "Fonction de cette personne au sein de la start-up",
        "salon_yn":     "Avez-vous déjà participé à un salon international auparavant?",
        "salon_nom":    "Si Oui, Le(s)quel(s) ?",
        "rep_nom":      "Nom & prénom de la personne qui représentera physiquement la start-up à Paris ",
        "rep_func":     "La fonction au sein de l'entreprise de la personne participante",
        "rep_mail":     "Adresse mail ",
        "rep_tel":      "Contact téléphone ",
        "passport":     "La personne représentant la structure dispose-t-elle d\u2019un passeport valide au moins 3 mois à compter de son entrée en France (soit à compter du 15 juin 2026)  ",
        "femme":        " Y a-t-il une femme parmi les co-fondateurs ?  ",
        "visa":         "La personne représentant la structure dispose-t-elle d\u2019un Visa Schengen valide pour la période du 17 au 20 Juin 2026? ",
        "ca_tnd":       "Si oui, quel a été votre chiffre d'affaires global en 2025 (en TND)?",
        "stade":        "Quel est le stade de développement actuel de votre produit?",
        "salon_deleg":  "Si oui, à quel salon (nom et année) ? Faisiez-vous partie d'une délégation officielle soutenue par Expertise France, la Fondation Tunisie pour le Développement ou la GIZ Tunisie ?",
        "eval_post":    "Évaluation Post-Événement  ",
        "droit_image":  "Autorisation d'utilisation de l'image (Droit à l'image)  ",
    }

    SCORE_COLS = [
        "Startup", "Secteur", "Contact (nom)", "Email contact", "Téléphone contact",
        "SCORE TOTAL /10",
        "S: Région hors Gd Tunis (0-1)", "S: Femme co-fond. (0-1)",
        "S: Âge ≥2 ans (0-1)", "S: Nb employés (0-3)", "S: CA existant (0-1)",
        "S: Levée fonds (0-1)", "S: Présence intl (0-1)", "S: Marché européen (0-1)",
        "Label Startup Act (info)", "Salon intl passé (info)", "Objectifs VivaTech (qualitatif)",
        "✅ Bénéficiaire The Dot", "✅ Passport valide", "✅ Visa valide", "✅ Non sélec. autre déleg.",
        "Représentant (nom)", "Représentant (email)", "Représentant (tél)", "Représentant (fonction)",
    ]

    DATA_GROUPS = {
        "Identité & Contact":   ["Startup", "Horodateur", "Email formulaire", "Contact (nom)", "Email contact", "Téléphone contact", "Position dans startup"],
        "Programme & Label":    ["Programme The Dot", "Label Startup Act (info)"],
        "Profil Startup":       ["Secteur", "Site web / LinkedIn", "Pitch Deck", "Âge startup", "Région", "Nb employés", "Stade produit", "Description produit"],
        "Finances":             ["Génère un CA", "CA 2025 (déclaré)", "CA 2025 (TND)", "Traction locale"],
        "Levée de fonds":       ["Levée fonds (equity)", "Montant levée (equity)", "Levée fonds (quasi-equity)", "Montant levée (quasi-equity)"],
        "International":        ["Présence internationale", "Pays / marchés ciblés", "Clients / partenaires intl", "CA ou contrats à l'étranger"],
        "Produit / GTM":        ["Utilisateurs pilotes", "État avancement / GTM"],
        "Salons & Objectifs":   ["Salon intl passé (info)", "Salon(s) précédent(s)", "Salon + délégation officielle", "Objectifs VivaTech (qualitatif)", "Détail objectifs"],
        "Représentant Paris":   ["Représentant (nom)", "Représentant (fonction)", "Représentant (email)", "Représentant (tél)"],
        "Administratif":        ["Femme co-fondatrice", "Passport valide", "Visa Schengen valide", "Engagement éval. post-event", "Droit à l'image"],
        "Éligibilité":          ["✅ Bénéficiaire The Dot", "✅ Passport valide", "✅ Visa valide", "✅ Non sélec. autre déleg.", "ELIGIBLE"],
        "Scores":               ["SCORE TOTAL /10", "S: Région hors Gd Tunis (0-1)", "S: Femme co-fond. (0-1)",
                                 "S: Âge ≥2 ans (0-1)", "S: Nb employés (0-3)", "S: CA existant (0-1)",
                                 "S: Levée fonds (0-1)", "S: Présence intl (0-1)", "S: Marché européen (0-1)"],
    }

    SCORE_MAP = [
        ("Région hors Gd Tunis", "S: Région hors Gd Tunis (0-1)", 1),
        ("Femme co-fond.",       "S: Femme co-fond. (0-1)",        1),
        ("Âge ≥ 2 ans",         "S: Âge ≥2 ans (0-1)",           1),
        ("Nb employés",          "S: Nb employés (0-3)",           3),
        ("CA existant",          "S: CA existant (0-1)",           1),
        ("Levée de fonds",       "S: Levée fonds (0-1)",           1),
        ("Présence intl",        "S: Présence intl (0-1)",         1),
        ("Marché EU",            "S: Marché européen (0-1)",       1),
    ]

    SCORE_MAP_DETAIL = [
        ("Région hors Grand Tunis",  "S: Région hors Gd Tunis (0-1)", 1),
        ("Femme co-fondatrice",      "S: Femme co-fond. (0-1)",        1),
        ("Âge ≥ 2 ans",             "S: Âge ≥2 ans (0-1)",           1),
        ("Nombre d'employés",        "S: Nb employés (0-3)",           3),
        ("CA existant",              "S: CA existant (0-1)",           1),
        ("Levée de fonds",           "S: Levée fonds (0-1)",           1),
        ("Présence internationale",  "S: Présence intl (0-1)",         1),
        ("Marché européen",          "S: Marché européen (0-1)",       1),
    ]

    DETAIL_SECTIONS = {
        "👤 Identité & Contact": [
            ("Horodateur", "Horodateur"), ("Email formulaire", "Email formulaire"),
            ("Nom", "Contact (nom)"), ("Email", "Email contact"),
            ("Téléphone", "Téléphone contact"), ("Position", "Position dans startup"),
        ],
        "🏢 Profil Startup": [
            ("Secteur", "Secteur"), ("Site web", "Site web / LinkedIn"),
            ("Pitch Deck", "Pitch Deck"), ("Âge", "Âge startup"),
            ("Région", "Région"), ("Nb employés", "Nb employés"), ("Stade", "Stade produit"),
        ],
        "📝 Programme & Label": [
            ("Programme The Dot", "Programme The Dot"),
            ("Label SA (info)", "Label Startup Act (info)"),
        ],
        "📖 Description": [
            ("Description", "Description produit"),
        ],
        "💰 Finances": [
            ("Génère CA", "Génère un CA"), ("CA 2025 (déclaré)", "CA 2025 (déclaré)"),
            ("CA 2025 (TND)", "CA 2025 (TND)"), ("Traction", "Traction locale"),
        ],
        "💼 Levée de fonds": [
            ("Equity", "Levée fonds (equity)"), ("Montant equity", "Montant levée (equity)"),
            ("Quasi-equity", "Levée fonds (quasi-equity)"), ("Montant quasi", "Montant levée (quasi-equity)"),
        ],
        "🌍 International": [
            ("Présence intl", "Présence internationale"), ("Pays / marchés", "Pays / marchés ciblés"),
            ("Clients intl", "Clients / partenaires intl"), ("CA / contrats", "CA ou contrats à l'étranger"),
        ],
        "🚀 Produit / GTM": [
            ("Utilisateurs pilotes", "Utilisateurs pilotes"), ("État / GTM", "État avancement / GTM"),
        ],
        "🎪 Salons & Objectifs": [
            ("Salon passé (info)", "Salon intl passé (info)"), ("Salon(s)", "Salon(s) précédent(s)"),
            ("Délégation officielle", "Salon + délégation officielle"),
            ("Objectifs VivaTech", "Objectifs VivaTech (qualitatif)"),
            ("Détail objectifs", "Détail objectifs"),
        ],
        "✈️ Représentant à Paris": [
            ("Nom", "Représentant (nom)"), ("Fonction", "Représentant (fonction)"),
            ("Email", "Représentant (email)"), ("Tél", "Représentant (tél)"),
        ],
        "📋 Administratif": [
            ("Femme co-fondatrice", "Femme co-fondatrice"), ("Passport", "Passport valide"),
            ("Visa", "Visa Schengen valide"), ("Éval. post-event", "Engagement éval. post-event"),
            ("Droit image", "Droit à l'image"),
        ],
    }
