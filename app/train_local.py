import json
import copy
import random
import argparse
from dataclasses import dataclass, fields
from pathlib import Path
from typing import List, Tuple, Callable
from tqdm import tqdm

import torch
from torch import nn, optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader

IMAGE_SIZE = 224
RESIZE_SIZE = 256
NORMALIZE_MEAN = [0.485, 0.456, 0.406]
NORMALIZE_STD = [0.229, 0.224, 0.225]
NUM_WORKERS = 4


@dataclass
class HyperParams:
    learning_rate: float
    batch_size: int
    jitter_brightness: float
    jitter_contrast: float
    jitter_saturation: float
    jitter_hue: float
    flip_prob: float
    freeze_backbone: bool


@dataclass
class Individual:
    params: HyperParams
    fitness: float
    state: dict


def create_model(name: str, n_classes: int) -> nn.Module:
    if name == "resnet18":
        model = models.resnet18(pretrained=True)
        model.fc = nn.Linear(model.fc.in_features, n_classes)
    elif name == "mobilenet_v2":
        model = models.mobilenet_v2(pretrained=True)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, n_classes)
    else:
        raise ValueError(f"Unknown model: {name}")
    return model


def get_transforms(params: HyperParams) -> transforms.Compose:
    return transforms.Compose([
        transforms.RandomResizedCrop(IMAGE_SIZE),
        transforms.RandomHorizontalFlip(p=params.flip_prob),
        transforms.ColorJitter(
            params.jitter_brightness,
            params.jitter_contrast,
            params.jitter_saturation,
            params.jitter_hue
        ),
        transforms.ToTensor(),
        transforms.Normalize(NORMALIZE_MEAN, NORMALIZE_STD)
    ])


def train_model(
    params: HyperParams,
    model_name: str,
    n_classes: int,
    device: torch.device,
    data_dir: Path,
    epochs: int
) -> nn.Module:
    train_tf = get_transforms(params)
    train_ds = datasets.ImageFolder(str(data_dir / "train"), train_tf)
    train_loader = DataLoader(train_ds, batch_size=params.batch_size, shuffle=True, num_workers=NUM_WORKERS)

    model = create_model(model_name, n_classes)
    if params.freeze_backbone:
        for name, param in model.named_parameters():
            if "fc" not in name and "classifier.1" not in name:
                param.requires_grad = False
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=params.learning_rate)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=2, gamma=0.5)

    for epoch in range(epochs):
        model.train()
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            loss = criterion(model(inputs), labels)
            loss.backward()
            optimizer.step()
        scheduler.step()

    return model


