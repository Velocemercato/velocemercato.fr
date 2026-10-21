"""VM Performance 2.0 — fenêtres Atelier, Stage 1 / E85 et Électrique (tkinter)."""
from __future__ import annotations

import os
import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from atelier_store import Atelier, ValidationError, TYPES_VEHICULE, ENERGIES, TYPES_INTERVENTION, STATUTS
from electrique import DemoEV, OBDEV, MESURES_EV, AVERTISSEMENT_HT, formater, NON_FOURNI
from pdf_simple import lines_to_pdf
from stage1_e85 import (Moteur, Etude, EtudeErreur, courbe, AVERTISSEMENT, CHECKLIST_E85,
                        CHECKLIST_STAGE1, score_checklist)

DARK, PANEL, INK, MUTED, BORDER = "#091120", "#111e31", "#eef6ff", "#95a8bf", "#2b3d55"
NEON, GOLD, RED, BLUE = "#37e4a5", "#ffcf6a", "#ff4d5e", "#3aa0ff"
FOOTER = "VM Performance 2.0 — prototype privé"


def _ouvrir(path: Path):
    try:
        if hasattr(os, "startfile"):
            os.startfile(path)  # type: ignore[attr-defined]
    except OSError:
        pass


class Base(tk.Toplevel):
    titre = "VM Performance"

    def __init__(self, parent):
        super().__init__(parent)
        self.title(f"{self.titre} — VM Performance 2.0")
        self.configure(bg=DARK)
        self.geometry("1040x700")
        self.minsize(820, 560)
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", rowheight=24)

    def lab(self, parent, text, size=10, color=MUTED, bold=False, **kw):
        return tk.Label(parent, text=text, bg=kw.pop("bg", DARK), fg=color,
                        font=("Segoe UI", size, "bold" if bold else "normal"), justify="left", **kw)

    def btn(self, parent, text, cmd, accent=False):
        return tk.Button(parent, text=text, command=cmd, relief="flat", cursor="hand2",
                         bg=NEON if accent else "#1b2b42", fg="#06101d" if accent else INK,
                         activebackground=GOLD, font=("Segoe UI", 10, "bold"), padx=12, pady=6)

    def champ(self, parent, label, row, widget=None, width=28):
        self.lab(parent, label, 9, INK, bg=PANEL).grid(row=row, column=0, sticky="w", pady=3, padx=(0, 8))
        w = widget or tk.Entry(parent, width=width, relief="flat", bg="#e8f1fb", fg="#142037", font=("Segoe UI", 10))
        w.grid(row=row, column=1, sticky="we", pady=3)
        return w


