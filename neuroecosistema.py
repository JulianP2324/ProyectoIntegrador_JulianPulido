"""Núcleo del proyecto integrador NeuroEcosistema. Solo usa la biblioteca estándar."""
from __future__ import annotations

from dataclasses import dataclass, asdict
import json
import math
import random
from pathlib import Path
from typing import Iterable

SIZE = 32
ACTIONS = ((0, 0), (0, -1), (0, 1), (-1, 0), (1, 0))
ACTION_NAMES = ("quieto", "arriba", "abajo", "izquierda", "derecha")
PREY_INPUTS = 10
PREDATOR_INPUTS = 9
HIDDEN = (12, 8)


class NeuralNetwork:
    """Perceptrón multicapa con dos capas ocultas y activación tanh."""
    def __init__(self, sizes: tuple[int, ...], rng: random.Random, genes: list[float] | None = None):
        self.sizes = sizes
        self.genes = list(genes) if genes is not None else [rng.gauss(0, 0.55) for _ in range(self.gene_count(sizes))]
        if len(self.genes) != self.gene_count(sizes):
            raise ValueError("El número de parámetros no corresponde a la arquitectura")

    @staticmethod
    def gene_count(sizes: tuple[int, ...]) -> int:
        return sum((a + 1) * b for a, b in zip(sizes, sizes[1:]))

    def forward(self, values: Iterable[float]) -> list[float]:
        x = list(values)
        if len(x) != self.sizes[0]:
            raise ValueError(f"Se esperaban {self.sizes[0]} entradas y llegaron {len(x)}")
        cursor = 0
        for layer_index, (n_in, n_out) in enumerate(zip(self.sizes, self.sizes[1:])):
            layer = []
            for _ in range(n_out):
                weights = self.genes[cursor:cursor + n_in]
                bias = self.genes[cursor + n_in]
                cursor += n_in + 1
                z = sum(w * v for w, v in zip(weights, x)) + bias
                layer.append(math.tanh(z))
            x = layer
        return x

    def to_dict(self) -> dict:
        return {"architecture": list(self.sizes), "genes": self.genes}

    @classmethod
    def from_dict(cls, data: dict) -> "NeuralNetwork":
        return cls(tuple(data["architecture"]), random.Random(0), data["genes"])


@dataclass
class Agent:
    x: int
    y: int
    energy: float
    brain: NeuralNetwork | None = None
    alive: bool = True
    score: float = 0.0
    last_action: str = "quieto"


@dataclass
class EpisodeResult:
    seed: int
    scenario: str
    controller: str
    ticks: int
    prey_survived: int
    food_eaten: int
    captures: int
    prey_energy_end: float
    predator_energy_end: float
    capture_tick_mean: float | None


SCENARIOS = {
    "abundancia": {"plants": 110, "predators": 2, "obstacles": 0},
    "escasez": {"plants": 28, "predators": 2, "obstacles": 0},
    "presion": {"plants": 70, "predators": 5, "obstacles": 45},
}


def sign(x: int) -> float:
    return 0.0 if x == 0 else (1.0 if x > 0 else -1.0)


def nearest(agent: Agent, others: list[Agent]) -> Agent | None:
    living = [a for a in others if a.alive]
    return min(living, key=lambda a: abs(a.x-agent.x)+abs(a.y-agent.y), default=None)


