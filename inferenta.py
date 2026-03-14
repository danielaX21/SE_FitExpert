"""
inferenta.py  –  Motorul de inferență (Forward Chaining)
Autor: Vanya Iulia-Maria
Rol:   Baza de cunoștințe + Mașina de inferență
"""

import json


def incarca_baza(cale="baza_cunostinte.json"):
    """Încarcă baza de cunoștințe din fișierul JSON."""
    with open(cale, "r", encoding="utf-8") as f:
        return json.load(f)


class MotorInferenta:
    """
    Mașină de inferență Forward Chaining (Înlănțuire înainte).

    Procesul:
      1. Pornește de la faptele furnizate de utilizator (premise).
      2. Parcurge toate regulile din baza de cunoștințe.
      3. Dacă condițiile unei reguli sunt satisfăcute → aplică concluzia.
      4. Faptele noi deduse pot activa alte reguli (înlănțuire).
      5. Se oprește când nu mai există nicio regulă activabilă.
    """

    def __init__(self, baza: dict):
        self.reguli  = baza["reguli"]
        self.default = baza["default"]

    def ruleaza(self, fapte_initiale: dict):
        """
        Rulează Forward Chaining pe faptele utilizatorului.

        Parametri:
            fapte_initiale: dict cu răspunsurile colectate din UI
                            ex: {"obiectiv": "Slăbit intens", "mediu": "Acasă / Individual", ...}

        Returnează:
            recomandari: list of dict  – top 3 sporturi recomandate (sortate după confidence)
            explicatie:  list of str   – traseul de inferență pas cu pas
        """
        fapte    = dict(fapte_initiale)   # copie locală, nu modificăm originalul
        explicatie  = []
        recomandari = {}                  # sport → {sport, justificare, score, matched}

        # ── BUCLA FORWARD CHAINING ──────────────────────────────────────
        # Continuăm cât timp cel puțin o regulă a produs un fapt nou.
        # Aceasta implementează strategia "data-driven" (bazată pe date).
        schimbat = True
        while schimbat:
            schimbat = False

            for regula in self.reguli:
                conditii = regula["daca"]

                # Verificăm dacă TOATE condițiile regulii sunt satisfăcute
                if not all(fapte.get(k) == v for k, v in conditii.items()):
                    continue   # regula nu se aplică → trecem mai departe

                # ── Reguli INTERMEDIARE (deduc fapte noi) ──
                # Ex: obiectiv="Slăbit intens" → tip="Cardio"
                if "atunci_fapt" in regula:
                    for k, v in regula["atunci_fapt"].items():
                        if fapte.get(k) != v:
                            fapte[k] = v
                            explicatie.append(
                                f"[FAPT NOU] {k} = \"{v}\"  "
                                f"(dedus din: {conditii})"
                            )
                            schimbat = True   # s-a adăugat un fapt → mai rulăm o dată

                # ── Reguli FINALE (produc o recomandare) ──
                # Ex: tip="Cardio" + mediu="Acasă" → "Home HIIT"
                if "atunci" in regula:
                    sport  = regula["atunci"]
                    scor   = regula.get("confidence", 0.7)

                    # Păstrăm recomandarea cu cel mai mare scor de certitudine
                    if sport not in recomandari or recomandari[sport]["score"] < scor:
                        recomandari[sport] = {
                            "sport":       sport,
                            "justificare": regula["justificare"],
                            "score":       scor,
                            "matched":     list(conditii.keys())
                        }
                        explicatie.append(
                            f"[REGULĂ ACTIVĂ] → \"{sport}\"  "
                            f"(confidence: {int(scor*100)}%,  condiții: {conditii})"
                        )

        # ── SORTARE ȘI SELECȚIE TOP 3 ───────────────────────────────────
        lista = sorted(recomandari.values(),
                       key=lambda x: x["score"], reverse=True)

        # Dacă nu s-a activat nicio regulă finală → recomandare implicită
        if not lista:
            d = self.default
            lista = [{
                "sport":       d["atunci"],
                "justificare": d["justificare"],
                "score":       d.get("confidence", 0.55),
                "matched":     []
            }]
            explicatie.append(
                "[DEFAULT] Nicio regulă specifică nu s-a potrivit → "
                "recomandare generală."
            )

        return lista[:3], explicatie