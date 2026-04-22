from __future__ import annotations

import re


def split_into_exercises(text: str) -> list[dict[str, str]]:
    pattern = r"(Exercice\s+\d+\s*[—-]?\s*[^\n]*)"
    parts = re.split(pattern, text, flags=re.IGNORECASE)

    exercises: list[dict[str, str]] = []

    if len(parts) < 2:
        return [{"title": "Full Lesson", "text": text.strip()}]

    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""
        exercises.append(
            {
                "title": title,
                "text": body,
            }
        )

    return exercises


def extract_vocab_candidates(text: str) -> list[dict[str, str]]:
    text = text.replace("\n", " ")

    phrase_patterns = [
        r"\bpassé composé\b",
        r"\bfutur proche\b",
        r"\bfutur simple\b",
        r"\bil y a\b",
        r"\bquelque chose\b",
        r"\bquelqu’un\b",
    ]

    results: list[dict[str, str]] = []
    seen: set[str] = set()

    for pattern in phrase_patterns:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            normalized = match.strip().lower()
            if normalized not in seen:
                seen.add(normalized)
                results.append({"term": match.strip(), "source_type": "phrase"})

    word_matches = re.findall(r"\b[a-zA-ZÀ-ÿ’'-]{3,}\b", text)

    stop_words = {
        "exercice", "choisis", "complète", "corrige", "texte", "questions",
        "bonne", "forme", "avec", "dans", "pour", "hier", "demain",
        "maintenant", "aujourd’hui", "aujourd'hui", "ce", "cet", "cette",
        "ces", "une", "des", "les", "que", "qui", "où", "oui", "non",
        "mais", "donc", "parce", "elle", "nous", "vous", "ils", "elles",
        "je", "tu", "il", "un", "une", "est", "ont", "pas", "très",
    }

    for word in word_matches:
        normalized = word.strip(" .,!?:;").lower()
        if normalized in stop_words:
            continue
        if normalized.startswith("exercice"):
            continue
        if normalized not in seen:
            seen.add(normalized)
            results.append({"term": word.strip(), "source_type": "word"})

    return results[:100]