from flask import Flask
import json
import os
from app.btree import BTree


USUARIOS_FILE = "usuarios.json"
VOOS_FILE = "voos.json"


def carregar_json(file):
    if not os.path.exists(file):
        return []
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def salvar_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def proximo_id(registros):
    if not registros:
        return 1
    return max(item.get("id", 0) for item in registros) + 1


