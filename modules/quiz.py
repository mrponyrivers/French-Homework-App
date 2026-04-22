from __future__ import annotations

import random


def build_mcq_quiz(vocab_items: list[dict], num_questions: int = 10) -> list[dict]:
    clean_items = []
    for item in vocab_items:
        term = (item.get("term") or "").strip()
        meaning = (item.get("meaning") or "").strip()
        notes = (item.get("notes") or "").strip()

        if term and meaning:
            clean_items.append({
                "term": term,
                "meaning": meaning,
                "notes": notes,
            })

    if len(clean_items) < 4:
        return []

    num_questions = min(num_questions, len(clean_items))
    chosen_items = random.sample(clean_items, num_questions)

    all_meanings = list({item["meaning"] for item in clean_items})

    questions = []
    for item in chosen_items:
        correct_answer = item["meaning"]

        distractor_pool = [m for m in all_meanings if m != correct_answer]
        if len(distractor_pool) < 3:
            continue

        distractors = random.sample(distractor_pool, 3)
        options = distractors + [correct_answer]
        random.shuffle(options)

        questions.append({
            "term": item["term"],
            "correct_answer": correct_answer,
            "options": options,
            "notes": item["notes"],
        })

    return questions