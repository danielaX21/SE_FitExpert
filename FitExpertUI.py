import tkinter as tk
from tkinter import messagebox, font
import json

class FitExpertUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FitExpert – Professional Fitness Advisor")
        self.root.geometry("500x600")
        self.root.configure(bg="#121212")  # Fundal Dark Mode modern

        # Configurare Fonturi
        self.titlu_font = font.Font(family="Helvetica", size=20, weight="bold")
        self.text_font = font.Font(family="Helvetica", size=12)
        self.btn_font = font.Font(family="Helvetica", size=11, weight="bold")

        # Culori Tematice (Neutru/Energy)
        self.accent_color = "#BB86FC"  # Mov electric (specific Material Design)
        self.bg_card = "#1E1E1E"       # Gri închis pentru card
        self.text_color = "#E0E0E0"    # Alb-gri pentru lizibilitate

        # Incarcare Baza de Cunostinte
        try:
            with open('baza_cunostinte.json', 'r', encoding='utf-8') as f:
                self.date = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Eroare", "Fișierul JSON lipsește!")
            self.root.destroy()

        self.index_intrebare = 0
        self.total_intrebari = len(self.date["intrebari"])
        self.raspunsuri_utilizator = {}

        self.creeaza_widgeturi()
        self.afiseaza_intrebare()

    def creeaza_widgeturi(self):
        # Bara de Progres (Custom)
        self.canvas_progress = tk.Canvas(self.root, height=10, bg="#333333", highlightthickness=0)
        self.canvas_progress.pack(fill="x", side="top")
        self.progress_bar = self.canvas_progress.create_rectangle(0, 0, 0, 10, fill=self.accent_color)

        # Header
        self.header_label = tk.Label(self.root, text="FIT EXPERT", bg="#121212", 
                                     fg=self.accent_color, font=self.titlu_font, pady=30)
        self.header_label.pack()

        # Cardul Central (unde stau intrebarile)
        self.card = tk.Frame(self.root, bg=self.bg_card, padx=30, pady=30, 
                             highlightbackground="#333333", highlightthickness=1)
        self.card.pack(expand=True, fill="both", padx=40, pady=(0, 40))

        self.label_intrebare = tk.Label(self.card, text="", bg=self.bg_card, 
                                        fg=self.text_color, font=self.text_font, 
                                        wraplength=350, justify="center")
        self.label_intrebare.pack(pady=(0, 25))

        self.options_frame = tk.Frame(self.card, bg=self.bg_card)
        self.options_frame.pack(fill="x")

        # Butonul "Next" stilizat
        self.btn_next = tk.Button(self.root, text="CONTINUĂ", command=self.proceseaza,
                                  bg=self.accent_color, fg="#121212", font=self.btn_font,
                                  relief="flat", padx=40, pady=12, cursor="hand2",
                                  activebackground="#A370DB")
        self.btn_next.pack(side="bottom", pady=40)

    def actualizeaza_progres(self):
        procent = (self.index_intrebare / self.total_intrebari) * 500
        self.canvas_progress.coords(self.progress_bar, 0, 0, procent, 10)

    def afiseaza_intrebare(self):
        self.actualizeaza_progres()
        
        # Curatare optiuni
        for widget in self.options_frame.winfo_children():
            widget.destroy()

        intrebare_data = self.date["intrebari"][self.index_intrebare]
        self.label_intrebare.config(text=intrebare_data["text"].upper())
        
        self.var_selectata = tk.StringVar(value="")

        # RadioButtons stilizate pentru Dark Mode
        for optiune in intrebare_data["optiuni"]:
            rb = tk.Radiobutton(self.options_frame, text=optiune, variable=self.var_selectata, 
                                value=optiune, bg=self.bg_card, fg=self.text_color,
                                font=self.text_font, selectcolor="#333333", 
                                activebackground=self.bg_card, activeforeground=self.accent_color,
                                pady=10, cursor="hand2")
            rb.pack(anchor="w")

    def proceseaza(self):
        raspuns = self.var_selectata.get()
        if not raspuns:
            messagebox.showwarning("Info", "Selectează o opțiune pentru a avansa!")
            return

        id_intrebare = self.date["intrebari"][self.index_intrebare]["id"]
        self.raspunsuri_utilizator[id_intrebare] = raspuns
        
        self.index_intrebare += 1
        
        if self.index_intrebare < self.total_intrebari:
            self.afiseaza_intrebare()
        else:
            self.actualizeaza_progres()
            self.finalizare()

    def finalizare(self):
        # Aici interfața trimite datele către mașina de inferență [cite: 27, 89]
        messagebox.showinfo("FitExpert", "Analiza profilului tau a fost finalizata!")
        print("Date colectate:", self.raspunsuri_utilizator)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FitExpertUI(root)
    root.mainloop()