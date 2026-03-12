import tkinter as tk
from tkinter import messagebox, font
import json

class FitExpertUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FitExpert – Premium Advisor")
        self.root.geometry("600x750")
        self.root.configure(bg="#0F0C29") # Fundal Deep Navy/Space

        # Culori Paletă Mov Premium
        self.color_primary = "#BB86FC"  # Mov Electric
        self.color_bg_card = "#1A1A2E"  # Card Navy închis
        self.color_text = "#E0E0E0"
        self.color_accent = "#03DAC6"   # Teal pentru accente (opțional)

        # Incarcare Date
        with open('baza_cunostinte.json', 'r', encoding='utf-8') as f:
            self.date = json.load(f)

        self.index = 0
        self.raspunsuri = {}
        
        self.setup_styles()
        self.build_ui()
        self.show_question()

    def setup_styles(self):
        self.f_title = font.Font(family="Montserrat", size=24, weight="bold")
        self.f_text = font.Font(family="Inter", size=12)
        self.f_btn = font.Font(family="Inter", size=11, weight="bold")

    def build_ui(self):
        # Bara de progres "Neon"
        self.p_canvas = tk.Canvas(self.root, height=4, bg="#0F0C29", highlightthickness=0)
        self.p_canvas.pack(fill="x")
        self.p_bar = self.p_canvas.create_rectangle(0, 0, 0, 4, fill=self.color_primary, outline="")

        # Header cu Glow
        self.header = tk.Label(self.root, text="FITEXPERT", bg="#0F0C29", 
                               fg=self.color_primary, font=self.f_title, pady=40)
        self.header.pack()

        # Cardul Central - "Glass Effect"
        self.card = tk.Frame(self.root, bg=self.color_bg_card, padx=40, pady=40,
                             highlightbackground="#2A2A4A", highlightthickness=2)
        self.card.pack(expand=True, fill="both", padx=50, pady=(0, 40))

        self.q_label = tk.Label(self.card, text="", bg=self.color_bg_card, 
                                fg="white", font=("Inter", 14, "bold"), 
                                wraplength=400, justify="center")
        self.q_label.pack(pady=(0, 30))

        self.opts_frame = tk.Frame(self.card, bg=self.color_bg_card)
        self.opts_frame.pack(fill="x")

        # Buton "Next" cu stil modern
        self.btn_next = tk.Button(self.root, text="CONTINUĂ  →", command=self.next_step,
                                  bg=self.color_primary, fg="#0F0C29", font=self.f_btn,
                                  relief="flat", padx=60, pady=18, cursor="hand2",
                                  activebackground="#D7B7FD")
        self.btn_next.pack(side="bottom", pady=50)

    def update_progress(self):
        w = (self.index / len(self.date["intrebari"])) * 600
        self.p_canvas.coords(self.p_bar, 0, 0, w, 4)

    def show_question(self):
        self.update_progress()
        for w in self.opts_frame.winfo_children(): w.destroy()

        q = self.date["intrebari"][self.index]
        self.q_label.config(text=q["text"])
        
        self.v = tk.StringVar(value="")
        for opt in q["optiuni"]:
            # Stilizare Radio - eliminam cercul standard unde se poate sau il coloram
            rb = tk.Radiobutton(self.opts_frame, text=opt, variable=self.v, value=opt,
                                bg=self.color_bg_card, fg=self.color_text, 
                                font=self.f_text, selectcolor="#2A2A4A",
                                activebackground=self.color_bg_card, 
                                activeforeground=self.color_primary,
                                pady=12, cursor="hand2", anchor="w")
            rb.pack(fill="x", padx=20)

    def next_step(self):
        if not self.v.get():
            messagebox.showwarning("FitExpert", "Te rugăm să alegi o variantă pentru a debloca recomandarea! ✨")
            return

        q_id = self.date["intrebari"][self.index]["id"]
        self.raspunsuri[q_id] = self.v.get()
        
        self.index += 1
        if self.index < len(self.date["intrebari"]):
            self.show_question()
        else:
            self.show_result()

    def show_result(self):
        self.update_progress()
        for w in self.card.winfo_children(): w.destroy()
        self.btn_next.destroy()

        # Logica Forward Chaining (Motorul tau)
        res = self.date["recomandare_default"]
        for r in self.date["reguli"]:
            if all(self.raspunsuri.get(k) == v for k, v in r["daca"].items()):
                res = r
                break

        # Afisare Rezultat "Fancy"
        tk.Label(self.card, text="PROFIL ANALIZAT COMPLET", bg=self.color_bg_card, 
                 fg=self.color_primary, font=("Inter", 10, "bold")).pack(pady=(0, 20))
        
        tk.Label(self.card, text=res["atunci"], bg=self.color_bg_card, 
                 fg="white", font=("Montserrat", 22, "bold"), wraplength=400).pack()
        
        # Linie de decor
        tk.Frame(self.card, height=2, width=100, bg=self.color_primary).pack(pady=20)

        tk.Label(self.card, text=res["descriere"], bg=self.color_bg_card, 
                 fg="#B0B0C0", font=self.f_text, wraplength=400, justify="center").pack(pady=20)

        tk.Button(self.card, text="REÎNCEPE ANALIZA", command=self.reset,
                  bg="#2A2A4A", fg="white", font=self.f_btn, relief="flat", 
                  padx=20, pady=10, cursor="hand2").pack(side="bottom", pady=20)

    def reset(self):
        self.root.destroy()
        run_app()

def run_app():
    root = tk.Tk()
    FitExpertUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()