import tkinter as tk
from tkinter import messagebox, font
import time

class FitExpertPro:
    def __init__(self, root):
        self.root = root
        self.root.title("FitExpert Pro v2.0")
        self.root.geometry("650x800")
        self.root.configure(bg="#0B0B15") # Darker, more premium navy

        # Paleta de culori
        self.color_accent = "#BB86FC"
        self.color_bg_card = "#161625"
        self.color_text = "#FFFFFF"
        self.color_text_dim = "#A0A0B0"

        # Fonturi
        self.font_h1 = font.Font(family="Verdana", size=26, weight="bold")
        self.font_q = font.Font(family="Verdana", size=14, weight="bold")
        self.font_ui = font.Font(family="Verdana", size=11)

        with open('baza_cunostinte.json', 'r', encoding='utf-8') as f:
            self.date = json.load(f)

        self.index = 0
        self.fapte = {}
        self.render_main_layout()

    def render_main_layout(self):
        # Progress bar neon
        self.canvas_p = tk.Canvas(self.root, height=5, bg="#0B0B15", highlightthickness=0)
        self.canvas_p.pack(fill="x")
        self.p_bar = self.canvas_p.create_rectangle(0, 0, 0, 5, fill=self.color_accent, outline="")

        # Title
        tk.Label(self.root, text="FITEXPERT PRO", bg="#0B0B15", fg=self.color_accent, 
                 font=self.font_h1, pady=40).pack()

        # Main Card
        self.main_card = tk.Frame(self.root, bg=self.color_bg_card, padx=45, pady=45,
                                  highlightbackground="#2D2D45", highlightthickness=2)
        self.main_card.pack(expand=True, fill="both", padx=60, pady=(0, 40))

        self.content_area = tk.Frame(self.main_card, bg=self.color_bg_card)
        self.content_area.pack(expand=True, fill="both")

        # Bottom Button
        self.btn_next = tk.Button(self.root, text="CONTINUĂ  →", command=self.handle_next,
                                  bg=self.color_accent, fg="#0B0B15", font=("Verdana", 11, "bold"),
                                  relief="flat", padx=60, pady=18, cursor="hand2")
        self.btn_next.pack(side="bottom", pady=50)
        
        # Hover Effect
        self.btn_next.bind("<Enter>", lambda e: self.btn_next.config(bg="#D7B7FD"))
        self.btn_next.bind("<Leave>", lambda e: self.btn_next.config(bg=self.color_accent))

        self.refresh_question()

    def refresh_question(self):
        # Update progress
        total = len(self.date["intrebari"])
        self.canvas_p.coords(self.p_bar, 0, 0, (self.index/total)*650, 5)

        for w in self.content_area.winfo_children(): w.destroy()
        
        q = self.date["intrebari"][self.index]
        tk.Label(self.content_area, text=f"INTREBAREA {self.index + 1}", bg=self.color_bg_card, 
                 fg=self.color_accent, font=("Verdana", 9, "bold")).pack(pady=(0, 10))
        
        tk.Label(self.content_area, text=q["text"], bg=self.color_bg_card, fg=self.color_text, 
                 font=self.font_q, wraplength=400).pack(pady=(0, 40))

        self.selection = tk.StringVar(value="")
        for opt in q["optiuni"]:
            f = tk.Frame(self.content_area, bg=self.color_bg_card)
            f.pack(fill="x", pady=5)
            # Custom Radio style
            rb = tk.Radiobutton(f, text=opt, variable=self.selection, value=opt,
                                bg=self.color_bg_card, fg=self.color_text_dim, 
                                selectcolor="#2D2D45", font=self.font_ui,
                                activebackground=self.color_bg_card, 
                                activeforeground=self.color_accent, cursor="hand2")
            rb.pack(side="left", padx=20)

    def handle_next(self):
        if not self.selection.get():
            messagebox.showwarning("FitExpert", "Te rugăm să alegi o opțiune pentru analiză! 🔍")
            return

        qid = self.date["intrebari"][self.index]["id"]
        self.fapte[qid] = self.selection.get()
        
        self.index += 1
        if self.index < len(self.date["intrebari"]):
            self.refresh_question()
        else:
            self.show_thinking_state()

    def show_thinking_state(self):
        for w in self.content_area.winfo_children(): w.destroy()
        self.btn_next.pack_forget()
        
        self.canvas_p.coords(self.p_bar, 0, 0, 650, 5)
        
        tk.Label(self.content_area, text="⚙️", font=("Verdana", 40), bg=self.color_bg_card).pack(pady=20)
        tk.Label(self.content_area, text="MAȘINA DE INFERENȚĂ ANALIZEAZĂ...", 
                 bg=self.color_bg_card, fg=self.color_accent, font=("Verdana", 10, "bold")).pack()
        
        self.root.after(1500, self.display_final_result)

    def display_final_result(self):
        for w in self.content_area.winfo_children(): w.destroy()
        
        # Logica Forward Chaining din Baza de Cunostinte [cite: 45, 131]
        res = self.date["default"]
        for r in self.date["reguli"]:
            if all(self.fapte.get(k) == v for k, v in r["daca"].items()):
                res = r
                break
        
        tk.Label(self.content_area, text="RECOMANDARE PERSONALIZATĂ", bg=self.color_bg_card, 
                 fg=self.color_accent, font=("Verdana", 9, "bold")).pack(pady=(0, 20))
        
        tk.Label(self.content_area, text=res["atunci"].upper(), bg=self.color_bg_card, 
                 fg=self.color_text, font=self.font_h1, wraplength=450).pack()

        # Justificarea Sistemului Expert 
        tk.Frame(self.content_area, height=2, width=80, bg="#3D3D55").pack(pady=25)
        
        tk.Label(self.content_area, text=res["justificare"], bg=self.color_bg_card, 
                 fg=self.color_text_dim, font=self.font_ui, wraplength=400, justify="center").pack()

        tk.Button(self.root, text="REÎNCEPE TESTUL", command=self.restart,
                  bg="#1E1E2F", fg="white", relief="flat", padx=20, pady=10).pack(side="bottom", pady=40)

    def restart(self):
        for w in self.root.winfo_children(): w.destroy()
        self.__init__(self.root)

if __name__ == "__main__":
    import json
    root = tk.Tk()
    app = FitExpertPro(root)
    root.mainloop()