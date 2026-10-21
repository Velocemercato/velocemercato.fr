# -*- coding: utf-8 -*-
"""VM Performance 1.0 — diagnostic OBD-II en lecture seule.

Copyright (C) 2026 VM Performance contributors
SPDX-License-Identifier: GPL-2.0-only
Aucun ordre d'ecriture, de reprogrammation ou d'effacement n'est emis.
"""
from __future__ import annotations

import csv
import math
import queue
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP = "VM PERFORMANCE"
VERSION = "2.0 — diagnostic, atelier, clés, Stage 1/E85 (simulation), électrique"
DARK = "#091120"
PANEL = "#111e31"
INK = "#eef6ff"
MUTED = "#95a8bf"
BORDER = "#2b3d55"
NEON = "#37e4a5"
GOLD = "#ffcf6a"
WARNING = "#ff8e74"

FIELDS = (
    ("rpm", "RÉGIME MOTEUR", "tr/min"),
    ("speed", "VITESSE", "km/h"),
    ("coolant", "TEMPÉRATURE", "°C"),
    ("load", "CHARGE MOTEUR", "%"),
    ("voltage", "TENSION OBD", "V"),
)


class DemoBackend:
    name = "DÉMONSTRATION — valeurs simulées"

    def __init__(self) -> None:
        self.t0 = time.monotonic()

    def read_snapshot(self) -> dict[str, float]:
        t = time.monotonic() - self.t0
        return {
            "rpm": max(680, 1450 + 630 * math.sin(t / 3.5) + 145 * math.sin(t / 1.2)),
            "speed": max(0, 38 + 24 * math.sin(t / 8.0)),
            "coolant": 86 + 4 * math.sin(t / 20.0),
            "load": max(5, 28 + 18 * math.sin(t / 5.3)),
            "voltage": 13.9 + 0.12 * math.sin(t / 6.0),
        }

    def read_codes(self) -> list[tuple[str, str]]:
        return [("P0300", "Ratés d'allumage détectés (EXEMPLE FICTIF)")]

    def close(self) -> None:
        pass


class OBDBackend:
    """Uniquement Mode 01, Mode 03 et tension adaptateur : aucune commande d'écriture."""
    name = "OBD2 RÉEL — lecture seule"

    def __init__(self, port: str) -> None:
        try:
            import obd
        except ImportError as exc:
            raise RuntimeError("Bibliothèque OBD absente. Lance INSTALLER_OBD2.bat.") from exc
        self.obd = obd
        self.lock = threading.Lock()
        try:
            # portstr accepte un port COM Windows, ou None pour autodetection.
            self.conn = obd.OBD(portstr=port or None, fast=False, timeout=1)
            if not self.conn.is_connected():
                status = self.conn.status()
                self.conn.close()
                raise RuntimeError(f"Véhicule non connecté ({status}). Vérifie contact, prise et port COM.")
        except Exception as exc:
            if isinstance(exc, RuntimeError):
                raise
            raise RuntimeError(f"Connexion impossible : {exc}") from exc

    def _value(self, command, unit: str | None = None) -> float | None:
        # Respecter les PID compatibles du véhicule, aucun force=True.
        if not self.conn.supports(command):
            return None
        response = self.conn.query(command)
        if response is None or response.is_null():
            return None
        v = response.value
        if v is None:
            return None
        try:
            if unit and hasattr(v, "to"):
                v = v.to(unit)
            return float(getattr(v, "magnitude", v))
        except (ValueError, TypeError, AttributeError):
            return None

    def read_snapshot(self) -> dict[str, float | None]:
        with self.lock:
            return self._snapshot()

    def _snapshot(self) -> dict[str, float | None]:
        commands = self.obd.commands
        return {
            "rpm": self._value(commands.RPM, "rpm"),
            "speed": self._value(commands.SPEED, "kph"),
            "coolant": self._value(commands.COOLANT_TEMP, "degC"),
            "load": self._value(commands.ENGINE_LOAD, "percent"),
            "voltage": self._value(commands.ELM_VOLTAGE, "volt"),
        }

    def read_codes(self) -> list[tuple[str, str]]:
        command = self.obd.commands.GET_DTC
        with self.lock:
            response = self.conn.query(command) if self.conn.supports(command) else None
        if response is None or response.is_null() or not response.value:
            return []
        return [(str(code), str(description or "Description inconnue"))
                for code, description in response.value]

    def close(self) -> None:
        self.conn.close()


class VMApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("VM Performance 2.0 | Prototype privé — diagnostic & atelier")
        self.geometry("1040x740")
        self.minsize(790, 640)
        self.configure(bg=DARK)
        self.backend: DemoBackend | OBDBackend | None = None
        self.events: queue.Queue = queue.Queue()
        self.history: deque[tuple] = deque(maxlen=600)
        self.snapshot: dict[str, float | None] = {}
        self.busy = False
        self.gener = 0
        self.mode = tk.StringVar(value="Démo")
        self.port = tk.StringVar(value="")
        self.connection_label = tk.StringVar(value="● Hors connexion")
        self.status_message = tk.StringVar(value="Prêt · lance des mesures fictives ou connecte un OBD2 compatible")
        self.values: dict[str, tk.StringVar] = {}
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._build_ui()
        self.after(100, self.poll_events)
        self.after(2000, self.heartbeat)

    def _label(self, parent, text, size=10, color=MUTED, bold=False, **kwargs):
        return tk.Label(parent, text=text, bg=kwargs.get("bg", DARK), fg=color,
                        font=("Segoe UI", size, "bold" if bold else "normal"),
                        anchor=kwargs.get("anchor", "w"), justify="left")

    def _button(self, parent, text, command, accent=False):
        b = tk.Button(parent, text=text, command=command, borderwidth=0,
                      font=("Segoe UI", 10, "bold"),
                      bg=NEON if accent else BORDER,
                      fg=DARK if accent else INK,
                      activebackground=GOLD, activeforeground=DARK,
                      relief="flat", padx=13, pady=11, cursor="hand2")
        return b

    def _build_ui(self) -> None:
        header = tk.Frame(self, bg=DARK, padx=28, pady=22)
        header.pack(fill="x")
        self._label(header, "VM  /  PERFORMANCE", size=24, color=NEON, bold=True).pack(anchor="w")
        self._label(header, "Diagnostic auto & moto  •  lecture seule  •  gestion des dossiers de clés perdues",
                    size=11, color=INK).pack(anchor="w", pady=(4, 0))
        actions = tk.Frame(header, bg=DARK)
        actions.pack(anchor="w", pady=(9, 0))
        self._button(actions, "🔑  Clés / dépannage", self.open_key_cases, True).pack(side="left", padx=(0, 6))
        self._button(actions, "🧾  Atelier & devis", self.open_atelier).pack(side="left", padx=(0, 6))
        self._button(actions, "📈  Stage 1 / E85 (simulation)", self.open_stage1).pack(side="left", padx=(0, 6))
        self._button(actions, "⚡  Électrique / hybride", self.open_ev).pack(side="left")
        self._label(header, "PROTOTYPE PRIVÉ — version 2.0 · lecture seule · aucune écriture calculateur",
                    size=9, color=GOLD, bold=True).pack(anchor="w", pady=(6, 0))
        line = tk.Frame(self, height=2, bg=NEON)
        line.pack(fill="x", padx=28)

        connect = tk.Frame(self, bg=PANEL, padx=17, pady=13, highlightbackground=BORDER, highlightthickness=1)
        connect.pack(fill="x", padx=28, pady=(18, 14))
        top = tk.Frame(connect, bg=PANEL)
        top.pack(fill="x")
        self._label(top, "SOURCE DE DONNÉES", 9, NEON, True, bg=PANEL).pack(side="left")
        self._label(top, "AUTO + MOTO OBD2 compatibles", 9, MUTED, bg=PANEL).pack(side="right")
        form = tk.Frame(connect, bg=PANEL)
        form.pack(fill="x", pady=(10, 0))
        self.mode_select = ttk.Combobox(form, state="readonly", textvariable=self.mode,
                                        values=["Démo", "OBD2 réel"], width=15)
        self.mode_select.pack(side="left", padx=(0, 12), ipady=5)
        self._label(form, "Port COM (optionnel) :", 10, INK, bg=PANEL).pack(side="left")
        self.port_input = tk.Entry(form, textvariable=self.port, width=10, relief="flat", bg="#e8f1fb",
                                   fg="#142037", font=("Segoe UI", 11))
        self.port_input.pack(side="left", padx=(8, 10), ipady=7)
        self._label(form, "ex. COM3 · vide = auto", 9, MUTED, bg=PANEL).pack(side="left")
        buttons = tk.Frame(connect, bg=PANEL)
        buttons.pack(fill="x", pady=(12, 0))
        self.connect_button = self._button(buttons, "▶  Simuler les mesures", self.connect, True)
        self.connect_button.pack(side="left", padx=(0, 7))
        self._button(buttons, "⏹  Déconnecter", self.disconnect).pack(side="left", padx=(0, 8))
        self._button(buttons, "⌄  Exporter CSV", self.export_csv).pack(side="left")
        self._label(buttons, "", 10, NEON, True, bg=PANEL).pack(side="right")
        self.connection_display = self._label(buttons, "", 10, NEON, True, bg=PANEL)
        self.connection_display.pack(side="right")
        self.connection_label.trace_add("write", lambda *_: self.connection_display.config(text=self.connection_label.get()))
        self.connection_display.config(text=self.connection_label.get())
        self.mode_select.bind("<<ComboboxSelected>>", self._mode_changed)

        cards = tk.Frame(self, bg=DARK)
        cards.pack(fill="x", padx=23, pady=(0, 14))
        for idx, (key, title, unit) in enumerate(FIELDS):
            frame = tk.Frame(cards, bg=PANEL, highlightthickness=1, highlightbackground=BORDER,
                             padx=12, pady=14)
            frame.grid(row=0, column=idx, padx=5, sticky="nsew")
            cards.grid_columnconfigure(idx, weight=1, uniform="metric")
            self._label(frame, title, 9, MUTED, True, bg=PANEL).pack(anchor="w")
            val = tk.StringVar(value="—")
            self.values[key] = val
            tk.Label(frame, textvariable=val, bg=PANEL, fg=NEON,
                     font=("Segoe UI", 23, "bold"), anchor="w").pack(fill="x", pady=(3, 0))
            self._label(frame, unit, 10, MUTED, bg=PANEL).pack(anchor="w")

        main = tk.Frame(self, bg=DARK)
        main.pack(fill="both", expand=True, padx=28)
        left = tk.Frame(main, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self._label(left, "RÉGIME MOTEUR — HISTORIQUE", 10, INK, True, bg=PANEL).pack(anchor="w", padx=18, pady=(16, 8))
        self.graph = tk.Canvas(left, height=245, bg=PANEL, highlightthickness=0)
        self.graph.pack(fill="both", expand=True, padx=15, pady=(0, 14))
        self.graph.bind("<Configure>", lambda _: self.draw_graph())

        right = tk.Frame(main, bg=PANEL, width=335, highlightbackground=BORDER, highlightthickness=1)
        right.pack(side="right", fill="both")
        right.pack_propagate(False)
        self._label(right, "CODES DÉFAUT (DTC)", 11, INK, True, bg=PANEL).pack(anchor="w", padx=14, pady=(15, 10))
        self.codes = tk.Text(right, bg="#0b1727", fg=INK, font=("Consolas", 10),
                             wrap="word", relief="flat", height=10, padx=12, pady=12)
        self.codes.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.codes.insert("end", "Connecte un véhicule ou démarre la démo, puis clique sur Lire les défauts.\n")
        self.codes.config(state="disabled")
        self._button(right, "⌕  Lire les défauts", self.read_codes).pack(fill="x", padx=12, pady=(0, 12))
        self._label(right, "Lecture uniquement : aucun effacement des codes.\n"
                    "Les résultats ne remplacent pas un diagnostic professionnel.",
                    9, MUTED, bg=PANEL).pack(anchor="w", padx=14, pady=(0, 14))

        bottom = tk.Frame(self, bg=DARK, padx=28, pady=16)
        bottom.pack(fill="x")
        self._label(bottom, "⚠ Démo = données fictives : ne démarre AUCUNE voiture. Ne jamais utiliser en conduisant.\n"
                    "OBD2 lecture seule, motos seulement si compatibles.", 9, GOLD).pack(side="left")
        tk.Label(bottom, textvariable=self.status_message, bg=DARK, fg=MUTED,
                 font=("Segoe UI", 9), justify="right", anchor="e", wraplength=360).pack(side="right")
        self._mode_changed()

    def open_key_cases(self):
        from dossiers_cles import DossiersWindow
        existing = getattr(self, 'keys_window', None)
        if existing is not None and existing.winfo_exists():
            existing.lift()
            existing.focus_force()
            return
        try:
            self.keys_window = DossiersWindow(self)
        except (OSError, RuntimeError, ValueError) as exc:
            messagebox.showerror("Atelier clés", str(exc))

    def _open_once(self, attr, factory, title):
        existing = getattr(self, attr, None)
        if existing is not None and existing.winfo_exists():
            existing.lift()
            existing.focus_force()
            return
        try:
            setattr(self, attr, factory())
        except (OSError, RuntimeError, ValueError) as exc:
            messagebox.showerror(title, str(exc))

    def open_atelier(self):
        from fenetres_v2 import AtelierWindow
        self._open_once("atelier_window", lambda: AtelierWindow(self), "Atelier")

    def open_stage1(self):
        from fenetres_v2 import Stage1Window
        self._open_once("stage1_window", lambda: Stage1Window(self), "Stage 1 / E85")

    def open_ev(self):
        from fenetres_v2 import ElectriqueWindow
        b = self.backend
        if isinstance(b, OBDBackend):
            factory = lambda: ElectriqueWindow(self, b.conn, b.obd, verrou=b.lock)
        else:
            factory = lambda: ElectriqueWindow(self)
        self._open_once("ev_window", factory, "Électrique")

    def _mode_changed(self, _=None):
        is_demo = self.mode.get() == "Démo"
        self.port_input.config(state="disabled" if is_demo else "normal")
        self.connect_button.config(text="▶  Simuler les mesures" if is_demo else "🔌  Connecter OBD2")

    def _run(self, kind, fn, generation=None):
        gen = self.gener if generation is None else generation
        def work():
            try:
                value = fn()
                self.events.put((gen, kind, value, None))
            except Exception as exc:
                self.events.put((gen, kind, None, str(exc)))
        threading.Thread(target=work, daemon=True).start()

    def connect(self):
        if self.busy:
            return
        self.disconnect()
        self.busy = True
        mode = self.mode.get()
        port = self.port.get().strip()
        self.connection_label.set("● Connexion…")
        self.status_message.set("Connexion en cours. Ne débranche pas l'adaptateur.")
        self._run("connected", lambda: DemoBackend() if mode == "Démo" else OBDBackend(port))

    def disconnect(self):
        self.gener += 1
        old = self.backend
        self.backend = None
        self.busy = False
        self.connection_label.set("● Hors connexion")
        self.status_message.set("Déconnecté · aucune écriture ECU")
        if old is not None:
            self._run("closed", old.close, generation=-1)

    def poll_events(self):
        while True:
            try:
                gen, kind, value, error = self.events.get_nowait()
            except queue.Empty:
                break
            if gen != self.gener:
                if kind == "connected" and value is not None:
                    self._run("closed", value.close, generation=-1)
                continue
            if kind == "connected":
                self.busy = False
                if error:
                    self.connection_label.set("● Erreur connexion")
                    self.status_message.set(error)
                    messagebox.showerror("Connexion OBD2", error)
                else:
                    self.backend = value
                    self.history.clear()
                    self.connection_label.set("● " + ("DÉMO" if isinstance(value, DemoBackend) else "OBD2 CONNECTÉ"))
                    self.status_message.set(value.name)
                    self.refresh_data()
            elif kind == "snapshot":
                self.busy = False
                if error:
                    self.status_message.set("Erreur lecture : " + error)
                else:
                    self.snapshot = value
                    self.history.append((datetime.now().astimezone().isoformat(timespec="seconds"),
                                         self.backend.name if self.backend else "", *[value.get(k) for k, _, _ in FIELDS]))
                    for key, _, _ in FIELDS:
                        x = value.get(key)
                        self.values[key].set("—" if x is None else (f"{x:.1f}" if key == "voltage" else f"{round(x)}"))
                    self.draw_graph()
            elif kind == "codes":
                self.busy = False
                if error:
                    self.status_message.set(error)
                    messagebox.showerror("Lecture défauts", error)
                else:
                    if not value:
                        text = "Aucun code défaut renvoyé (ou lecture non prise en charge)."
                    else:
                        text = "\n\n".join(f"{code}\n{desc}" for code, desc in value)
                    if isinstance(self.backend, DemoBackend):
                        text = "⚠ CODES SIMULÉS — AUCUN VÉHICULE CONNECTÉ\n\n" + text
                    self.codes.config(state="normal")
                    self.codes.delete("1.0", "end")
                    self.codes.insert("end", text)
                    self.codes.config(state="disabled")
        self.after(120, self.poll_events)

    def heartbeat(self):
        if self.backend is not None and not self.busy:
            self.refresh_data()
        self.after(2000, self.heartbeat)

    def refresh_data(self):
        if self.backend is None or self.busy:
            return
        self.busy = True
        self._run("snapshot", self.backend.read_snapshot)

    def read_codes(self):
        if self.backend is None:
            messagebox.showinfo("Lecture DTC", "Connecte d'abord le mode Démo ou ton adaptateur OBD2.")
            return
        if self.busy:
            messagebox.showinfo("Patiente", "Une lecture est en cours. Réessaie dans un instant.")
            return
        self.busy = True
        self._run("codes", self.backend.read_codes)

    def draw_graph(self):
        self.graph.delete("all")
        w = max(self.graph.winfo_width(), 30)
        h = max(self.graph.winfo_height(), 30)
        for step in range(1, 5):
            y = h * step / 5
            self.graph.create_line(7, y, w-8, y, fill=BORDER, dash=(3, 7))
        valid = [row[2] for row in self.history if row[2] is not None]
        if len(valid) < 2:
            self.graph.create_text(w/2, h/2, text="En attente des mesures…",
                                   fill=MUTED, font=("Segoe UI", 12))
            return
        data = valid[-70:]
        maxval = max(3000, max(data) * 1.15)
        coords = []
        for idx, rpm in enumerate(data):
            coords.extend((10+(w-22)*idx/(len(data)-1), h-15-(h-30)*rpm/maxval))
        self.graph.create_line(*coords, fill=NEON, width=3, smooth=True)
        self.graph.create_text(12, 12, text=f"ÉCHELLE 0 – {maxval:.0f} tr/min",
                               anchor="nw", fill=MUTED, font=("Segoe UI", 9))

    def export_csv(self):
        if not self.history:
            messagebox.showinfo("Export CSV", "Commence par enregistrer des mesures en mode démo ou réel.")
            return
        dest = filedialog.asksaveasfilename(title="Exporter les mesures",
                                             defaultextension=".csv", initialfile="VM_mesures.csv",
                                             filetypes=[("Tableur CSV", "*.csv")])
        if not dest:
            return
        try:
            with Path(dest).open("w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["Horodatage local", "Source", "RPM tr/min", "Vitesse km/h",
                                 "Température °C", "Charge moteur %", "Tension V"])
                writer.writerows(self.history)
            self.status_message.set(f"CSV enregistré : {Path(dest).name} ({len(self.history)} lignes)")
        except OSError as exc:
            messagebox.showerror("Export CSV", str(exc))

    def on_close(self):
        if self.backend is not None:
            try:
                self.backend.close()
            except Exception:
                pass
        self.destroy()


