import os
import json
import copy
import argparse
from pathlib import Path
from tqdm import tqdm

import torch
from torch import nn, optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader

def get_model(name, n_classes, pretrained=True):
    if name == "resnet18":
        model = models.resnet18(pretrained=pretrained)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, n_classes)
    elif name == "mobilenet_v2":
        model = models.mobilenet_v2(pretrained=pretrained)
        num_ftrs = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(num_ftrs, n_classes)
    else:
        raise ValueError("Unknown model: " + name)
    return model

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="dataset/binary_data", help="Path to data directory with train/ and val/")
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--model", choices=["resnet18","mobilenet_v2"], default="resnet18")
    parser.add_argument("--no-gpu", action="store_true", help="Force CPU")
    parser.add_argument("--out", default="binary_model_ts.pt") # Nowa nazwa wyjściowa
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    train_dir = data_dir / "train"
    val_dir = data_dir / "val"
    assert train_dir.exists() and val_dir.exists(), f"Train/val not found in {data_dir}"

    device = torch.device("cuda" if torch.cuda.is_available() and not args.no_gpu else "cpu")
    print("Using device:", device)

    train_tf = transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(0.2,0.2,0.2,0.05),
        transforms.ToTensor(),
        transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
    ])
    val_tf = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
    ])

    train_ds = datasets.ImageFolder(str(train_dir), train_tf)
    val_ds = datasets.ImageFolder(str(val_dir), val_tf)

    classes = train_ds.classes
    print("Classes (train folder order):", classes)

    train_loader = DataLoader(train_ds, batch_size=args.batch, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_ds, batch_size=args.batch, shuffle=False, num_workers=4)

    model = get_model(args.model, len(classes), pretrained=True)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-3)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.1)

    best_acc = 0.0
    best_wts = copy.deepcopy(model.state_dict())

    for epoch in range(args.epochs):
        print(f"Epoch {epoch+1}/{args.epochs}")
        for phase in ["train","val"]:
            model.train() if phase=="train" else model.eval()
            loader = train_loader if phase=="train" else val_loader

            running_loss = 0.0
            running_corrects = 0
            total = 0
            loop = tqdm(loader, desc=phase)
            for inputs, labels in loop:
                inputs = inputs.to(device)
                labels = labels.to(device)
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
                loop.set_postfix(loss=(running_loss/total), acc=(running_corrects/total))
            epoch_loss = running_loss / total
            epoch_acc = running_corrects / total
            print(f"{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}")
            if phase=="val" and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_wts = copy.deepcopy(model.state_dict())
                torch.save({'model_state': best_wts, 'classes': classes}, "binary_best_model.pth")
        scheduler.step()

    print("Best val Acc: {:.4f}".format(best_acc))
    model.load_state_dict(best_wts)

    with open("binary_classes.json", "w", encoding="utf-8") as f:
        json.dump(classes, f, ensure_ascii=False, indent=2)
    torch.save(model.state_dict(), "binary_resnet_state_dict.pth")

    model.eval()
    example = torch.randn(1,3,224,224).to(device)
    traced = torch.jit.trace(model.cpu(), example.cpu())
    traced.save(args.out)
    print("Saved TorchScript model to", args.out)
    print("Saved binary_classes.json")

if __name__ == "__main__":
    main()