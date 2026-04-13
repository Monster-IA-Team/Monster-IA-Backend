from PIL import Image
from torchvision import transforms
from dto.response.prediction_res import PredictionResponse
from dto.response.class_cofidence_res import ClassConfidenceResponse
import os, torch, json, io

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_TORCH_DIR = os.path.join(CURRENT_DIR, '..', 'dataset', 'torch')
DATASET_JSON_DIR = os.path.join(CURRENT_DIR, '..', 'dataset', 'json')

class PredictionService:
    def __init__(self,
                 model_path: str = os.path.join(DATASET_TORCH_DIR, "monster_model_ts.pt"),
                 classes_path: str = os.path.join(DATASET_JSON_DIR, "classes.json")):
        
        with open(classes_path, 'r', encoding="utf-8") as f:
            self.classes = json.load(f)
        
        self.model = torch.jit.load(model_path, map_location=torch.device('cpu'))
        self.model.eval()
        
        self.tf = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
    def read_img(self, img_bytes: bytes) -> Image.Image:
        return Image.open(io.BytesIO(img_bytes)).convert('RGB')
    
    def predict(self, img_bytes: bytes) -> PredictionResponse:
        img = self.read_img(img_bytes)
        img_t = self.tf(img).unsqueeze(0)
        
        with torch.no_grad():
            out = self.model(img_t)
            
            if out.dim() == 1:
                out = out.unsqueeze(0)
                
            probs = torch.nn.functional.softmax(out, dim=1).squeeze()
            conf_val, idx_val = torch.max(probs, dim=0)
            best_label = self.classes[idx_val.item()]
            best_conf = float(conf_val.item())
            
            preds = []
            for i, p in enumerate(probs.tolist()):
                preds.append(ClassConfidenceResponse(
                    class_name=self.classes[i],
                    confidence=float(p)
                ))
            
            preds_sorted = sorted(preds, key=lambda x: x.confidence, reverse=True)
            
        return PredictionResponse(
            label = best_label,
            confidence = best_conf,
            prediction = preds_sorted,
            num_classes = len(self.classes)
        )