"""Interfaz de línea de comandos y visualización de NeuroEcosistema."""
import argparse
import random
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from neuroecosistema import (ACTION_NAMES, Ecosystem, SCENARIOS, load_brain,
                             new_brain, save_brain, save_results, train_species)

ROOT = Path(__file__).resolve().parent
MODELS = ROOT / "models"
RESULTS = ROOT / "results"


def train(args):
    hidden = tuple(int(part) for part in args.arquitectura.split(","))
    if len(hidden) < 2 or any(n < 1 for n in hidden):
        raise SystemExit("La arquitectura debe incluir al menos dos capas ocultas; ejemplo: 12,8")
    destination = ROOT / args.directorio_modelos
    for species in ("presa", "depredador"):
        brain = train_species(species, args.generaciones, args.poblacion, args.episodios,
                              args.escenario, args.semilla + (0 if species == "presa" else 1_000_000), hidden)
        save_brain(destination / f"{species}.json", brain, species, args.semilla)
    print(f"Modelos guardados en {destination}")


def run_experiments(args):
    rng = random.Random(args.semilla)
    trained_prey = load_brain(MODELS / "presa.json") if (MODELS / "presa.json").exists() else None
    trained_pred = load_brain(MODELS / "depredador.json") if (MODELS / "depredador.json").exists() else None
    alt_path = MODELS / "alternativa"
    alt_prey = load_brain(alt_path / "presa.json") if (alt_path / "presa.json").exists() else None
    alt_pred = load_brain(alt_path / "depredador.json") if (alt_path / "depredador.json").exists() else None
    controllers = ["aleatorio", "neuronal_inicial", "neuronal_entrenado"]
    if alt_prey and alt_pred:
        controllers.append("neuronal_alternativo")
    rows = []
    for scenario_index, scenario in enumerate(SCENARIOS):
        for controller in controllers:
            for _ in range(args.repeticiones):
                # Misma semilla de entorno para los controladores comparados en cada repetición.
                seed = args.semilla + scenario_index * 100_000 + _ * 17
                if controller == "aleatorio":
                    pbrains = dbrains = None
                elif controller == "neuronal_inicial":
                    pbrains = [new_brain("presa", random.Random(seed))] * 12
                    dbrains = [new_brain("depredador", random.Random(seed + 1))] * SCENARIOS[scenario]["predators"]
                elif controller == "neuronal_alternativo":
                    pbrains = [alt_prey] * 12
                    dbrains = [alt_pred] * SCENARIOS[scenario]["predators"]
                else:
                    pbrains = [trained_prey] * 12 if trained_prey else [new_brain("presa", rng) for _ in range(12)]
                    dbrains = [trained_pred] * SCENARIOS[scenario]["predators"] if trained_pred else None
                world = Ecosystem(seed, scenario, pbrains, dbrains,
                                  controller="random" if controller == "aleatorio" else "neural")
                world.controller = controller
                result = world.run(); rows.append(result)
                print(f"{scenario:10} {controller:20} semilla={seed} supervivientes={result.prey_survived} "
                      f"alimento={result.food_eaten} capturas={result.captures} ticks={result.ticks}")
    path = RESULTS / "experimentos.csv"
    save_results(path, rows)
    print(f"Datos guardados en {path}")


