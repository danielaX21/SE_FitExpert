"""
inferenta.py  –  Motorul de inferență (Forward Chaining)
Autor: Vanya Iulia-Maria
Rol:   Baza de cunoștințe + Mașina de inferență

Algoritm: Forward Chaining (Înlănțuire înainte)
  Pornește de la faptele utilizatorului și aplică reguli
  până când nu mai există nicio regulă activabilă.
  Suportă reguli intermediare (care deduc fapte noi)
  și reguli finale (care produc recomandări de sporturi).
  Conflictele dintre reguli sunt rezolvate prin confidence.
"""

import json


def incarca_baza(cale="baza_cunostinte.json"):
    """
    Încarcă baza de cunoștințe din fișierul JSON.

    Parametri:
        cale (str): calea relativă sau absolută a fișierului JSON

    Returnează:
        dict: dicționarul complet cu 'intrebari', 'reguli', 'default'

    Ridică:
        FileNotFoundError: dacă fișierul nu există
        json.JSONDecodeError: dacă fișierul nu este JSON valid
    """
    with open(cale, "r", encoding="utf-8") as f:
        return json.load(f)


class MotorInferenta:
    """
    Mașină de inferență Forward Chaining (Înlănțuire înainte).

    Procesul de inferență:
      1. Pornește de la faptele furnizate de utilizator (premise).
      2. Parcurge TOATE regulile din baza de cunoștințe.
      3. Dacă TOATE condițiile unei reguli sunt satisfăcute:
         a. Reguli intermediare -> adaugă fapte noi în memorie de lucru
         b. Reguli finale       -> înregistrează o recomandare
      4. Dacă s-a adăugat cel puțin un fapt nou -> repetă de la 2.
      5. Se oprește când nicio regulă nu mai poate fi activată.
      6. Rezolvă conflictele: dacă două reguli recomandă același
         sport, câștigă cea cu valoarea 'confidence' mai mare.
      7. Returnează top 3 recomandări sortate descrescător.

    Atribute:
        reguli  (list): lista de reguli din baza de cunoștințe
        default (dict): recomandarea implicită dacă nicio regulă nu se activează
    """

    def __init__(self, baza: dict):
        """
        Inițializează motorul cu o bază de cunoștințe încărcată.

        Parametri:
            baza (dict): dicționarul returnat de incarca_baza()
        """
        self.reguli  = baza["reguli"]
        self.default = baza["default"]

    def ruleaza(self, fapte_initiale: dict):
        """
        Rulează algoritmul Forward Chaining pe faptele utilizatorului.

        Parametri:
            fapte_initiale (dict): răspunsurile colectate din interfață
                ex: {"obiectiv": "Slăbit intens", "mediu": "Acasă / Individual", ...}

        Returnează:
            tuple:
                recomandari (list[dict]): top 3 sporturi recomandate
                explicatie  (list[str]):  traseul complet de inferență
        """
        fapte       = dict(fapte_initiale)
        explicatie  = []
        recomandari = {}

        schimbat = True
        while schimbat:
            schimbat = False

            for regula in self.reguli:
                conditii = regula["daca"]

                if not all(fapte.get(k) == v for k, v in conditii.items()):
                    continue

                # Reguli INTERMEDIARE
                if "atunci_fapt" in regula:
                    for k, v in regula["atunci_fapt"].items():
                        if fapte.get(k) != v:
                            fapte[k] = v
                            schimbat  = True
                            explicatie.append(
                                f"[FAPT NOU] {k} = \"{v}\"  "
                                f"<- condiție satisfăcută: {conditii}"
                            )

                # Reguli FINALE
                if "atunci" in regula:
                    sport = regula["atunci"]
                    scor  = regula.get("confidence", 0.7)

                    conflict = self._rezolva_conflict(
                        recomandari, sport, scor, conditii, regula
                    )
                    if conflict["actualizat"]:
                        recomandari[sport] = conflict["rec"]
                        explicatie.append(
                            f"[REGULĂ ACTIVĂ] -> \"{sport}\" "
                            f"(confidence: {int(scor*100)}%)"
                        )
                    elif conflict["ignorat"]:
                        explicatie.append(
                            f"[CONFLICT REZOLVAT] \"{sport}\" există deja "
                            f"cu scor mai mare -> ignorat "
                            f"({int(scor*100)}% < "
                            f"{int(recomandari[sport]['score']*100)}%)"
                        )

        lista = sorted(
            recomandari.values(),
            key=lambda x: x["score"],
            reverse=True
        )

        if not lista:
            d = self.default
            lista = [{
                "sport":       d["atunci"],
                "justificare": d["justificare"],
                "score":       d.get("confidence", 0.55),
                "matched":     []
            }]
            explicatie.append(
                "[DEFAULT] Nicio regulă specifică activată -> "
                "recomandare generală implicită."
            )

        return lista[:3], explicatie

    def _rezolva_conflict(self, recomandari, sport, scor, conditii, regula):
        """
        Rezolvă conflictele când același sport este recomandat de mai multe reguli.

        Strategia: câștigă recomandarea cu valoarea 'confidence' cea mai mare.
        În caz de egalitate, se păstrează prima recomandare găsită.

        Returnează:
            dict cu cheile 'actualizat', 'ignorat', 'rec'
        """
        rec_noua = {
            "sport":       sport,
            "justificare": regula.get("justificare", ""),
            "score":       scor,
            "matched":     list(conditii.keys())
        }

        if sport not in recomandari:
            return {"actualizat": True, "ignorat": False, "rec": rec_noua}

        scor_existent = recomandari[sport]["score"]

        if scor > scor_existent:
            return {"actualizat": True, "ignorat": False, "rec": rec_noua}
        else:
            return {"actualizat": False, "ignorat": True, "rec": None}

    def genereaza_explicatii_human(self, fapte_initiale: dict, recomandari: list):
        """
        Generează explicații în limbaj natural (română) pentru utilizator.

        Traduce traseul tehnic de inferență în propoziții prietenoase,
        arătând utilizatorului DE CE sistemul a ajuns la acea concluzie.

        Parametri:
            fapte_initiale (dict): răspunsurile utilizatorului
            recomandari    (list): top 3 recomandări returnate de ruleaza()

        Returnează:
            list[str]: lista de propoziții explicative în română
        """
        linii = []

        obiectiv    = fapte_initiale.get("obiectiv",    "nespecificat")
        experienta  = fapte_initiale.get("experienta",  "nespecificat")
        mediu       = fapte_initiale.get("mediu",       "nespecificat")
        timp        = fapte_initiale.get("timp",        "nespecificat")

        linii.append(
            f"Pe baza profilului tau — obiectiv: {obiectiv}, "
            f"nivel: {experienta}, mediu preferat: {mediu} — "
            f"sistemul a parcurs baza de cunostinte si a activat regulile potrivite."
        )

        if recomandari:
            top = recomandari[0]
            linii.append(
                f"Cea mai buna potrivire este {top['sport']} "
                f"(certitudine {int(top['score']*100)}%) deoarece: "
                f"{top['justificare']}"
            )

        if len(recomandari) > 1:
            alternative = ", ".join(
                f"{r['sport']} ({int(r['score']*100)}%)"
                for r in recomandari[1:]
            )
            linii.append(f"Alternativele recomandate sunt: {alternative}.")

        if timp in ["5-7 ore", "8+ ore"]:
            linii.append(
                "Deoarece ai timp generos pe saptamana, poti combina "
                "mai multe tipuri de antrenament pentru rezultate optime."
            )
        elif timp == "1-2 ore":
            linii.append(
                "Cu timpul disponibil limitat, recomandarile sunt "
                "optimizate pentru eficienta maxima in sesiuni scurte."
            )

        return linii