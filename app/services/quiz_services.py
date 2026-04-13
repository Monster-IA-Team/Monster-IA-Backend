import json, os 
from dto.request.quiz_answers_req import QuizAnswersRequest


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(CURRENT_DIR, "..", "dataset")

class QuizService:
    def __init__(self, 
                 monster_path: str = os.path.join(DATASET_DIR, "monsters.json"), 
                 tree_path: str = os.path.join(DATASET_DIR, "tree.json")):
        with open(monster_path, "r", encoding="utf-8") as f_monsters:
            self.monster_list = json.load(f_monsters)
            
        with open(tree_path, "r", encoding="utf-8") as f_tree:
            self.tree = json.load(f_tree) 
    
    def get_answers(self, answers: QuizAnswersRequest) -> list[str]:
        candidates = set(self.monster_list)
        
        shop_key = "Stacjonarnie" if answers.shop_type == 0 else "Online"
        node = self.tree.get("answers", {}).get(shop_key, {})
        if "filter" in node:
            candidates = candidates.intersection(set(node["filter"]))
            
        if answers.shop_type == 0:
            sub_key = "Żabka" if answers.is_zabka else "inne"
        else:
            sub_key = "yes" if answers.high_budget else "no"
            
        node = node.get("answers", {}).get(sub_key, {})
        if "filter" in node:
            candidates = candidates.intersection(set(node["filter"]))
            
        sugar_key = "yes" if answers.sugar_free else "no"
        node = node.get("answers", {}).get(sugar_key, {})
        if "filter" in node:
            candidates = candidates.intersection(set(node["filter"]))
            
        taste_map = {0: "Słodki", 1: "Umiarkowany", 2: "Kwaśny"}
        taste_key = taste_map.get(answers.taste_preference, "Słodki")
        
        node = node.get("answers", {}).get(taste_key, {})
        if "filter" in node:
            candidates = candidates.intersection(set(node["filter"]))
            
        final_results = sorted([c for c in candidates if c in self.monster_list])
        
        return final_results