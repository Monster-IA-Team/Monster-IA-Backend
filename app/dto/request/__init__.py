def quiz_answare(answers: QuizAnswers):
    candidates = set(monster_list)
    
    shop_key = "Stacjonarnie" if answers.shop_type == 0 else "Online"
    node = tree.get("answers", {}).get(shop_key, {})
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
        
    final_results = sorted([c for c in candidates if c in monster_list])
    
    return final_results