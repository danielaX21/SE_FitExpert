import tkinter as tk
from tkinter import font
import json
import math


# ─────────────────────────────────────────────
#  PALETA & CONSTANTE
# ─────────────────────────────────────────────
BG           = "#050508"
CARD_BG      = "#0E0E18"
CARD_BORDER  = "#1C1C30"
ACCENT       = "#C8F545"   # lime acid
ACCENT2      = "#7B61FF"   # violet electric
ACCENT3      = "#FF4D6A"   # coral
TEXT_HI      = "#F5F5FF"
TEXT_LO      = "#6B6B8A"
SEL_BG       = "#1A2200"
SEL_BORDER   = "#C8F545"

FONT_TITLE   = ("Courier New", 26, "bold")
FONT_MONO    = ("Courier New", 10)
FONT_Q       = ("Georgia", 17, "bold")
FONT_SUB     = ("Georgia", 11, "italic")
FONT_OPT     = ("Helvetica", 12)
FONT_TINY    = ("Courier New", 8)
FONT_NUM     = ("Courier New", 38, "bold")


# ─────────────────────────────────────────────
#  HELPER – Canvas Progress Bar
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
        w = self.winfo_width() or 600
        ratio = step / max(self.total, 1)
        # track
        self.create_rectangle(0, 0, w, 3, fill=CARD_BG, outline="")
        # fill
        if ratio > 0:
            self.create_rectangle(0, 0, int(w * ratio), 3,
                                  fill=ACCENT, outline="")


# ─────────────────────────────────────────────
#  HELPER – Opțiune radio custom
# ─────────────────────────────────────────────
class OptionRow(tk.Frame):
    def __init__(self, parent, text, var, value, callback):
        super().__init__(parent, bg=CARD_BG,
                         highlightthickness=1,
                         highlightbackground=CARD_BORDER,
                         cursor="hand2")
        self.var      = var
        self.value    = value
        self.callback = callback
        self._selected = False

        # index label (A, B, C…)
        idx = chr(65 + list(parent.winfo_children()).index(self) - 0)
        self.lbl_idx = tk.Label(self, text=idx, fg=TEXT_LO,
                                bg=CARD_BG, font=FONT_TINY,
                                width=3, anchor="center")
        self.lbl_idx.pack(side="left", padx=(14, 4), pady=14)

        self.lbl = tk.Label(self, text=text, fg=TEXT_HI,
                            bg=CARD_BG, font=FONT_OPT,
                            anchor="w", justify="left",
                            wraplength=460)
        self.lbl.pack(side="left", fill="x", expand=True,
                      padx=(0, 20), pady=14)

        # dot indicator
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
        self.config(bg=SEL_BG, highlightbackground=SEL_BORDER,
                    highlightthickness=1)
        self.lbl.config(bg=SEL_BG, fg=TEXT_HI)
        self.lbl_idx.config(bg=SEL_BG, fg=ACCENT)
        self.dot.config(bg=SEL_BG)
        self._draw_dot(True)

    def deselect(self):
        self._selected = False
        self.config(bg=CARD_BG, highlightbackground=CARD_BORDER,
                    highlightthickness=1)
        self.lbl.config(bg=CARD_BG, fg=TEXT_HI)
        self.lbl_idx.config(bg=CARD_BG, fg=TEXT_LO)
        self.dot.config(bg=CARD_BG)
        self._draw_dot(False)