class AtelierWindow(Base):
    titre = "Atelier : clients, véhicules, devis et interventions"

    def __init__(self, parent, db_path: Path | None = None):
        super().__init__(parent)
        self.store = Atelier(db_path)
        self.lab(self, "ATELIER", 18, NEON, True).pack(anchor="w", padx=20, pady=(14, 0))
        self.lab(self, "Données enregistrées uniquement sur ce PC. Collecte minimale : pas de pièce d'identité, "
                 "pas de code de sécurité.", 9).pack(anchor="w", padx=20)
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=16, pady=10)
        self.tab_clients(nb)
        self.tab_vehicules(nb)
        self.tab_interventions(nb)
        bas = tk.Frame(self, bg=DARK)
        bas.pack(fill="x", padx=16, pady=(0, 12))
        for t, c in (("💾 Sauvegarder", self.sauvegarder), ("♻ Restaurer", self.restaurer),
                     ("⌄ Export CSV", self.export_csv), ("🗑 Purger > 3 ans", self.purger)):
            self.btn(bas, t, c).pack(side="left", padx=(0, 6))
        self.rafraichir()

    # -- onglets
    def _form(self, nb, titre):
        f = tk.Frame(nb, bg=DARK)
        nb.add(f, text=titre)
        left = tk.Frame(f, bg=PANEL, padx=14, pady=12)
        left.pack(side="left", fill="y", padx=(0, 10), pady=6)
        left.grid_columnconfigure(1, weight=1)
        right = tk.Frame(f, bg=DARK)
        right.pack(side="left", fill="both", expand=True, pady=6)
        return left, right

    def _tree(self, parent, cols):
        tv = ttk.Treeview(parent, columns=[c for c, _ in cols], show="headings", selectmode="browse")
        for c, w in cols:
            tv.heading(c, text=c)
            tv.column(c, width=w, anchor="w")
        tv.pack(fill="both", expand=True)
        return tv

    def tab_clients(self, nb):
        l, r = self._form(nb, "👤 Clients")
        self.c_nom = self.champ(l, "Nom / entreprise *", 0)
        self.c_tel = self.champ(l, "Téléphone", 1)
        self.c_mail = self.champ(l, "E-mail", 2)
        self.c_notes = self.champ(l, "Notes", 3)
        self.btn(l, "➕ Ajouter le client", self.add_client, True).grid(row=4, column=0, columnspan=2, sticky="we", pady=(10, 4))
        self.btn(l, "🗑 Supprimer (droit à l'effacement)", self.del_client).grid(row=5, column=0, columnspan=2, sticky="we")
        self.tv_c = self._tree(r, [("Nom", 220), ("Téléphone", 130), ("E-mail", 200), ("Créé", 150)])

    def tab_vehicules(self, nb):
        l, r = self._form(nb, "🚗 Véhicules")
        self.v_client = self.champ(l, "Client *", 0, ttk.Combobox(l, state="readonly", width=26))
        self.v_type = self.champ(l, "Type *", 1, ttk.Combobox(l, state="readonly", values=TYPES_VEHICULE, width=26))
        self.v_type.set("Auto")
        self.v_marque = self.champ(l, "Marque *", 2)
        self.v_modele = self.champ(l, "Modèle", 3)
        self.v_annee = self.champ(l, "Année", 4)
        self.v_energie = self.champ(l, "Énergie *", 5, ttk.Combobox(l, state="readonly", values=ENERGIES, width=26))
        self.v_energie.set("Essence")
        self.v_km = self.champ(l, "Kilométrage", 6)
        self.btn(l, "➕ Ajouter le véhicule", self.add_vehicule, True).grid(row=7, column=0, columnspan=2, sticky="we", pady=(10, 4))
        self.btn(l, "📄 Fiche PDF du véhicule", self.pdf_vehicule).grid(row=8, column=0, columnspan=2, sticky="we")
        self.tv_v = self._tree(r, [("Client", 170), ("Type", 70), ("Marque", 110), ("Modèle", 120), ("Année", 60), ("Énergie", 90), ("Km", 80)])

    def tab_interventions(self, nb):
        l, r = self._form(nb, "🧾 Devis & interventions")
        self.i_veh = self.champ(l, "Véhicule *", 0, ttk.Combobox(l, state="readonly", width=26))
        self.i_type = self.champ(l, "Type *", 1, ttk.Combobox(l, state="readonly", values=TYPES_INTERVENTION, width=26))
        self.i_type.set("Diagnostic")
        self.i_date = self.champ(l, "Date (JJ/MM/AAAA)", 2)
        self.i_date.insert(0, date.today().strftime("%d/%m/%Y"))
        self.i_desc = self.champ(l, "Description *", 3)
        self.i_montant = self.champ(l, "Montant (€)", 4)
        self.i_statut = self.champ(l, "Statut", 5, ttk.Combobox(l, state="readonly", values=STATUTS, width=26))
        self.i_statut.set("Devis")
        self.btn(l, "➕ Enregistrer", self.add_intervention, True).grid(row=6, column=0, columnspan=2, sticky="we", pady=(10, 4))
        self.btn(l, "✔ Changer le statut de la sélection", self.maj_statut).grid(row=7, column=0, columnspan=2, sticky="we")
        self.tv_i = self._tree(r, [("Date", 90), ("Client", 140), ("Véhicule", 140), ("Type", 130), ("Description", 220), ("Montant", 80), ("Statut", 80)])

    # -- actions
    def _safe(self, fn):
        try:
            fn()
            self.rafraichir()
        except ValidationError as exc:
            messagebox.showwarning("Vérifie la saisie", str(exc), parent=self)

    def add_client(self):
        def go():
            self.store.ajouter_client(self.c_nom.get(), self.c_tel.get(), self.c_mail.get(), self.c_notes.get())
            for e in (self.c_nom, self.c_tel, self.c_mail, self.c_notes):
                e.delete(0, "end")
        self._safe(go)

    def del_client(self):
        sel = self.tv_c.selection()
        if not sel:
            return
        if messagebox.askyesno("Supprimer", "Supprimer ce client, ses véhicules et tout son historique ?", parent=self):
            self._safe(lambda: self.store.supprimer_client(sel[0]))

    def add_vehicule(self):
        cid = self._clients_ids.get(self.v_client.get())
        def go():
            if not cid:
                raise ValidationError("Choisis un client.")
            self.store.ajouter_vehicule(cid, self.v_type.get(), self.v_marque.get(), self.v_modele.get(),
                                        self.v_annee.get(), self.v_energie.get(), self.v_km.get())
            for e in (self.v_marque, self.v_modele, self.v_annee, self.v_km):
                e.delete(0, "end")
        self._safe(go)

    def add_intervention(self):
        vid = self._veh_ids.get(self.i_veh.get())
        def go():
            if not vid:
                raise ValidationError("Choisis un véhicule.")
            self.store.ajouter_intervention(vid, self.i_type.get(), self.i_desc.get(), self.i_montant.get(),
                                            self.i_statut.get(), self.i_date.get())
            self.i_desc.delete(0, "end")
            self.i_montant.delete(0, "end")
        self._safe(go)

    def maj_statut(self):
        sel = self.tv_i.selection()
        if sel:
            self._safe(lambda: self.store.changer_statut(sel[0], self.i_statut.get()))

    def pdf_vehicule(self):
        sel = self.tv_v.selection()
        if not sel:
            messagebox.showinfo("Fiche PDF", "Sélectionne un véhicule dans la liste.", parent=self)
            return
        path = filedialog.asksaveasfilename(parent=self, defaultextension=".pdf", filetypes=[("PDF", "*.pdf")],
                                            initialfile="fiche-atelier.pdf")
        if path:
            titre, lignes = self.store.rapport_lignes(sel[0])
            _ouvrir(lines_to_pdf(titre, lignes, Path(path), FOOTER))

    def export_csv(self):
        path = filedialog.asksaveasfilename(parent=self, defaultextension=".csv", filetypes=[("CSV", "*.csv")],
                                            initialfile="interventions.csv")
        if path:
            self.store.export_csv(Path(path))
            messagebox.showinfo("Export", "Export CSV terminé.", parent=self)

    def sauvegarder(self):
        path = filedialog.asksaveasfilename(parent=self, defaultextension=".vmsave",
                                            filetypes=[("Sauvegarde VM", "*.vmsave")],
                                            initialfile=f"sauvegarde-vm-{date.today().isoformat()}.vmsave")
        if path:
            self.store.sauvegarder(Path(path))
            messagebox.showinfo("Sauvegarde", "Sauvegarde créée. Garde-la sur une clé USB ou un disque à part.", parent=self)

    def restaurer(self):
        path = filedialog.askopenfilename(parent=self, filetypes=[("Sauvegarde VM", "*.vmsave"), ("Tous", "*.*")])
        if path and messagebox.askyesno("Restaurer", "Remplacer les données actuelles par cette sauvegarde ?", parent=self):
            self._safe(lambda: self.store.restaurer(Path(path)))

    def purger(self):
        if messagebox.askyesno("Conservation des données", "Supprimer les clients sans intervention depuis plus de 3 ans ?", parent=self):
            n = self.store.purger_anciens(3)
            self.rafraichir()
            messagebox.showinfo("Conservation", f"{n} client(s) supprimé(s).", parent=self)

    def rafraichir(self):
        for tv in (self.tv_c, self.tv_v, self.tv_i):
            tv.delete(*tv.get_children())
        clients = self.store.clients()
        self._clients_ids = {f"{c['nom']} ({c['id'][:4]})": c["id"] for c in clients}
        self.v_client["values"] = list(self._clients_ids)
        for c in clients:
            self.tv_c.insert("", "end", iid=c["id"], values=(c["nom"], c["telephone"], c["email"], c["cree"][:16]))
        vehs = self.store.vehicules()
        self._veh_ids = {f"{v['marque']} {v['modele']} — {v['client']} ({v['id'][:4]})": v["id"] for v in vehs}
        self.i_veh["values"] = list(self._veh_ids)
        for v in vehs:
            self.tv_v.insert("", "end", iid=v["id"], values=(v["client"], v["type"], v["marque"], v["modele"], v["annee"],
                                                             v["energie"], "" if v["kilometrage"] is None else v["kilometrage"]))
        for i in self.store.interventions():
            m = "" if i["montant"] is None else f"{i['montant']:.2f} €".replace(".", ",")
            self.tv_i.insert("", "end", iid=i["id"], values=(i["date"], i["client"], f"{i['marque']} {i['modele']}",
                                                             i["type"] + (" [DÉMO]" if i["demo"] else ""), i["description"], m, i["statut"]))


