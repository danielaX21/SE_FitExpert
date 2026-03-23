import json


def incarca_baza(cale="baza_cunostinte.json"):
    with open(cale, "r", encoding="utf-8") as f:
        return json.load(f)


class MotorInferenta:

    def __init__(self, baza: dict):
        self.reguli  = baza["reguli"]
        self.default = baza["default"]


    def ruleaza(self, fapte_initiale: dict):
        fapte = dict(fapte_initiale)
        explicatie = []
        
        # 1. Forward Chaining - Deducem fapte intermediare
        schimbat = True
        while schimbat:
            schimbat = False
            for regula in self.reguli:
                if "atunci_fapt" in regula:
                    conditii = regula["daca"]
                    if all(fapte.get(k) == v for k, v in conditii.items()):
                        for k, v in regula["atunci_fapt"].items():
                            if fapte.get(k) != v:
                                fapte[k] = v
                                schimbat = True
                                explicatie.append(f"[Deducție] Deoarece {conditii}, am stabilit că {k} = {v}")

        # 2. Colectare sporturi cu scor de potrivire (fără a-l afișa)
        recomandari_potentiale = []
        for regula in self.reguli:
            if "atunci" in regula:
                sport = regula["atunci"]
                conditii = regula["daca"]
                
                # Calculăm câte condiții din regulă sunt respectate de faptele noastre
                potriviri = sum(1 for k, v in conditii.items() if fapte.get(k) == v)
                total_cond = len(conditii)

                # Dacă există măcar o potrivire, considerăm sportul candidat
                if potriviri > 0:
                    recomandari_potentiale.append({
                        "sport": sport,
                        "justificare": regula.get("justificare", ""),
                        "complexitate": potriviri, 
                        "procent_logic": potriviri / total_cond, # Folosit doar pentru sortare internă
                        "score": 1.0
                    })

        # 3. Sortare: prioritizăm potrivirea de 100%, apoi numărul de condiții
        # Astfel, regulile cele mai specifice și corecte trec primele
        lista_sortata = sorted(
            recomandari_potentiale, 
            key=lambda x: (x["procent_logic"], x["complexitate"]), 
            reverse=True
        )
        
        # Eliminăm duplicatele
        vazute = set()
        final = []
        for r in lista_sortata:
            if r["sport"] not in vazute:
                final.append(r)
                vazute.add(r["sport"])

        # 4. Garanție Top 3: Dacă avem mai puțin de 3, completăm cu Default
        while len(final) < 3:
            if not any(r["sport"] == self.default["atunci"] for r in final):
                final.append({
                    "sport": self.default["atunci"],
                    "justificare": self.default["justificare"],
                    "score": 1.0,
                    "complexitate": 0
                })
            else:
                # Dacă și default-ul e deja acolo, punem o variantă generică de siguranță
                final.append({
                    "sport": "Activitate Fizică Generală",
                    "justificare": "Menținerea unui stil de viață activ prin mișcare zilnică.",
                    "score": 1.0,
                    "complexitate": 0
                })

        return final[:3], explicatie

    def _rezolva_conflict(self, recomandari, sport, scor, conditii, regula):
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
                f"Cea mai buna potrivire identificată este **{top['sport']}** deoarece: "
                f"{top['justificare']}"
            )

        

        if len(recomandari) > 1:
            alternative = ", ".join(
                f"{r['sport']}" 
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