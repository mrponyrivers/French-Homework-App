# French Homework App 🇫🇷

A Streamlit app that turns uploaded French homework `.docx` files into structured study material.

---

## Overview

This project helps turn French homework documents into:

- saved lessons
- extracted exercises
- vocabulary study material
- flashcards
- quiz modes
- exercise practice

It is designed to work with both:

- vocabulary tables
- fill-in-the-blank homework lessons with answers in parentheses

---

## Features

- Upload `.docx` French homework files
- Extract lesson text
- Extract Word tables
- Save lessons to SQLite
- Parse fill-in-the-blank exercises
- Detect answers written in parentheses
- Read section instructions for grouped exercises
- Support vocabulary-based flashcards
- Support vocabulary quiz mode
- Support exercise quiz mode
- Support exercise practice mode
- Browse saved lesson history
- Delete selected lessons

---

## Example supported formats

### Vocabulary table lessons

| French | English |
|--------|---------|
| le     | the     |
| être   | to be   |

### Fill-in-the-blank lessons

```text
Exercise 1. Complete. Choisis le bon mot: je, tu, il, elle
_ suis etudiant. (Je)
_t’appelles comment? (Tu)
_est mon frere. (Il)
_est ma soeur. (Elle)
## Tech Stack

- Python
- Streamlit
- SQLite
- python-docx
- pandas