class Stage1Window(Base):
    titre = "Étude Stage 1 / E85 (simulation)"

    def __init__(self, parent):
        super().__init__(parent)
        bandeau = tk.Frame(self, bg=RED, padx=14, pady=8)
        bandeau.pack(fill="x")
        tk.Label(bandeau, text="SIMULATION — ESTIMATION NON CERTIFIÉE · aucune lecture ni écriture de calculateur",
                 bg=RED, fg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        body = tk.Frame(self, bg=DARK)
        body.pack(fill="both", expand=True, padx=14, pady=10)
        form = tk.Frame(body, bg=PANEL, padx=14, pady=12)
        form.pack(side="left", fill="y")
        form.grid_columnconfigure(1, weight=1)
        self.nom = self.champ(form, "Nom de l'étude", 0)
        self.nom.insert(0, "Étude client")
        entries = [("o_p", "Origine : puissance (ch) *", "150"), ("o_c", "Origine : couple (Nm) *", "250"),
                   ("r_c", "Régime couple max", "2000"), ("r_p", "Régime puissance max", "5500"),
                   ("r_m", "Régime maxi", "6500"), ("c_p", "Après : puissance (ch) *", ""),
                   ("c_c", "Après : couple (Nm) *", ""), ("src", "Source des valeurs « après »", "")]
        self.e = {}
        for row, (k, lab, val) in enumerate(entries, 1):
            self.e[k] = self.champ(form, lab, row, width=16)
            self.e[k].insert(0, val)
        self.vars = {}
        r = len(entries) + 1
        self.lab(form, "Points de contrôle", 10, GOLD, True, bg=PANEL).grid(row=r, column=0, columnspan=2, sticky="w", pady=(10, 2))
        for k, txt in CHECKLIST_STAGE1 + CHECKLIST_E85:
            r += 1
            v = tk.BooleanVar()
            self.vars[k] = v
            tk.Checkbutton(form, text=txt, variable=v, bg=PANEL, fg=INK, selectcolor=DARK, activebackground=PANEL,
                           wraplength=330, justify="left", anchor="w", font=("Segoe UI", 8)).grid(row=r, column=0, columnspan=2, sticky="w")
        r += 1
        self.btn(form, "📈 Calculer les courbes", self.calculer, True).grid(row=r, column=0, sticky="we", pady=(10, 0))
        self.btn(form, "📄 Rapport PDF", self.pdf).grid(row=r, column=1, sticky="we", pady=(10, 0), padx=(6, 0))
        right = tk.Frame(body, bg=DARK)
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))
        self.canvas = tk.Canvas(right, bg=PANEL, highlightthickness=0, height=360)
        self.canvas.pack(fill="both", expand=True)
        self.info = self.lab(right, AVERTISSEMENT, 9, GOLD, wraplength=560)
        self.info.pack(anchor="w", pady=(8, 0))
        self.etude = None

    def _etude(self) -> Etude:
        def f(k, integer=False):
            v = self.e[k].get().strip().replace(",", ".")
            if not v:
                raise EtudeErreur("Remplis les champs marqués *. Les valeurs « après » doivent venir d'une source réelle.")
            try:
                return int(float(v)) if integer else float(v)
            except ValueError as exc:
                raise EtudeErreur(f"Valeur invalide : {v}") from exc
        rc, rp, rm = f("r_c", True), f("r_p", True), f("r_m", True)
        return Etude(self.nom.get().strip() or "Étude", Moteur(f("o_p"), f("o_c"), rc, rp, rm),
                     Moteur(f("c_p"), f("c_c"), rc, rp, rm), {k: v.get() for k, v in self.vars.items()},
                     self.e["src"].get().strip())

    def calculer(self):
        try:
            self.etude = self._etude()
            a, b = courbe(self.etude.origine), courbe(self.etude.cible)
        except EtudeErreur as exc:
            messagebox.showwarning("Étude", str(exc), parent=self)
            return
        self.dessiner(a, b)
        e = self.etude.ecarts()
        s, n = score_checklist(self.etude.checklist, CHECKLIST_STAGE1 + CHECKLIST_E85)
        txt = (f"Écart : {e['puissance_ch']:+g} ch ({e['puissance_pct']:+g} %) · {e['couple_nm']:+g} Nm ({e['couple_pct']:+g} %) · "
               f"points de contrôle validés : {s}/{n}\n" + "\n".join("⚠ " + x for x in self.etude.alertes()) + "\n" + AVERTISSEMENT)
        self.info.config(text=txt)

    def dessiner(self, a, b):
        c = self.canvas
        c.delete("all")
        w, h = max(c.winfo_width(), 400), max(c.winfo_height(), 300)
        pad = 46
        rmax = a[-1][0]
        vmax = max(max(t for _, t, _ in a + b), max(p for _, _, p in a + b)) * 1.1
        X = lambda r: pad + (r - 1000) / max(1, rmax - 1000) * (w - 2 * pad)
        Y = lambda v: h - pad - v / vmax * (h - 2 * pad)
        c.create_line(pad, h - pad, w - pad, h - pad, fill=BORDER)
        c.create_line(pad, pad, pad, h - pad, fill=BORDER)
        for r in range(1000, rmax + 1, 1000):
            c.create_text(X(r), h - pad + 14, text=str(r), fill=MUTED, font=("Segoe UI", 8))
        for pts, col, dash, lab in ((a, BLUE, (4, 3), "origine"), (b, RED, None, "après (saisi)")):
            c.create_line(*[v for r, t, _ in pts for v in (X(r), Y(t))], fill=col, width=2, dash=dash)
            c.create_line(*[v for r, _, p in pts for v in (X(r), Y(p))], fill=GOLD if lab != "origine" else MUTED, width=2, dash=dash)
        c.create_text(pad + 6, pad - 18, anchor="w", fill=INK, font=("Segoe UI", 9, "bold"),
                      text="Couple (bleu origine / rouge après) · Puissance (gris origine / or après) — ESTIMATION")
        c.create_text(w - pad, h - 12, anchor="e", fill=MUTED, font=("Segoe UI", 8), text="tr/min")

    def pdf(self):
        if not self.etude:
            self.calculer()
            if not self.etude:
                return
        path = filedialog.asksaveasfilename(parent=self, defaultextension=".pdf", filetypes=[("PDF", "*.pdf")],
                                            initialfile="etude-stage1-e85.pdf")
        if path:
            _ouvrir(lines_to_pdf("Étude Stage 1 / E85 — SIMULATION", self.etude.lignes_rapport(), Path(path), FOOTER))


