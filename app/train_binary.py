import os
import json
import copy
import argparse
from pathlib import Path
from tqdm import tqdm

import torch
from torch import nn, optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, WeightedRandomSampler

def get_model(name, n_classes, pretrained=True):
    if name == "resnet18":
        model = models.resnet18(weights='DEFAULT' if pretrained else None)
        for param in model.parameters():
            param.requires_grad = False

        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, n_classes)
        
    elif name == "mobilenet_v2":
        model = models.mobilenet_v2(weights='DEFAULT' if pretrained else None)
        for param in model.parameters():
            param.requires_grad = False
        num_ftrs = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(num_ftrs, n_classes)
    else:
        raise ValueError("Unknown model: " + name)
    return model

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="dataset/binary_data", help="Path to data directory")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--model", choices=["resnet18","mobilenet_v2"], default="resnet18")
    parser.add_argument("--no-gpu", action="store_true")
    parser.add_argument("--out", default="binary_model_ts.pt")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() and not args.no_gpu else "cpu")
    print(f"--- Odpalam trening na: {device} ---")

    train_tf = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(0.1, 0.1, 0.1, 0.05),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    val_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    train_ds = datasets.ImageFolder(os.path.join(args.data_dir, "train"), train_tf)
    val_ds = datasets.ImageFolder(os.path.join(args.data_dir, "val"), val_tf)

    targets = train_ds.targets
    class_count = [targets.count(i) for i in range(len(train_ds.classes))]
    class_weights = 1. / torch.tensor(class_count, dtype=torch.float)
    samples_weights = class_weights[targets]
    sampler = WeightedRandomSampler(weights=samples_weights, num_samples=len(samples_weights), replacement=True)

    train_loader = DataLoader(train_ds, batch_size=args.batch, sampler=sampler, num_workers=4)
    val_loader = DataLoader(val_ds, batch_size=args.batch, shuffle=False, num_workers=4)

    model = get_model(args.model, len(train_ds.classes))
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-4)

    best_acc = 0.0
    best_wts = copy.deepcopy(model.state_dict())

    for epoch in range(args.epochs):
        print(f"\nEpoka {epoch+1}/{args.epochs}")
        for phase in ["train", "val"]:
            model.train() if phase == "train" else model.eval()
            loader = train_loader if phase == "train" else val_loader
            
            running_loss, running_corrects, total = 0.0, 0, 0
            
            loop = tqdm(loader, desc=f"{phase.capitalize()}")
            for inputs, labels in loop:
                inputs, labels = inputs.to(device), labels.to(device)
                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == "train"):
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)
                    _, preds = torch.max(outputs, 1)

                    if phase == "train":
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data).item()
                total += inputs.size(0)
                loop.set_postfix(acc=(running_corrects/total))

            epoch_acc = running_corrects / total
            if phase == "val" and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_wts = copy.deepcopy(model.state_dict())

    print(f"\nTrening zakończony! Najlepsza celność: {best_acc:.4f}")

    model.load_state_dict(best_wts)
    model.eval()

    example = torch.randn(1, 3, 224, 224).to(device)
    traced = torch.jit.trace(model.cpu(), example.cpu())
    traced.save(args.out)
    
    with open("binary_classes.json", "w", encoding="utf-8") as f:
        json.dump(train_ds.classes, f, ensure_ascii=False, indent=2)

    print(f"Model zapisany jako: {args.out}")

if __name__ == "__main__":
    main()