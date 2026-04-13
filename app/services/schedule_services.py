import random, json, os
from datetime import time
from dto.request.schedule_req import ScheduleRequest
from dto.response.schedule_res import ScheduleResponse
from dto.response.drink_session_res import DrinkSessionResponse
from dto.request.task_interval_req import TaskIntervalRequest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(CURRENT_DIR, "..", "dataset", "json", "ga_config.json")

class ScheduleService:
    def __init__(self, config_path: str = CONFIG_PATH):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    
        self.min_effect = config["min_effect_hours"]
        self.max_effect = config["max_effect_hours"]
        self.min_gap = config["min_gap_hours"]
        self.overlap_penalty = config["overlap_penalty"]
        self.late_penalty = config["late_penalty"]
        self.buffer_hours = config["buffer_hours"]
        self.population_size = config["population_size"]
        self.generations = config["generations"]
        
    @staticmethod
    def time_to_float(t: time) -> float:
        return t.hour + t.minute / 60.0

    @staticmethod
    def float_to_time(f_time: float) -> time:
        f_time = f_time % 24.0
        hour = int(f_time)
        minute = int(round((f_time - hour) * 60))
        
        if minute == 60:
            hour += 1
            minute = 0
            
        if hour == 24:
            hour = 0
            
        return time(hour=hour, minute=minute)
    
    @staticmethod
    def overlap_length(a_start, a_end, b_start, b_end):
        return max(0.0, min(a_end, b_end) - max(a_start, b_start))
    
    @staticmethod
    def merge_intervals(intervals):
        if not intervals:
            return []
        
        intervals.sort()
        merged = [intervals[0]]
        
        for start, end, in intervals[1:]:
            last_start, last_end = merged[-1]
            if start <= last_end:
                merged[-1] = (last_start, max(last_end, end))
            else:
                merged.append((start, end))
        
        return merged
    
    def calculate_schedule(self, req: ScheduleRequest) -> ScheduleResponse:
        wake_f = self.time_to_float(req.wake)
        sleep_f = self.time_to_float(req.sleep)
        
        if sleep_f <= wake_f:
            sleep_f += 24.0
        
        task_f = []
        
        for t in req.tasks:
            start_f = self.time_to_float(t.start)
            end_f = self.time_to_float(t.end)
            
            if start_f < wake_f and sleep_f > 24.0:
                start_f += 24.0
            
            if end_f < start_f:
                end_f += 24.0
                
            task_f.append((start_f, end_f))
            
        def random_individual():
            individual = []
            
            for _ in range(req.monster_count):
                start = random.uniform(wake_f, sleep_f - self.max_effect)
                effect = random.uniform(self.min_effect, self.max_effect)
                individual.append((start, effect))
            
            return individual
        
        def fitness(individual):
            intervals = []
            for (start, effect) in individual:
                end = start + effect
                
                if start < wake_f or end > sleep_f:
                    return -9999.0
                
                if end > sleep_f - self.buffer_hours:
                    return -9999.0
                
                intervals.append((start, end))
            
            starts = sorted(start for start, _ in individual)
            
            for i in range(len(starts) - 1):
                if starts[i + 1] - starts[i] < self.min_gap:
                    return -9999.0
                
            penalty = 0.0
            
            for i in range(len(intervals)):
                for j in range(i+1, len(intervals)):
                    overlap = self.overlap_length(
                        intervals[i][0], intervals[i][1],
                        intervals[j][0], intervals[j][1]
                    )
                    
                    penalty += overlap * self.overlap_penalty
                
            merged_intervals = self.merge_intervals(intervals)
            covered = 0.0
             
            for ts, te in task_f:
                for s, e in merged_intervals:
                    covered += self.overlap_length(s, e, ts, te)
            
            return covered - penalty
        
        population = [random_individual() for _ in range(self.population_size)]
        
        for _ in range(self.generations):
            scored = sorted(
                ((fitness(ind), ind) for ind in population), 
                reverse=True, 
                key=lambda x: x[0]
                )
            
            survivors = [ind for _, ind in scored[: max(1, self.population_size // 2)]]
            childern = []
            
            while len(childern) + len(survivors) < self.population_size:
                p1, p2 = random.choice(survivors), random.choice(survivors)
                child = []
                
                for m in range(req.monster_count):
                    s1, e1 = p1[m]
                    s2, e2 = p2[m]
                    
                    start = (s1 + s2) / 2
                    effect = (e1 + e2) / 2
                    
                    if random.random() < 0.2:
                        start += random.uniform(-0.5, 0.5)
                        
                    if random.random() < 0.2:
                        effect += random.uniform(-0.5, 0.5)
                        
                    start = max(wake_f, min(start, sleep_f - self.max_effect))
                    effect = max(self.min_effect, min(effect, self.max_effect))
                    
                    child.append((start, effect))
                
                childern.append(child)
            
            population = survivors + childern
        
        best = max(population, key=lambda ind: fitness(ind))
        covered_hours = max(0.0, fitness(best))
        
        total_task_hours = sum(te - ts for ts, te in task_f)
        ratio = covered_hours / total_task_hours if total_task_hours > 0 else 0.0
        effectiveness = round(min(1.0, ratio) * 9 + 1)
        
        session = [
            DrinkSessionResponse(
                start = self.float_to_time(start),
                end = int(round(effect))
            )
            for (start, effect) in sorted(best, key=lambda x: x[0])
        ]
        
        return ScheduleResponse(
            drink_sessions = session,
            covered_hours = int(round(covered_hours)),
            effectiveness = effectiveness
        )