class SimulationWindow:
    CELL = 20

    def __init__(self, scenario: str, seed: int, random_agents: bool):
        self.root = tk.Tk()
        self.root.title("NeuroEcosistema — Julian Pulido")
        self.root.resizable(False, False)
        self.paused = False
        rng = random.Random(seed)
        pmodel, dmodel = MODELS / "presa.json", MODELS / "depredador.json"
        pbrain = load_brain(pmodel) if pmodel.exists() else new_brain("presa", rng)
        dbrain = load_brain(dmodel) if dmodel.exists() else new_brain("depredador", rng)
        self.world = Ecosystem(seed, scenario, [pbrain] * 12,
            [dbrain] * SCENARIOS[scenario]["predators"],
            controller="random" if random_agents else "neural")
        frame = ttk.Frame(self.root, padding=8); frame.grid()
        self.canvas = tk.Canvas(frame, width=640, height=640, bg="#f3f4ed", highlightthickness=0)
        self.canvas.grid(row=0, column=0, rowspan=5)
        side = ttk.Frame(frame, padding=(12, 0, 0, 0)); side.grid(row=0, column=1, sticky="n")
        ttk.Label(side, text="NEUROECOSISTEMA", font=("Segoe UI", 13, "bold")).grid(sticky="w")
        ttk.Label(side, text="Autor: Julian Pulido").grid(sticky="w", pady=(3, 9))
        self.stats = ttk.Label(side, justify="left"); self.stats.grid(sticky="w", pady=4)
        ttk.Label(side, text="Decisión seleccionada", font=("Segoe UI", 10, "bold")).grid(sticky="w", pady=(12, 3))
        self.detail = tk.Text(side, width=35, height=13, wrap="word", state="disabled"); self.detail.grid(sticky="w")
        ttk.Button(side, text="Pausar / continuar", command=self.toggle).grid(sticky="ew", pady=(10, 2))
        self.canvas.bind("<Button-1>", self.inspect_cell)
        self.root.after(100, self.loop)

    def toggle(self):
        self.paused = not self.paused

    def inspect_cell(self, event):
        x, y = event.x // self.CELL, event.y // self.CELL
        group = next((("presa", self.world.prey), ("depredador", self.world.predators)), None)
        agent = next((a for a in self.world.prey + self.world.predators if a.alive and (a.x, a.y) == (x, y)), None)
        info = "Haz clic en una presa o depredador para consultar la decisión más reciente."
        if agent:
            kind = "presa" if agent in self.world.prey else "depredador"
            decision = next((d for d in reversed(self.world.last_decisions)
                             if d["tipo"] == kind and d["agente"] == (self.world.prey if kind == "presa" else self.world.predators).index(agent)), None)
            info = f"Tipo: {kind}\nEnergía: {agent.energy:.2f}\nÚltima acción: {agent.last_action}\n"
            if decision:
                info += "\nEntradas:\n" + ", ".join(f"{v:.2f}" for v in decision["entradas"])
                info += "\n\nSalidas de la red:\n" + ", ".join(f"{v:.2f}" for v in decision["salidas"])
            else:
                info += "\nAgente controlado por referencia aleatoria."
        self.detail.configure(state="normal"); self.detail.delete("1.0", "end")
        self.detail.insert("1.0", info); self.detail.configure(state="disabled")

    def draw(self):
        c, s = self.canvas, self.CELL; c.delete("all")
        for x, y in self.world.obstacles:
            c.create_rectangle(x*s, y*s, (x+1)*s, (y+1)*s, fill="#63717a", outline="")
        for x, y in self.world.plants:
            c.create_oval(x*s+6, y*s+6, x*s+14, y*s+14, fill="#55a630", outline="")
        for a in self.world.prey:
            if a.alive: c.create_oval(a.x*s+3, a.y*s+3, (a.x+1)*s-3, (a.y+1)*s-3, fill="#3a86ff", outline="white")
        for a in self.world.predators:
            if a.alive: c.create_oval(a.x*s+2, a.y*s+2, (a.x+1)*s-2, (a.y+1)*s-2, fill="#e63946", outline="white")
        living = [p for p in self.world.prey if p.alive]
        energy = f"{sum(p.energy for p in living)/len(living):.1f}" if living else "0"
        self.stats.configure(text=f"Escenario: {self.world.scenario}\nTick: {self.world.tick}/{self.world.max_ticks}\n"
            f"Presas vivas: {len(living)}\nAlimento consumido: {self.world.food_eaten}\n"
            f"Capturas: {self.world.captures}\nEnergía media presas: {energy}")

    def loop(self):
        if not self.paused and self.world.tick < self.world.max_ticks and any(p.alive for p in self.world.prey):
            self.world.step()
        self.draw(); self.root.after(120, self.loop)

    def show(self):
        self.root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="Simulación 2D de presas y depredadores con redes neuronales")
    commands = parser.add_subparsers(dest="command", required=True)
    t = commands.add_parser("entrenar", help="Entrena las redes por neuroevolución")
    t.add_argument("--generaciones", type=int, default=8); t.add_argument("--poblacion", type=int, default=10)
    t.add_argument("--episodios", type=int, default=2); t.add_argument("--escenario", choices=SCENARIOS, default="abundancia")
    t.add_argument("--semilla", type=int, default=71); t.add_argument("--arquitectura", default="12,8")
    t.add_argument("--directorio-modelos", default="models"); t.set_defaults(func=train)
    e = commands.add_parser("experimentos", help="Compara controles en tres escenarios")
    e.add_argument("--repeticiones", type=int, default=10); e.add_argument("--semilla", type=int, default=2026); e.set_defaults(func=run_experiments)
    g = commands.add_parser("visualizar", help="Abre la simulación interactiva")
    g.add_argument("--escenario", choices=SCENARIOS, default="abundancia"); g.add_argument("--semilla", type=int, default=42)
    g.add_argument("--aleatorio", action="store_true"); g.set_defaults(func=lambda a: SimulationWindow(a.escenario, a.semilla, a.aleatorio).show())
    args = parser.parse_args(); args.func(args)


if __name__ == "__main__":
    main()
