def evaluate_item(item, user_profile, type_):
    score = 0
    if hasattr(item, 'categories') and user_profile.categories and item.categories:
        if set(user_profile.categories) & set(item.categories):
            score -= 2
    if hasattr(item, 'level') and user_profile.current_level and item.level:
        if item.level > user_profile.current_level:
            score += 2
        elif item.level == user_profile.current_level:
            score += 1
    if hasattr(item, 'frequency') and item.frequency:
        score += max(0, 10 - item.frequency)
    if type_ == 'word':
        score += getattr(item, 'component_count', 0) + getattr(item, 'value_count', 0)
    elif type_ == 'phrase':
        score += getattr(item, 'word_count', 0) + getattr(item, 'value_count', 0)
    elif type_ == 'group':
        score += getattr(item, 'member_count', 0)
    return score

def genetic_algorithm(user, db, population_size=30, generations=10, set_size=20):
    from app import models
    user_profile = user.profile
    if user_profile is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="User profile is not set. Please fill in your profile before generating a study set.")
    active_reviews = db.query(models.UserCardReview).filter_by(user_id=user.id, is_review=True).all()
    reviewed_word_ids = set(r.item_id for r in active_reviews if r.item_type == 'word')
    reviewed_phrase_ids = set(r.item_id for r in active_reviews if r.item_type == 'phrase')
    reviewed_group_ids = set(r.item_id for r in active_reviews if r.item_type == 'group')
    words = {w.id: w for w in db.query(models.Word).filter(~models.Word.id.in_(reviewed_word_ids)).all()}
    phrases = {p.id: p for p in db.query(models.Phrase).filter(~models.Phrase.id.in_(reviewed_phrase_ids)).all()}
    groups = {g.id: g for g in db.query(models.SemanticGroup).filter(~models.SemanticGroup.id.in_(reviewed_group_ids)).all()}
    n_words = int(set_size * 0.4)
    n_phrases = int(set_size * 0.4)
    n_groups = set_size - n_words - n_phrases
    import random
    population = []
    for _ in range(population_size):
        word_ids = random.sample(list(words.keys()), min(n_words, len(words)))
        phrase_ids = random.sample(list(phrases.keys()), min(n_phrases, len(phrases)))
        group_ids = random.sample(list(groups.keys()), min(n_groups, len(groups)))
        population.append((word_ids, phrase_ids, group_ids))
    for _ in range(generations):
        scored = []
        for word_ids, phrase_ids, group_ids in population:
            score = sum(evaluate_item(words[wid], user_profile, 'word') for wid in word_ids)
            score += sum(evaluate_item(phrases[pid], user_profile, 'phrase') for pid in phrase_ids)
            score += sum(evaluate_item(groups[gid], user_profile, 'group') for gid in group_ids)
            scored.append((score, word_ids, phrase_ids, group_ids))
        scored.sort(key=lambda x: x[0])
        survivors = scored[:population_size//2]
        new_population = []
        for _ in range(population_size):
            parent1 = random.choice(survivors)
            parent2 = random.choice(survivors)
            def crossover(a, b, n, pool):
                cut = random.randint(1, n-1) if n > 1 else 1
                child = list(set(a[:cut] + b[cut:]))
                if random.random() < 0.2:
                    if random.random() < 0.5 and len(child) > 1:
                        child.pop(random.randint(0, len(child)-1))
                    else:
                        available = set(pool) - set(child)
                        if available:
                            child.append(random.choice(list(available)))
                while len(child) > n:
                    child.pop(random.randint(0, len(child)-1))
                available = set(pool) - set(child)
                while len(child) < n and available:
                    child.append(random.choice(list(available)))
                    available = set(pool) - set(child)
                return list(set(child))
            child_word_ids = crossover(parent1[1], parent2[1], n_words, words.keys())
            child_phrase_ids = crossover(parent1[2], parent2[2], n_phrases, phrases.keys())
            child_group_ids = crossover(parent1[3], parent2[3], n_groups, groups.keys())
            new_population.append((child_word_ids, child_phrase_ids, child_group_ids))
        population = new_population
    best = min(population, key=lambda ids: (
        sum(evaluate_item(words[wid], user_profile, 'word') for wid in ids[0]) +
        sum(evaluate_item(phrases[pid], user_profile, 'phrase') for pid in ids[1]) +
        sum(evaluate_item(groups[gid], user_profile, 'group') for gid in ids[2])
    ))
    return best[0], best[1], best[2] 