class Ecosystem:
    def __init__(self, seed: int, scenario: str = "abundancia", prey_brains: list[NeuralNetwork] | None = None,
                 predator_brains: list[NeuralNetwork] | None = None, controller: str = "neural",
                 prey_count: int = 12, max_ticks: int = 180):
        if scenario not in SCENARIOS:
            raise ValueError(f"Escenario desconocido: {scenario}")
        self.rng = random.Random(seed)
        self.seed, self.scenario, self.controller = seed, scenario, controller
        self.max_ticks = max_ticks
        config = SCENARIOS[scenario]
        cells = [(x, y) for x in range(SIZE) for y in range(SIZE)]
        self.rng.shuffle(cells)
        self.obstacles = set(cells[:config["obstacles"]])
        free = [c for c in cells if c not in self.obstacles]
        self.plants = set(free[:config["plants"]])
        occupied = set(self.plants)
        def place(brains, count, energy):
            agents = []
            for i in range(count):
                pos = next(c for c in free if c not in occupied)
                occupied.add(pos)
                agents.append(Agent(*pos, energy, brains[i] if brains and i < len(brains) else None))
            return agents
        self.prey = place(prey_brains, prey_count, 12.0)
        self.predators = place(predator_brains, config["predators"], 14.0)
        self.tick = self.food_eaten = self.captures = 0
        self.capture_ticks: list[int] = []
        self.last_decisions: list[dict] = []

    def prey_inputs(self, a: Agent) -> list[float]:
        plant = min(self.plants, key=lambda p: abs(p[0]-a.x)+abs(p[1]-a.y), default=None)
        predator = nearest(a, self.predators)
        dx, dy = ((plant[0]-a.x, plant[1]-a.y) if plant else (0, 0))
        px, py = ((predator.x-a.x, predator.y-a.y) if predator else (0, 0))
        return [a.x/(SIZE-1)*2-1, a.y/(SIZE-1)*2-1, sign(dx), sign(dy),
                sign(px), sign(py), (abs(px)+abs(py))/SIZE if predator else 1.0,
                a.energy/16-0.5, len(self.plants)/150-0.5,
                1.0 if (a.x, a.y) in self.plants else -1.0]

    def predator_inputs(self, a: Agent) -> list[float]:
        prey = nearest(a, self.prey)
        dx, dy = ((prey.x-a.x, prey.y-a.y) if prey else (0, 0))
        return [a.x/(SIZE-1)*2-1, a.y/(SIZE-1)*2-1, sign(dx), sign(dy),
                (abs(dx)+abs(dy))/SIZE if prey else 1.0, a.energy/18-0.5,
                len(self.prey)/12-0.5, 1.0 if prey and (abs(dx)+abs(dy) <= 1) else -1.0,
                len(self.obstacles)/60-0.5]

    def choose_action(self, agent: Agent, kind: str, index: int) -> int:
        if self.controller == "random" or agent.brain is None:
            return self.rng.randrange(len(ACTIONS))
        inputs = self.prey_inputs(agent) if kind == "presa" else self.predator_inputs(agent)
        outputs = agent.brain.forward(inputs)
        # La red da puntuaciones de acción; una máscara impide escoger movimientos contra paredes.
        candidates = []
        for i, (dx, dy) in enumerate(ACTIONS):
            nx, ny = agent.x + dx, agent.y + dy
            if 0 <= nx < SIZE and 0 <= ny < SIZE and (nx, ny) not in self.obstacles:
                candidates.append(i)
        chosen = max(candidates, key=lambda i: outputs[i]) if candidates else 0
        self.last_decisions.append({"tick": self.tick, "tipo": kind, "agente": index,
                                    "entradas": inputs, "salidas": outputs,
                                    "accion": ACTION_NAMES[chosen]})
        return chosen

    def step(self) -> None:
        self.last_decisions = []
        for kind, group in (("presa", self.prey), ("depredador", self.predators)):
            for i, a in enumerate(group):
                if not a.alive:
                    continue
                action = self.choose_action(a, kind, i)
                a.last_action = ACTION_NAMES[action]
                dx, dy = ACTIONS[action]
                nx, ny = a.x + dx, a.y + dy
                if 0 <= nx < SIZE and 0 <= ny < SIZE and (nx, ny) not in self.obstacles:
                    a.x, a.y = nx, ny
                a.energy -= 0.08 if kind == "presa" else 0.10
                if kind == "presa" and (a.x, a.y) in self.plants:
                    self.plants.remove((a.x, a.y)); a.energy += 4.0; a.score += 2.0; self.food_eaten += 1
                elif kind == "depredador":
                    victim = next((p for p in self.prey if p.alive and p.x == a.x and p.y == a.y), None)
                    if victim:
                        victim.alive = False; a.energy += 7.0; a.score += 8.0
                        self.captures += 1; self.capture_ticks.append(self.tick)
                if a.energy <= 0:
                    a.alive = False
        if self.tick % 12 == 0:
            free = [(x, y) for x in range(SIZE) for y in range(SIZE)
                    if (x, y) not in self.obstacles and (x, y) not in self.plants]
            if free and len(self.plants) < SCENARIOS[self.scenario]["plants"]:
                self.plants.add(self.rng.choice(free))
        self.tick += 1

    def run(self) -> EpisodeResult:
        while self.tick < self.max_ticks and any(p.alive for p in self.prey) and self.predators:
            self.step()
        return EpisodeResult(self.seed, self.scenario, self.controller, self.tick,
            sum(p.alive for p in self.prey), self.food_eaten, self.captures,
            round(sum(p.energy for p in self.prey if p.alive), 3),
            round(sum(p.energy for p in self.predators if p.alive), 3),
            round(sum(self.capture_ticks)/len(self.capture_ticks), 2) if self.capture_ticks else None)


