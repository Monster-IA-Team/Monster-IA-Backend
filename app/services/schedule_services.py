import random, json, os
from datetime import time
from typing import List, Tuple

from dto.request.schedule_req import ScheduleRequest
from dto.response.schedule_res import ScheduleResponse
from dto.response.drink_session_res import DrinkSessionResponse

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(CURRENT_DIR, "..", "dataset", "json", "ga_config.json")

INVALID_FITNESS = -9999.0


class TimeConverter:
    @staticmethod
    def to_float(t: time) -> float:
        return t.hour + t.minute / 60.0

    @staticmethod
    def from_float(f_time: float) -> time:
        f_time = f_time % 24.0
        hour = int(f_time)
        minute = int(round((f_time - hour) * 60))
        if minute == 60:
            hour += 1
            minute = 0
        if hour == 24:
            hour = 0
        return time(hour=hour, minute=minute)


class IntervalUtils:
    @staticmethod
    def overlap_length(start_a: float, end_a: float, start_b: float, end_b: float) -> float:
        return max(0.0, min(end_a, end_b) - max(start_a, start_b))

    @staticmethod
    def merge(intervals: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        if not intervals:
            return []
        intervals.sort()
        merged = [intervals[0]]
        for start, end in intervals[1:]:
            last_start, last_end = merged[-1]
            if start <= last_end:
                merged[-1] = (last_start, max(last_end, end))
            else:
                merged.append((start, end))
        return merged


class GeneticAlgorithm:
    def __init__(self, min_effect: float, max_effect: float, min_gap: float,
                 overlap_penalty: float, buffer_hours: float,
                 population_size: int, generations: int):
        self.min_effect = min_effect
        self.max_effect = max_effect
        self.min_gap = min_gap
        self.overlap_penalty = overlap_penalty
        self.buffer_hours = buffer_hours
        self.population_size = population_size
        self.generations = generations
        self.tournament_size = 3
        self.elite_count = max(1, population_size // 10)
        self.crossover_rate = 0.8
        self.mutation_rate = 0.2
        self.gaussian_std = 0.3

    def _is_valid_individual(self, individual: List[Tuple[float, float]],
                             wake_float: float, sleep_float: float) -> bool:
        for start, effect in individual:
            end = start + effect
            if start < wake_float or end > sleep_float or end > sleep_float - self.buffer_hours:
                return False
        starts = sorted(s for s, _ in individual)
        return all(starts[i + 1] - starts[i] >= self.min_gap
                   for i in range(len(starts) - 1))

    def _calculate_fitness(self, individual: List[Tuple[float, float]],
                           wake_float: float, sleep_float: float,
                           task_intervals: List[Tuple[float, float]]) -> float:
        if not self._is_valid_individual(individual, wake_float, sleep_float):
            return INVALID_FITNESS

        intervals = [(start, start + effect) for start, effect in individual]
        penalty = sum(
            IntervalUtils.overlap_length(interval_a[0], interval_a[1], interval_b[0], interval_b[1]) * self.overlap_penalty
            for idx_a, interval_a in enumerate(intervals)
            for interval_b in intervals[idx_a + 1:]
        )
        merged_intervals = IntervalUtils.merge(intervals)
        covered = sum(
            IntervalUtils.overlap_length(interval_start, interval_end, task_start, task_end)
            for task_start, task_end in task_intervals
            for interval_start, interval_end in merged_intervals
        )
        return covered - penalty

    def _create_individual(self, monster_count: int, wake_float: float,
                           sleep_float: float) -> List[Tuple[float, float]]:
        individual = []
        prev_start = wake_float
        for _ in range(monster_count):
            min_start = max(wake_float, prev_start + self.min_gap)
            max_start = sleep_float - self.max_effect - self.buffer_hours
            if min_start <= max_start:
                start = random.uniform(min_start, max_start)
            else:
                start = random.uniform(wake_float, sleep_float - self.max_effect)
            effect = random.uniform(self.min_effect, self.max_effect)
            individual.append((start, effect))
            prev_start = start
        return individual

    def _tournament_selection(self, population: List, fitness_scores: List[float]) -> List:
        contestants = random.sample(list(zip(population, fitness_scores)), self.tournament_size)
        return max(contestants, key=lambda x: x[1])[0]

    def _crossover(self, parent_a: List, parent_b: List, monster_count: int) -> Tuple[List, List]:
        if random.random() > self.crossover_rate or monster_count <= 1:
            return parent_a[:], parent_b[:]
        point = random.randint(1, monster_count - 1)
        return parent_a[:point] + parent_b[point:], parent_b[:point] + parent_a[point:]

    def _mutate(self, individual: List[Tuple[float, float]], wake_float: float,
                sleep_float: float, monster_count: int, mutation_rate: float) -> List[Tuple[float, float]]:
        mutated = []
        for i, (start, effect) in enumerate(individual):
            if random.random() < mutation_rate:
                start += random.gauss(0, self.gaussian_std)
            if random.random() < mutation_rate:
                effect += random.gauss(0, self.gaussian_std)

            start = max(wake_float, min(start, sleep_float - self.max_effect))
            effect = max(self.min_effect, min(effect, self.max_effect))

            if i > 0:
                start = max(start, mutated[-1][0] + self.min_gap)
            if start + effect > sleep_float - self.buffer_hours:
                effect = max(self.min_effect, sleep_float - self.buffer_hours - start)

            mutated.append((start, effect))
        return mutated

    def run(self, wake_float: float, sleep_float: float,
            task_intervals: List[Tuple[float, float]], monster_count: int) -> Tuple[List[Tuple[float, float]], float]:
        population = [self._create_individual(monster_count, wake_float, sleep_float)
                      for _ in range(self.population_size)]

        current_mutation_rate = self.mutation_rate
        for gen in range(self.generations):
            fitness_scores = [self._calculate_fitness(ind, wake_float, sleep_float, task_intervals)
                              for ind in population]

            sorted_indices = sorted(range(len(population)),
                                    key=lambda i: fitness_scores[i], reverse=True)
            elite = [population[i] for i in sorted_indices[:self.elite_count]]

            new_population = elite[:]
            while len(new_population) < self.population_size:
                parent_a = self._tournament_selection(population, fitness_scores)
                parent_b = self._tournament_selection(population, fitness_scores)
                child_a, child_b = self._crossover(parent_a, parent_b, monster_count)
                child_a = self._mutate(child_a, wake_float, sleep_float, monster_count, current_mutation_rate)
                child_b = self._mutate(child_b, wake_float, sleep_float, monster_count, current_mutation_rate)
                new_population.append(child_a)
                if len(new_population) < self.population_size:
                    new_population.append(child_b)

            population = new_population[:self.population_size]
            current_mutation_rate = max(0.05, 0.2 * (1 - gen / self.generations))

        fitness_scores = [self._calculate_fitness(ind, wake_float, sleep_float, task_intervals)
                          for ind in population]
        best_index = max(range(len(population)), key=lambda i: fitness_scores[i])
        return population[best_index], max(0.0, fitness_scores[best_index])


class ScheduleService:
    def __init__(self, config_path: str = CONFIG_PATH):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        self._ga = GeneticAlgorithm(
            min_effect=config["min_effect_hours"],
            max_effect=config["max_effect_hours"],
            min_gap=config["min_gap_hours"],
            overlap_penalty=config["overlap_penalty"],
            buffer_hours=config["buffer_hours"],
            population_size=config["population_size"],
            generations=config["generations"]
        )

    def _build_task_intervals(self, req: ScheduleRequest, wake_float: float,
                               sleep_float: float) -> Tuple[List[Tuple[float, float]], float]:
        task_intervals = []
        for task in req.tasks:
            task_start = TimeConverter.to_float(task.start)
            task_end = TimeConverter.to_float(task.end)
            if task_start < wake_float and sleep_float > 24.0:
                task_start += 24.0
            if task_end < task_start:
                task_end += 24.0
            task_intervals.append((task_start, task_end))
        total_task_hours = sum(te - ts for ts, te in task_intervals)
        return task_intervals, total_task_hours

    def calculate_schedule(self, req: ScheduleRequest) -> ScheduleResponse:
        wake_float = TimeConverter.to_float(req.wake)
        sleep_float = TimeConverter.to_float(req.sleep)
        if sleep_float <= wake_float:
            sleep_float += 24.0

        task_intervals, total_task_hours = self._build_task_intervals(req, wake_float, sleep_float)

        best, covered_hours = self._ga.run(wake_float, sleep_float, task_intervals, req.monster_count)

        ratio = covered_hours / total_task_hours if total_task_hours > 0 else 0.0
        effectiveness = round(min(1.0, ratio) * 9 + 1)

        sessions = [
            DrinkSessionResponse(start=TimeConverter.from_float(start), end=int(round(effect)))
            for start, effect in sorted(best, key=lambda x: x[0])
        ]
        return ScheduleResponse(drink_sessions=sessions,
                               covered_hours=int(round(covered_hours)),
                               effectiveness=effectiveness)
