import tkinter as tk
from inferenta import MotorInferenta, incarca_baza

# ─────────────────────────────────────────────
#  PALETA & CONSTANTE VIZUALE
# ─────────────────────────────────────────────
BG          = "#050508"
CARD_BG     = "#0E0E18"
CARD_BORDER = "#1C1C30"
ACCENT      = "#C8F545"
ACCENT2     = "#7B61FF"
ACCENT3     = "#FF4D6A"
TEXT_HI     = "#F5F5FF"
TEXT_LO     = "#6B6B8A"
SEL_BG      = "#1A2200"
SEL_BORDER  = "#C8F545"

FONT_TITLE  = ("Courier New", 26, "bold")
FONT_MONO   = ("Courier New", 10)
FONT_Q      = ("Georgia", 17, "bold")
FONT_SUB    = ("Georgia", 11, "italic")
FONT_OPT    = ("Helvetica", 12)
FONT_TINY   = ("Courier New", 8)
FONT_NUM    = ("Courier New", 38, "bold")


# ─────────────────────────────────────────────
#  WIDGET – Bara de progres animata
# ─────────────────────────────────────────────
class ProgressBar(tk.Canvas):
    def __init__(self, parent, total, **kw):
        kw.setdefault("bg", BG)
        super().__init__(parent, height=3,
                         highlightthickness=0, **kw)
        self.total = total
        self._step = 0

    def set(self, step):
        self._step = step
        self.delete("all")
        w     = self.winfo_width() or 600
        ratio = step / max(self.total, 1)
        self.create_rectangle(0, 0, w, 3, fill=CARD_BG, outline="")
        if ratio > 0:
            self.create_rectangle(0, 0, int(w * ratio), 3,
                                  fill=ACCENT, outline="")


# ─────────────────────────────────────────────
#  WIDGET – Rand optiune radio custom
# ─────────────────────────────────────────────
class OptionRow(tk.Frame):
    def __init__(self, parent, text, var, value, callback, index=0):
        super().__init__(parent, bg=CARD_BG,
                         highlightthickness=1,
                         highlightbackground=CARD_BORDER,
                         cursor="hand2")
        self.var       = var
        self.value     = value
        self.callback  = callback
        self._selected = False

        idx_label = chr(65 + index)  # A, B, C, D...
        self.lbl_idx = tk.Label(self, text=idx_label, fg=TEXT_LO,
                                bg=CARD_BG, font=FONT_TINY,
                                width=3, anchor="center")
        self.lbl_idx.pack(side="left", padx=(14, 4), pady=14)

        self.lbl = tk.Label(self, text=text, fg=TEXT_HI,
                            bg=CARD_BG, font=FONT_OPT,
                            anchor="w", justify="left",
                            wraplength=460)
        self.lbl.pack(side="left", fill="x", expand=True,
                      padx=(0, 20), pady=14)

        self.dot = tk.Canvas(self, width=16, height=16,
                             bg=CARD_BG, highlightthickness=0)
        self.dot.pack(side="right", padx=18)
        self._draw_dot(False)

        for w in (self, self.lbl, self.lbl_idx, self.dot):
            w.bind("<Button-1>", self._click)
        self.bind("<Enter>", self._hover)
        self.bind("<Leave>", self._unhover)

    def _click(self, _=None):
        self.var.set(self.value)
        self.callback()

    def _hover(self, _=None):
        if not self._selected:
            self.config(highlightbackground=ACCENT2)

    def _unhover(self, _=None):
        if not self._selected:
            self.config(highlightbackground=CARD_BORDER)

    def _draw_dot(self, selected):
        self.dot.delete("all")
        if selected:
            self.dot.config(bg=SEL_BG)
            self.dot.create_oval(2, 2, 14, 14,
                                 outline=ACCENT, width=2, fill="")
            self.dot.create_oval(5, 5, 11, 11,
                                 fill=ACCENT, outline="")
        else:
            self.dot.config(bg=CARD_BG)
            self.dot.create_oval(2, 2, 14, 14,
                                 outline=TEXT_LO, width=1, fill="")

    def select(self):
        self._selected = True
        self.config(bg=SEL_BG, highlightbackground=SEL_BORDER)
        self.lbl.config(bg=SEL_BG, fg=TEXT_HI)
        self.lbl_idx.config(bg=SEL_BG, fg=ACCENT)
        self.dot.config(bg=SEL_BG)
        self._draw_dot(True)

    def deselect(self):
        self._selected = False
        self.config(bg=CARD_BG, highlightbackground=CARD_BORDER)
        self.lbl.config(bg=CARD_BG, fg=TEXT_HI)
        self.lbl_idx.config(bg=CARD_BG, fg=TEXT_LO)
        self.dot.config(bg=CARD_BG)
        self._draw_dot(False)


