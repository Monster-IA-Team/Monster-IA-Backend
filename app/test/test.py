import itertools
import os
import random
import sys
from datetime import time

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.append(APP_DIR)


from services.quiz_services import QuizService
from services.schedule_services import ScheduleService
from services.prediction_services import PredictionService

class MockQuizReq:
    def __init__(self, shop_type, is_zabka, high_budget, sugar_free, taste_preference):
        self.shop_type = shop_type
        self.is_zabka = is_zabka
        self.high_budget = high_budget
        self.sugar_free = sugar_free
        self.taste_preference = taste_preference


class MockTask:
    def __init__(self, start_h, end_h):
        self.start = time(hour=int(start_h) % 24, minute=int((start_h % 1) * 60))
        self.end = time(hour=int(end_h) % 24, minute=int((end_h % 1) * 60))


class MockScheduleReq:
    def __init__(self, wake_h, sleep_h, monster_count, tasks):
        self.wake = time(hour=int(wake_h) % 24, minute=0)
        self.sleep = time(hour=int(sleep_h) % 24, minute=0)
        self.monster_count = monster_count
        self.tasks = tasks

def test_expert_system():
    print("Rozpoczynam testowanie wszystkich ścieżek Systemu Eksperckiego...")

    json_dir = os.path.join(APP_DIR, "dataset", "json")
    quiz_service = QuizService(
        monster_path=os.path.join(json_dir, "monsters.json"),
        tree_path=os.path.join(json_dir, "tree.json")
    )

    shop_types = [0, 1]
    is_zabka_opts = [True, False]
    high_budget_opts = [True, False]
    sugar_free_opts = [True, False]
    taste_prefs = [0, 1, 2]
    all_combinations = list(
        itertools.product(shop_types, is_zabka_opts, high_budget_opts, sugar_free_opts, taste_prefs))

    results_lengths = []

    for combo in all_combinations:
        req = MockQuizReq(*combo)
        ans = quiz_service.get_answers(req)
        results_lengths.append(len(ans))

    empty_results = results_lengths.count(0)
    one_to_three = sum(1 for x in results_lengths if 1 <= x <= 3)
    more_than_three = sum(1 for x in results_lengths if x > 3)

    labels = ['Brak rekomendacji\n(Ślepa uliczka)', 'Wąska rekomendacja\n(1-3 puszki)', 'Szeroki wybór\n(>3 puszki)']
    sizes = [empty_results, one_to_three, more_than_three]

    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel")[0:3])
    plt.title(f'Skuteczność Drzewa Decyzyjnego\n(Analiza {len(all_combinations)} możliwych profili użytkownika)',
              fontsize=14)
    plt.savefig(os.path.join(CURRENT_DIR, 'real_expert_system_coverage.png'), dpi=300)
    plt.close()
    print("Zapisano: real_expert_system_coverage.png")