def evaluate_model(model: nn.Module, data_dir: Path, device: torch.device) -> float:
    val_tf = transforms.Compose([
        transforms.Resize(RESIZE_SIZE),
        transforms.CenterCrop(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(NORMALIZE_MEAN, NORMALIZE_STD)
    ])
    val_ds = datasets.ImageFolder(str(data_dir / "val"), val_tf)
    val_loader = DataLoader(val_ds, batch_size=32, shuffle=False, num_workers=NUM_WORKERS)

    model.eval()
    correct = total = 0
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            preds = torch.max(model(inputs), 1)[1]
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    return correct / total if total > 0 else 0.0


def train_and_evaluate(
    params: HyperParams,
    model_name: str,
    n_classes: int,
    device: torch.device,
    data_dir: Path,
    epochs: int
) -> Tuple[float, dict]:
    model = train_model(params, model_name, n_classes, device, data_dir, epochs)
    fitness = evaluate_model(model, data_dir, device)
    return fitness, copy.deepcopy(model.state_dict())


def random_hyperparams() -> HyperParams:
    return HyperParams(
        learning_rate=10**random.uniform(-4, -2),
        batch_size=random.choice([16, 32, 64]),
        jitter_brightness=random.uniform(0.0, 0.4),
        jitter_contrast=random.uniform(0.0, 0.4),
        jitter_saturation=random.uniform(0.0, 0.4),
        jitter_hue=random.uniform(0.0, 0.1),
        flip_prob=random.uniform(0.0, 1.0),
        freeze_backbone=random.choice([True, False])
    )


def crossover(p1: HyperParams, p2: HyperParams) -> HyperParams:
    kwargs = {}
    for field in fields(HyperParams):
        value = p1 if random.random() < 0.5 else p2
        kwargs[field.name] = getattr(value, field.name)
    return HyperParams(**kwargs)


def mutate(params: HyperParams, mutation_rate: float = 0.3) -> HyperParams:
    kwargs = {}
    for field in fields(HyperParams):
        value = getattr(params, field.name)
        if random.random() < mutation_rate:
            if field.name == "learning_rate":
                kwargs[field.name] = max(1e-6, value * 10**random.uniform(-0.5, 0.5))
            elif field.name == "batch_size":
                kwargs[field.name] = random.choice([16, 32, 64])
            elif field.name == "jitter_hue":
                kwargs[field.name] = random.uniform(0.0, 0.1)
            elif field.name == "flip_prob":
                kwargs[field.name] = random.uniform(0.0, 1.0)
            elif field.name == "freeze_backbone":
                kwargs[field.name] = not value
            else:
                kwargs[field.name] = random.uniform(0.0, 0.4)
        else:
            kwargs[field.name] = value
    return HyperParams(**kwargs)


def initialize_population(size: int) -> List[Individual]:
    return [Individual(params=random_hyperparams(), fitness=0.0, state={}) for _ in range(size)]


def run_evolution(
    population: List[Individual],
    generations: int,
    elite_ratio: float,
    model_name: str,
    classes: List[str],
    device: torch.device,
    data_dir: Path,
    epochs: int
) -> Tuple[float, dict, HyperParams]:
    best_acc = 0.0
    best_state = None
    best_params = None

    for gen in range(generations):
        print(f"\nGeneration {gen + 1}/{generations}")

        for i, ind in enumerate(tqdm(population, desc="Training")):
            fitness, state = train_and_evaluate(ind.params, model_name, len(classes), device, data_dir, epochs)
            ind.fitness = fitness
            ind.state = state

            if fitness > best_acc:
                best_acc = fitness
                best_state = copy.deepcopy(state)
                best_params = copy.deepcopy(ind.params)
                torch.save({
                    "model_state": best_state,
                    "classes": classes,
                    "hyperparams": best_params
                }, "dataset/torch/best_model.pth")
            tqdm.write(f"Individual {i + 1}: Acc={fitness:.4f}, LR={ind.params.learning_rate:.5f}")

        population.sort(key=lambda x: x.fitness, reverse=True)
        avg = sum(ind.fitness for ind in population) / len(population)
        print(f"Best: {population[0].fitness:.4f}, Avg: {avg:.4f}, Best LR: {best_params.learning_rate:.5f}")

        if gen < generations - 1:
            n_elite = max(1, int(elite_ratio * len(population)))
            elites = population[:n_elite]
            new_pop = elites.copy()
            while len(new_pop) < len(population):
                p1, p2 = random.sample(elites, 2)
                child_params = mutate(crossover(p1.params, p2.params))
                new_pop.append(Individual(params=child_params, fitness=0.0, state={}))
            population = new_pop

    return best_acc, best_state, best_params


def save_final_model(state: dict, classes: List[str], model_name: str, device: torch.device, output_path: str) -> None:
    model = create_model(model_name, len(classes))
    model.load_state_dict(state)
    model = model.to(device)
    model.eval()

    torch_dir = Path("dataset/torch")
    torch_dir.mkdir(parents=True, exist_ok=True)
    torch.save(state, torch_dir / "monster_resnet_state_dict.pth")

    classes_path = Path("dataset/json/classes.json")
    classes_path.parent.mkdir(parents=True, exist_ok=True)
    with open(classes_path, "w", encoding="utf-8") as f:
        json.dump(classes, f, ensure_ascii=False, indent=2)

    example = torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE).to(device)
    traced = torch.jit.trace(model.cpu(), example.cpu())

    torch_path = Path(output_path)
    torch_path.parent.mkdir(parents=True, exist_ok=True)
    traced.save(output_path)
    print(f"Saved TorchScript model to {output_path}")
    print(f"Saved classes.json to {classes_path}")
    print(f"Saved state dict to {torch_dir / 'monster_resnet_state_dict.pth'}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="dataset/data")
    parser.add_argument("--generations", type=int, default=10)
    parser.add_argument("--population-size", type=int, default=8)
    parser.add_argument("--model", choices=["resnet18", "mobilenet_v2"], default="resnet18")
    parser.add_argument("--no-gpu", action="store_true")
    parser.add_argument("--out", default="dataset/torch/monster_model_ts.pt")
    parser.add_argument("--elite-ratio", type=float, default=0.25)
    parser.add_argument("--train-epochs", type=int, default=3)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() and not args.no_gpu else "cpu")
    data_dir = Path(args.data_dir)
    train_ds = datasets.ImageFolder(str(data_dir / "train"), transforms.ToTensor())
    classes = train_ds.classes
    print(f"Using device: {device}, Classes: {classes}")

    population = initialize_population(args.population_size)
    best_acc, best_state, best_params = run_evolution(
        population, args.generations, args.elite_ratio,
        args.model, classes, device, data_dir, args.train_epochs
    )

    print(f"\nBest accuracy: {best_acc:.4f}")
    print(f"Best hyperparameters: LR={best_params.learning_rate:.5f}, Batch={best_params.batch_size}, "
          f"Freeze={best_params.freeze_backbone}")
    save_final_model(best_state, classes, args.model, device, args.out)


if __name__ == "__main__":
    main()