# ─────────────────────────────────────────────
#  APLICATIA PRINCIPALA
# ─────────────────────────────────────────────
class FitExpertUI:
    def __init__(self, root):
        self.root  = root
        self.root.title("FitExpert Pro")
        self.root.geometry("720x860")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)
        self.root.minsize(620, 600)

        try:
            baza = incarca_baza("baza_cunostinte.json")
        except Exception as e:
            self._eroare(f"Eroare la incarcarea bazei de cunostinte:\n{e}")
            return

        self.date     = baza
        self.motor    = MotorInferenta(baza)
        self.index    = 0
        self.fapte    = {}
        self.opt_rows = []

        self._build_ui()
        self._render_question()

    # ── Construieste shell-ul UI ──────────────
    def _build_ui(self):
        """Construieste structura de baza a ferestrei: header, bara progres, content, footer."""
        total = len(self.date["intrebari"])

        hdr = tk.Frame(self.root, bg=BG)
        hdr.pack(fill="x", padx=40, pady=(30, 0))

        tk.Label(hdr, text="FIT",    fg=ACCENT,  bg=BG, font=FONT_TITLE).pack(side="left")
        tk.Label(hdr, text="EXPERT", fg=TEXT_HI, bg=BG, font=FONT_TITLE).pack(side="left")
        tk.Label(hdr, text=" PRO",   fg=ACCENT2, bg=BG, font=FONT_TITLE).pack(side="left")

        self.lbl_step = tk.Label(hdr, text="01 / 08",
                                 fg=TEXT_LO, bg=BG, font=FONT_MONO)
        self.lbl_step.pack(side="right")

        self.prog = ProgressBar(self.root, total)
        self.prog.pack(fill="x", pady=(10, 0))
        self.root.after(100, lambda: self.prog.set(0))

        tk.Frame(self.root, bg=CARD_BORDER, height=1).pack(fill="x")

        self.content = tk.Frame(self.root, bg=BG)
        self.content.pack(fill="both", expand=True, padx=40, pady=20)

        foot = tk.Frame(self.root, bg=BG)
        foot.pack(fill="x", padx=40, pady=(0, 30))

        self.err_lbl = tk.Label(foot, text="", fg=ACCENT3,
                                bg=BG, font=FONT_MONO)
        self.err_lbl.pack(side="left")

        self.btn = tk.Button(
            foot, text="CONTINUA  ->",
            command=self._handle_next,
            bg=ACCENT, fg=BG,
            font=("Courier New", 11, "bold"),
            relief="flat", padx=32, pady=14,
            cursor="hand2",
            activebackground="#aed43a", activeforeground=BG
        )
        self.btn.pack(side="right")

    # ── Afiseaza intrebarea curenta ───────────
    def _render_question(self):
        for w in self.content.winfo_children():
            w.destroy()
        self.opt_rows = []
        self.err_lbl.config(text="")

        q     = self.date["intrebari"][self.index]
        total = len(self.date["intrebari"])

        self.lbl_step.config(text=f"{self.index+1:02d} / {total:02d}")
        self.prog.set(self.index)
        self.root.after(50, lambda: self.prog.set(self.index + 1))

        tk.Label(self.content, text=f"{self.index+1:02d}",
                 fg=CARD_BORDER, bg=BG, font=FONT_NUM).pack(anchor="w")

        tk.Label(self.content, text=q["text"],
                 fg=TEXT_HI, bg=BG, font=FONT_Q,
                 wraplength=560, justify="left", anchor="w").pack(
                     fill="x", pady=(4, 20))

        self.selection = tk.StringVar(value="__none__")

        for i, opt in enumerate(q["optiuni"]):
            row = OptionRow(self.content, opt,
                            self.selection, opt,
                            self._on_select, index=i)
            row.pack(fill="x", pady=4)
            self.opt_rows.append((row, opt))

    def _on_select(self):
        self.err_lbl.config(text="")
        val = self.selection.get()
        for row, opt in self.opt_rows:
            if opt == val:
                row.select()
            else:
                row.deselect()

    # ── Navigare ─────────────────────────────
    def _handle_next(self):
        if self.selection.get() == "__none__":
            self.err_lbl.config(
                text="  Selecteaza o optiune pentru a continua.")
            return

        qid = self.date["intrebari"][self.index]["id"]
        self.fapte[qid] = self.selection.get()
        self.index += 1

        if self.index < len(self.date["intrebari"]):
            self._render_question()
        else:
            self._show_results()

    # ── Ecranul de rezultate ──────────────────
    def _show_results(self):
        for w in self.content.winfo_children():
            w.destroy()
        self.btn.config(text="RESTART  <-", command=self._restart)


        rezultate, traseu_tehnic = self.motor.ruleaza(self.fapte)
        explicatii_human = self.motor.genereaza_explicatii_human(
            self.fapte, rezultate
        )


        canvas = tk.Canvas(self.content, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(self.content, orient="vertical",
                          command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=inner,
                                      anchor="nw")

        
        def _on_inner_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        
        def _on_canvas_configure(e):
            canvas.itemconfig(win_id, width=e.width)
            for widget in inner.winfo_children():
                _update_wraplength(widget, e.width - 60)

        def _update_wraplength(widget, new_width):
            if isinstance(widget, tk.Label):
                try:
                    widget.config(wraplength=max(200, new_width))
                except Exception:
                    pass
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    _update_wraplength(child, new_width - 20)

        inner.bind("<Configure>", _on_inner_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        
        def _scroll(e):
            canvas.yview_scroll(-1 if e.delta > 0 else 1, "units")

        
        self.root.bind_all("<MouseWheel>", _scroll)
        self.root.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        self.root.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        # ── Sectiunea 1: Explicatii human-readable ──
        tk.Label(inner, text="DE CE ACESTE RECOMANDARI?",
                 fg=ACCENT, bg=BG,
                 font=("Courier New", 10, "bold")).pack(
                     anchor="w", pady=(10, 6))

        expl_frame = tk.Frame(inner, bg=CARD_BG,
                              highlightthickness=1,
                              highlightbackground=CARD_BORDER)
        expl_frame.pack(fill="x", pady=(0, 16))

        for linie in explicatii_human:
            tk.Label(expl_frame, text=linie,
                     fg=TEXT_HI, bg=CARD_BG,
                     font=FONT_SUB, wraplength=500,
                     justify="left").pack(
                         anchor="w", padx=16, pady=5)

        # ── Sectiunea 2: Top 3 recomandari ──
        tk.Label(inner, text="RECOMANDARI PERSONALIZATE",
                 fg=ACCENT, bg=BG,
                 font=("Courier New", 10, "bold")).pack(
                     anchor="w", pady=(4, 6))

        MEDAL = ["   ", "   ", "   "]

        for i, r in enumerate(rezultate):
            pct  = int(r["score"] * 100)
            card = tk.Frame(inner, bg=CARD_BG,
                            highlightthickness=1,
                            highlightbackground=(
                                ACCENT if i == 0 else CARD_BORDER))
            card.pack(fill="x", pady=6)

            top = tk.Frame(card, bg=CARD_BG)
            top.pack(fill="x", padx=18, pady=(14, 4))

            medal_texts = ["#1", "#2", "#3"]
            tk.Label(top, text=medal_texts[i], bg=CARD_BG,
                     fg=ACCENT if i == 0 else ACCENT2,
                     font=("Courier New", 12, "bold")).pack(side="left")
            
            tk.Label(top, text="  " + r["sport"],
                     fg=ACCENT if i == 0 else TEXT_HI,
                     bg=CARD_BG,
                     font=("Georgia", 14, "bold")).pack(
                         side="left", padx=8)

            tk.Label(card, text=r["justificare"],
                     fg=TEXT_LO, bg=CARD_BG,
                     font=FONT_SUB, wraplength=480,
                     justify="left").pack(
                         anchor="w", padx=18, pady=(0, 14))

        # ── Sectiunea 3: Traseu tehnic Forward Chaining ──
        tk.Frame(inner, bg=CARD_BORDER, height=1).pack(
            fill="x", pady=(20, 10))
        tk.Label(inner, text="TRASEU TEHNIC DE INFERENTA (Forward Chaining)",
                 fg=TEXT_LO, bg=BG,
                 font=("Courier New", 9, "bold")).pack(anchor="w")

        trace_f = tk.Frame(inner, bg=CARD_BG,
                           highlightthickness=1,
                           highlightbackground=CARD_BORDER)
        trace_f.pack(fill="x", pady=(6, 20))

        pasi = traseu_tehnic if traseu_tehnic else [
            "Nicio regula intermediara activata -> recomandare directa."]
        for step in pasi:
            culoare = (ACCENT    if "[FAPT NOU]"        in step else
                       ACCENT2   if "[REGULA ACTIVA]"   in step else
                       ACCENT3   if "[CONFLICT"         in step else
                       TEXT_LO)
            tk.Label(trace_f, text="  " + step,
                     fg=culoare, bg=CARD_BG,
                     font=FONT_TINY, anchor="w",
                     wraplength=560,
                     justify="left").pack(
                         fill="x", padx=14, pady=2)

    # ── Restart ───────────────────────────────
    def _restart(self):
        """Reseteaza complet aplicatia la starea initiala."""
        # Curatam binding-urile de scroll inainte de restart
        try:
            self.root.unbind_all("<MouseWheel>")
            self.root.unbind_all("<Button-4>")
            self.root.unbind_all("<Button-5>")
        except Exception:
            pass
        for w in self.root.winfo_children():
            w.destroy()
        FitExpertUI(self.root)

    # ── Eroare ───────────────────────────────
    def _eroare(self, msg):
        """Afiseaza o fereastra de eroare cu mesajul dat."""
        win = tk.Toplevel(self.root)
        win.title("Eroare")
        win.configure(bg=BG)
        tk.Label(win, text=msg, fg=ACCENT3, bg=BG,
                 font=FONT_OPT, padx=30, pady=30).pack()
        tk.Button(win, text="Inchide", command=win.destroy,
                  bg=ACCENT3, fg=BG).pack(pady=10)


# ─────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = FitExpertUI(root)
    root.mainloop()