class ElectriqueWindow(Base):
    titre = "Véhicules électriques et hybrides"

    def __init__(self, parent, connexion=None, module_obd=None, db_path: Path | None = None, verrou=None):
        super().__init__(parent)
        self.source = OBDEV(connexion, module_obd, verrou) if connexion is not None else DemoEV()
        self.store = Atelier(db_path)
        self.lab(self, "ÉLECTRIQUE / HYBRIDE", 18, BLUE, True).pack(anchor="w", padx=20, pady=(14, 0))
        self.lab(self, f"Source : {self.source.nom}", 10, GOLD if self.source.demo else NEON, True).pack(anchor="w", padx=20)
        self.lab(self, AVERTISSEMENT_HT, 9, RED, wraplength=980).pack(anchor="w", padx=20, pady=(4, 8))
        top = tk.Frame(self, bg=PANEL, padx=14, pady=12)
        top.pack(fill="x", padx=16)
        self.txt = tk.Text(top, height=8, bg="#0b1727", fg=INK, font=("Consolas", 10), relief="flat")
        self.txt.pack(fill="x")
        self.btn(top, "⟳ Lire les données disponibles", self.lire, True).pack(anchor="w", pady=(8, 0))
        log = tk.Frame(self, bg=PANEL, padx=14, pady=12)
        log.pack(fill="both", expand=True, padx=16, pady=10)
        log.grid_columnconfigure(1, weight=1)
        self.lab(log, "Journal de recharge (saisie manuelle ou relevé réel)", 11, INK, True, bg=PANEL).grid(row=0, column=0, columnspan=4, sticky="w")
        self.veh = self.champ(log, "Véhicule", 1, ttk.Combobox(log, state="readonly", width=40))
        self.r = {}
        for i, (k, lab) in enumerate((("date", "Date (JJ/MM/AAAA)"), ("d", "Charge début (%)"), ("f", "Charge fin (%)"),
                                      ("kwh", "Énergie (kWh)"), ("t", "Température (°C)")), 2):
            self.r[k] = self.champ(log, lab, i, width=14)
        self.btn(log, "➕ Ajouter la recharge", self.ajouter, True).grid(row=7, column=0, columnspan=2, sticky="w", pady=(8, 0))
        vehs = self.store.vehicules()
        self._veh = {f"{v['marque']} {v['modele']} — {v['client']} ({v['id'][:4]})": v["id"] for v in vehs}
        self.veh["values"] = list(self._veh)
        self.lire()

    def lire(self):
        try:
            mesures = self.source.lire()
        except Exception as exc:  # déconnexion, adaptateur retiré…
            mesures = {}
            messagebox.showwarning("Lecture", f"Lecture impossible : {exc}", parent=self)
        self.txt.config(state="normal")
        self.txt.delete("1.0", "end")
        self.txt.insert("end", "\n".join(formater(mesures, self.source.demo)))
        self.txt.config(state="disabled")

    def ajouter(self):
        vid = self._veh.get(self.veh.get())
        try:
            if not vid:
                raise ValidationError("Choisis un véhicule (crée-le d'abord dans l'Atelier).")
            self.store.ajouter_recharge(vid, self.r["date"].get(), self.r["d"].get(), self.r["f"].get(),
                                        self.r["kwh"].get(), self.r["t"].get(), "Saisie manuelle")
            for e in self.r.values():
                e.delete(0, "end")
            messagebox.showinfo("Recharge", "Recharge enregistrée.", parent=self)
        except ValidationError as exc:
            messagebox.showwarning("Vérifie la saisie", str(exc), parent=self)