def new_brain(kind: str, rng: random.Random, hidden: tuple[int, ...] = HIDDEN) -> NeuralNetwork:
    return NeuralNetwork(((PREY_INPUTS if kind == "presa" else PREDATOR_INPUTS), *hidden, len(ACTIONS)), rng)


def mutate(parent: NeuralNetwork, rng: random.Random, rate: float = 0.12, scale: float = 0.25) -> NeuralNetwork:
    genes = [g + rng.gauss(0, scale) if rng.random() < rate else g for g in parent.genes]
    return NeuralNetwork(parent.sizes, rng, genes)


def train_species(kind: str, generations: int = 8, population_size: int = 10,
                  episodes_per_brain: int = 2, scenario: str = "abundancia", seed: int = 71,
                  hidden: tuple[int, ...] = HIDDEN) -> NeuralNetwork:
    """Neuroevolución elitista: selecciona por supervivencia/energía o capturas."""
    rng = random.Random(seed)
    population = [new_brain(kind, rng, hidden) for _ in range(population_size)]
    initial_genes = list(population[0].genes)
    fitness_history = []
    for generation in range(generations):
        ranked = []
        for brain_i, brain in enumerate(population):
            outcomes = []
            for rep in range(episodes_per_brain):
                episode_seed = seed + generation*100_000 + brain_i*100 + rep
                brains = [brain] * (12 if kind == "presa" else 0)
                predators = [brain] * 2 if kind == "depredador" else None
                world = Ecosystem(episode_seed, scenario, prey_brains=brains if kind == "presa" else None,
                                  predator_brains=predators, prey_count=12, max_ticks=150)
                result = world.run()
                outcomes.append((result.prey_survived * 6 + result.prey_energy_end * 0.4 + result.food_eaten * 0.2)
                                if kind == "presa" else (result.captures * 8 + result.predator_energy_end * 0.5))
            ranked.append((sum(outcomes)/len(outcomes), brain))
        ranked.sort(key=lambda row: row[0], reverse=True)
        fitness_history.append(round(ranked[0][0], 4))
        print(f"{kind.capitalize()} generación {generation+1}/{generations}: mejor aptitud {ranked[0][0]:.2f}")
        keep = max(2, population_size // 4)
        parents = [brain for _, brain in ranked[:keep]]
        population = parents[:]
        while len(population) < population_size:
            population.append(mutate(rng.choice(parents), rng))
    winner = ranked[0][1]
    winner.training_evidence = {
        "best_fitness_by_generation": fitness_history,
        "parameters_changed_vs_first_initial_candidate": sum(a != b for a, b in zip(initial_genes, winner.genes)),
    }
    return winner


def save_brain(path: Path, brain: NeuralNetwork, species: str, seed: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"species": species, "seed": seed,
        "training_evidence": getattr(brain, "training_evidence", {}),
        "brain": brain.to_dict()}, indent=2), encoding="utf-8")


def load_brain(path: Path) -> NeuralNetwork:
    return NeuralNetwork.from_dict(json.loads(path.read_text(encoding="utf-8"))["brain"])


def save_results(path: Path, rows: list[EpisodeResult]) -> None:
    import csv
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)