def test_genetic_algorithm():
    print("Rozpoczynam test ogólnej wydajności Algorytmu Genetycznego (50 losowych scenariuszy)...")
    schedule_service = ScheduleService()

    runs = 50
    effectiveness_scores = []
    total_task_hours_list = []

    for i in range(runs):
        wake_h = random.randint(5, 10)
        sleep_h = random.randint(21, 24)
        monster_count = random.randint(1, 3)

        num_tasks = random.randint(1, 3)
        tasks = []
        current_start = wake_h + 1
        daily_task_hours = 0

        for _ in range(num_tasks):
            if current_start >= sleep_h - 2:
                break

            start_h = random.randint(current_start, sleep_h - 2)
            duration = random.randint(2, 5)
            end_h = min(start_h + duration, sleep_h)

            tasks.append(MockTask(start_h, end_h))
            daily_task_hours += (end_h - start_h)
            current_start = end_h + 1

        if not tasks:
            tasks = [MockTask(wake_h + 2, wake_h + 5)]
            daily_task_hours = 3

        req = MockScheduleReq(
            wake_h=wake_h, sleep_h=sleep_h, monster_count=monster_count,
            tasks=tasks
        )

        res = schedule_service.calculate_schedule(req)
        effectiveness_scores.append(res.effectiveness)
        total_task_hours_list.append(daily_task_hours)

    plt.figure(figsize=(10, 6))
    sns.histplot(effectiveness_scores, bins=10, kde=True, color='purple')
    plt.axvline(np.mean(effectiveness_scores), color='red', linestyle='dashed', linewidth=2,
                label=f'Średnia: {np.mean(effectiveness_scores):.1f}')

    plt.title('Rozkład efektywności harmonogramu\n(50 losowych scenariuszy)', fontsize=14)
    plt.xlabel('Wyliczona efektywność (1-10)', fontsize=12)
    plt.ylabel('Liczba scenariuszy', fontsize=12)
    plt.legend()
    plt.tight_layout()

    hist_filename = os.path.join(CURRENT_DIR, 'real_genetic_robustness_hist.png')
    plt.savefig(hist_filename, dpi=300)
    plt.close()
    print(f"Zapisano: {os.path.basename(hist_filename)}")
    
    plt.figure(figsize=(10, 6))
    sns.regplot(x=total_task_hours_list, y=effectiveness_scores, color='orange', scatter_kws={'s': 50})

    plt.title('Wpływ zapracowania na wyniki algorytmu genetycznego', fontsize=14)
    plt.xlabel('Suma godzin nauki/pracy w ciągu dnia', fontsize=12)
    plt.ylabel('Osiągnięta efektywność (1-10)', fontsize=12)
    plt.ylim(0, 11)
    plt.tight_layout()

    scatter_filename = os.path.join(CURRENT_DIR, 'real_genetic_robustness_scatter.png')
    plt.savefig(scatter_filename, dpi=300)
    plt.close()
    print(f"Zapisano: {os.path.basename(scatter_filename)}")

def test_neural_network():
    print("Testuję Sieć Neuronową na prawdziwych plikach...")

    folder_path = os.path.join(CURRENT_DIR, "images")

    if not os.path.exists(folder_path):
        print(f"BŁĄD: Nie znaleziono folderu {folder_path}")
        return

    prediction_service = PredictionService()
    confidences = []
    filenames = []
    predictions = []

    for img_name in os.listdir(folder_path):
        if not img_name.endswith((".jpg", ".png", ".jpeg")):
            continue

        print(f"Predykcja dla: {img_name}...")
        with open(os.path.join(folder_path, img_name), "rb") as f:
            res = prediction_service.predict(f.read())
            confidences.append(res.confidence)
            filenames.append(img_name.split('.')[0].replace('_', ' ').title())
            predictions.append(res.label)

    if not confidences:
        print("Nie znaleziono zdjęć w folderze testowym.")
        return

    plt.figure(figsize=(12, 7))
    ax = sns.barplot(x=filenames, y=confidences, color='#2ca02c', edgecolor='black')

    for i, p in enumerate(ax.patches):
        predicted_text = predictions[i]
        text_color = 'red' if predicted_text == "This image does not contain a monster." else 'black'
        display_text = "Not a Monster" if predicted_text == "This image does not contain a monster." else predicted_text

        ax.annotate(f'Predykcja:\n{display_text}',
                    (p.get_x() + p.get_width() / 2., p.get_height() + 0.02),
                    ha='center', va='bottom', fontsize=10, color=text_color, fontweight='bold')

    plt.axhline(np.mean(confidences), color='red', linestyle='dashed',
                label=f'Średnia pewność: {np.mean(confidences):.2f}')

    plt.title('Pewność i trafność predykcji modelu (CNN) na zbiorze weryfikacyjnym', fontsize=14, pad=20)
    plt.ylim(0, 1.2)
    plt.ylabel('Pewność predykcji (0.0 - 1.0)', fontsize=12)
    plt.xlabel('Plik wejściowy', fontsize=12)
    plt.xticks(rotation=15)
    plt.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(os.path.join(CURRENT_DIR, 'real_neural_network_confidence.png'), dpi=300)
    plt.close()
    print("Zapisano: real_neural_network_confidence.png")


if __name__ == "__main__":
    test_expert_system()
    test_genetic_algorithm()
    test_neural_network()
    print("Wszystkie testy zakończone! Wykresy znajdują się w folderze app/test/")