# ─────────────────────────────────────────────
#  APLICAȚIA PRINCIPALĂ
# ─────────────────────────────────────────────
class FitExpertPro:

    def __init__(self, root):
        self.root = root
        self.root.title("FitExpert Pro")
        self.root.geometry("680x820")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        try:
            with open("baza_cunostinte.json", "r", encoding="utf-8") as f:
                self.date = json.load(f)
        except Exception as e:
            self._error(f"Eroare la încărcarea bazei de cunoștințe:\n{e}")
            return

        self.index       = 0
        self.fapte       = {}
        self.opt_rows    = []

        self._build_ui()
        self._render_question()

    # ── UI shell ─────────────────────────────
    def _build_ui(self):
        total = len(self.date["intrebari"])

        # ── header ──
        hdr = tk.Frame(self.root, bg=BG)
        hdr.pack(fill="x", padx=40, pady=(30, 0))

        tk.Label(hdr, text="FIT", fg=ACCENT,
                 bg=BG, font=FONT_TITLE).pack(side="left")
        tk.Label(hdr, text="EXPERT", fg=TEXT_HI,
                 bg=BG, font=FONT_TITLE).pack(side="left")
        tk.Label(hdr, text=" PRO", fg=ACCENT2,
                 bg=BG, font=FONT_TITLE).pack(side="left")

        # step counter (right-aligned)
        self.lbl_step = tk.Label(hdr, text="01 / 08",
                                 fg=TEXT_LO, bg=BG, font=FONT_MONO)
        self.lbl_step.pack(side="right")

        # progress bar
        self.prog = ProgressBar(self.root, total, bg=BG)
        self.prog.pack(fill="x", padx=0, pady=(10, 0))
        self.root.after(100, lambda: self.prog.set(0))

        # decorative separator
        tk.Frame(self.root, bg=CARD_BORDER, height=1).pack(fill="x")

        # ── content area ──
        self.content = tk.Frame(self.root, bg=BG)
        self.content.pack(fill="both", expand=True, padx=40, pady=20)

        # ── footer button ──
        foot = tk.Frame(self.root, bg=BG)
        foot.pack(fill="x", padx=40, pady=(0, 30))

        self.err_lbl = tk.Label(foot, text="", fg=ACCENT3,
                                bg=BG, font=FONT_MONO)
        self.err_lbl.pack(side="left")

        self.btn = tk.Button(
            foot, text="CONTINUĂ  →",
            command=self._handle_next,
            bg=ACCENT, fg=BG,
            font=("Courier New", 11, "bold"),
            relief="flat", padx=32, pady=14,
            cursor="hand2", activebackground="#aed43a",
            activeforeground=BG
        )
        self.btn.pack(side="right")

    # ── render question ───────────────────────
    def _render_question(self):
        for w in self.content.winfo_children():
            w.destroy()
        self.opt_rows = []
        self.err_lbl.config(text="")

        q     = self.date["intrebari"][self.index]
        total = len(self.date["intrebari"])

        # step label
        self.lbl_step.config(
            text=f"{self.index+1:02d} / {total:02d}")
        self.prog.set(self.index)
        self.root.after(50, lambda: self.prog.set(self.index + 1))

        # big number
        num_f = tk.Frame(self.content, bg=BG)
        num_f.pack(fill="x", pady=(10, 0))
        tk.Label(num_f, text=f"{self.index+1:02d}",
                 fg=CARD_BORDER, bg=BG, font=FONT_NUM).pack(side="left")

        # question text
        tk.Label(self.content, text=q["text"],
                 fg=TEXT_HI, bg=BG, font=FONT_Q,
                 wraplength=580, justify="left",
                 anchor="w").pack(fill="x", pady=(4, 20))

        # options
        self.selection = tk.StringVar(value="__none__")

        for opt in q["optiuni"]:
            row = OptionRow(self.content, opt,
                            self.selection, opt,
                            self._on_select)
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

    # ── navigation ───────────────────────────
    def _handle_next(self):
        if self.selection.get() == "__none__":
            self.err_lbl.config(text="⚠  Selectează o opțiune pentru a continua.")
            return

        qid = self.date["intrebari"][self.index]["id"]
        self.fapte[qid] = self.selection.get()
        self.index += 1

        if self.index < len(self.date["intrebari"]):
            self._render_question()
        else:
            self._show_results()

    # ── inference engine ──────────────────────
    def _run_inference(self):
        facts   = dict(self.fapte)
        rules   = self.date["reguli"]
        explain = []
        recs    = {}

        changed = True
        while changed:
            changed = False
            for rule in rules:
                cond = rule["daca"]
                if not all(facts.get(k) == v for k, v in cond.items()):
                    continue

                if "atunci_fapt" in rule:
                    for k, v in rule["atunci_fapt"].items():
                        if facts.get(k) != v:
                            facts[k] = v
                            explain.append(f"dedus: {k} = {v}")
                            changed = True

                if "atunci" in rule:
                    sport = rule["atunci"]
                    score = rule.get("confidence", 0.7)
                    if sport not in recs or recs[sport]["score"] < score:
                        recs[sport] = {
                            "sport":       sport,
                            "justificare": rule["justificare"],
                            "score":       score,
                            "matched":     list(cond.keys())
                        }
                    explain.append(f"regulă activă → {sport} ({int(score*100)}%)")

        result_list = sorted(recs.values(),
                             key=lambda x: x["score"], reverse=True)

        if not result_list:
            d = self.date["default"]
            result_list = [{
                "sport":       d["atunci"],
                "justificare": d["justificare"],
                "score":       d.get("confidence", 0.55),
                "matched":     []
            }]

        return result_list[:3], explain

    # ── results screen ────────────────────────
    def _show_results(self):
        for w in self.content.winfo_children():
            w.destroy()
        self.btn.config(text="RESTART  ↺", command=self._restart)

        results, explain = self._run_inference()

        # ── scroll canvas ──
        canvas = tk.Canvas(self.content, bg=BG,
                           highlightthickness=0)
        sb = tk.Scrollbar(self.content, orient="vertical",
                          command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=inner,
                                      anchor="nw", width=580)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(
                       scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win_id, width=e.width))
        inner.bind("<MouseWheel>",
                   lambda e: canvas.yview_scroll(
                       -1 if e.delta > 0 else 1, "units"))

        # headline
        tk.Label(inner, text="REZULTATELE TALE",
                 fg=ACCENT, bg=BG,
                 font=("Courier New", 12, "bold")).pack(
                     anchor="w", pady=(10, 4))
        tk.Label(inner,
                 text="Sistemul expert a analizat profilul tău și îți recomandă:",
                 fg=TEXT_LO, bg=BG, font=FONT_SUB).pack(
                     anchor="w", pady=(0, 18))

        MEDAL = ["🥇", "🥈", "🥉"]

        for i, r in enumerate(results):
            pct = int(r["score"] * 100)
            card = tk.Frame(inner, bg=CARD_BG,
                            highlightthickness=1,
                            highlightbackground=(
                                ACCENT if i == 0 else CARD_BORDER))
            card.pack(fill="x", pady=8, ipady=0)

            # top strip (medal + sport name + score)
            top = tk.Frame(card, bg=CARD_BG)
            top.pack(fill="x", padx=18, pady=(16, 4))

            tk.Label(top, text=MEDAL[i], bg=CARD_BG,
                     font=("Segoe UI Emoji", 20)).pack(side="left")

            tk.Label(top, text=r["sport"],
                     fg=ACCENT if i == 0 else TEXT_HI,
                     bg=CARD_BG,
                     font=("Georgia", 15, "bold")).pack(
                         side="left", padx=12)

            tk.Label(top, text=f"{pct}%",
                     fg=ACCENT if i == 0 else ACCENT2,
                     bg=CARD_BG,
                     font=("Courier New", 13, "bold")).pack(side="right")

            # mini progress
            pbar = tk.Canvas(card, height=3, bg=CARD_BG,
                             highlightthickness=0)
            pbar.pack(fill="x", padx=18, pady=(2, 8))
            pbar.update_idletasks()
            w = pbar.winfo_width() or 540
            pbar.create_rectangle(0, 0, w, 3, fill=CARD_BORDER, outline="")
            fill_color = ACCENT if i == 0 else ACCENT2
            pbar.create_rectangle(0, 0, int(w * r["score"]), 3,
                                  fill=fill_color, outline="")

            # justification
            tk.Label(card, text=r["justificare"],
                     fg=TEXT_LO, bg=CARD_BG,
                     font=FONT_SUB, wraplength=510,
                     justify="left").pack(
                         anchor="w", padx=18, pady=(0, 16))

        # ── explain trace ──
        tk.Frame(inner, bg=CARD_BORDER, height=1).pack(
            fill="x", pady=(24, 12))
        tk.Label(inner, text="TRASEU DE INFERENȚĂ",
                 fg=TEXT_LO, bg=BG,
                 font=("Courier New", 9, "bold")).pack(anchor="w")

        trace_f = tk.Frame(inner, bg=CARD_BG,
                           highlightthickness=1,
                           highlightbackground=CARD_BORDER)
        trace_f.pack(fill="x", pady=(6, 20))

        for step in explain:
            tk.Label(trace_f, text="›  " + step,
                     fg=TEXT_LO, bg=CARD_BG,
                     font=FONT_TINY, anchor="w",
                     justify="left").pack(
                         fill="x", padx=14, pady=1)

        if not explain:
            tk.Label(trace_f, text="›  Nicio regulă intermediară activată.",
                     fg=TEXT_LO, bg=CARD_BG,
                     font=FONT_TINY).pack(padx=14, pady=4)

    # ── restart ───────────────────────────────
    def _restart(self):
        for w in self.root.winfo_children():
            w.destroy()
        FitExpertPro(self.root)

    # ── error popup ───────────────────────────
    def _error(self, msg):
        win = tk.Toplevel(self.root)
        win.title("Eroare")
        win.configure(bg=BG)
        tk.Label(win, text=msg, fg=ACCENT3, bg=BG,
                 font=FONT_OPT, padx=30, pady=30).pack()
        tk.Button(win, text="Închide", command=win.destroy,
                  bg=ACCENT3, fg=BG).pack(pady=10)


# ─────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = FitExpertPro(root)
    root.mainloop()