def selftest(report: Path | None = None) -> int:
    """Démarrage automatique sans véhicule (contrôle de l'EXE) : ouvre chaque fenêtre en mode démo,
    crée des données d'essai dans une base TEMPORAIRE, génère un PDF, puis ferme tout."""
    import tempfile
    from atelier_store import Atelier
    from fenetres_v2 import AtelierWindow, Stage1Window, ElectriqueWindow
    from pdf_simple import lines_to_pdf
    lines = []
    tmp = Path(tempfile.mkdtemp(prefix="vmperf-selftest-"))
    db = tmp / "selftest.sqlite3"
    try:
        store = Atelier(db)
        c = store.ajouter_client("Client essai")
        v = store.ajouter_vehicule(c, "Auto", "Essai", "Démo", "2020", "Hybride", 1000)
        store.ajouter_intervention(v, "Diagnostic", "Selftest", 0, "Terminé", demo=True)
        titre, lignes = store.rapport_lignes(v)
        lines_to_pdf(titre, lignes, tmp / "selftest.pdf", "selftest")
        lines.append("BASE+PDF OK")
        app = VMApp()
        app.update()
        app.connect()
        for _ in range(30):
            app.update()
            time.sleep(0.05)
        lines.append(f"DEMO {'OK' if app.backend is not None else 'KO'}")
        w1 = AtelierWindow(app, db); app.update(); lines.append(f"ATELIER OK ({len(w1.tv_i.get_children())} intervention)")
        w2 = Stage1Window(app)
        for k, val in (("c_p", "180"), ("c_c", "320"), ("src", "selftest")):
            w2.e[k].delete(0, "end"); w2.e[k].insert(0, val)
        w2.calculer(); app.update(); lines.append(f"STAGE1 {'OK' if w2.etude else 'KO'}")
        w3 = ElectriqueWindow(app, db_path=db); app.update(); lines.append("ELECTRIQUE OK")
        app.on_close()
        ok = all(l.split()[1] == "OK" for l in lines if len(l.split()) > 1)
    except Exception as exc:  # le rapport doit indiquer l'erreur
        lines.append(f"ERREUR {type(exc).__name__}: {exc}")
        ok = False
    text = "\n".join(lines) + ("\nRESULTAT OK\n" if ok else "\nRESULTAT ECHEC\n")
    if report:
        Path(report).write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0 if ok else 1


def main():
    import sys
    if "--selftest" in sys.argv:
        i = sys.argv.index("--selftest")
        out = sys.argv[i + 1] if len(sys.argv) > i + 1 else None
        raise SystemExit(selftest(Path(out) if out else None))
    app = VMApp()
    app.mainloop()


if __name__ == "__main__":
    main()
