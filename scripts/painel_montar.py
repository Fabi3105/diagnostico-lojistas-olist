# -*- coding: utf-8 -*-
"""Monta o index.html: injeta resultados/painel_dados.json (gerado por painel_dados.py) no modelo scripts/painel_modelo.html.
A malha dos estados vem do IBGE (API de malhas, qualidade mínima), simplificada e embutida no modelo."""
import os
from base import RAIZ, RESULTADOS
modelo = open(os.path.join(RAIZ, "scripts", "painel_modelo.html"), encoding="utf-8").read()
dados = open(os.path.join(RESULTADOS, "painel_dados.json"), encoding="utf-8").read()
open(os.path.join(RAIZ, "index.html"), "w", encoding="utf-8").write(modelo.replace("__DATA__", dados))
print("ok: index.html")
