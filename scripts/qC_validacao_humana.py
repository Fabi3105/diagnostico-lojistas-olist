# -*- coding: utf-8 -*-
"""Validação da classificação com IA, parte 2: comparação com a classificação humana (Fabian, 149 comentários sorteados).
Fabian classificou sem ver os rótulos da IA, seguindo as mesmas regras. Kappa de Cohen por tema, por grupo e
com "não recebido" e "atraso" fundidos. A marcação "sem resposta" não foi preenchida na planilha e fica fora."""
import os
import numpy as np, pandas as pd
from base import RESULTADOS, salvar

f = pd.read_csv(os.path.join(RESULTADOS, "qC_validacao_rotulos_fabian.csv"), sep=";")
r = pd.read_csv(os.path.join(RESULTADOS, "qC_validacao_rotulos_3ias.csv"), sep=";")
d = f.merge(r, on="cid")
GR = {"nao_recebido": "Entrega", "atraso": "Entrega", "falha_entrega": "Entrega", "incompleto": "Envio/estoque",
      "produto_errado": "Envio/estoque", "cancelamento_estoque": "Envio/estoque", "defeito_avaria": "Produto",
      "qualidade_anuncio": "Produto", "atendimento": "Outros", "outro": "Outros", "sem_maioria": "sem maioria"}
FUNDE = {"atraso": "nao_recebido_ou_atraso", "nao_recebido": "nao_recebido_ou_atraso"}

def cohen(x, y):
    x, y = np.asarray(x, dtype=str), np.asarray(y, dtype=str)
    po = (x == y).mean(); pe = sum((x == c).mean() * (y == c).mean() for c in set(x) | set(y))
    return (po - pe) / (1 - pe), 100 * po

rows = []
for nome, col in [("IA original (A)", "tema_A"), ("IA validador B", "tema_B"), ("IA validador C", "tema_C"), ("Maioria das 3 IAs", "maioria")]:
    for nivel, fx in [("tema", lambda s: s), ("tema, com 'não recebido' e 'atraso' fundidos", lambda s: s.replace(FUNDE)), ("grupo", lambda s: s.map(GR))]:
        k, po = cohen(fx(d.tema_F), fx(d[col]))
        rows.append({"comparacao": f"Fabian x {nome}", "nivel": nivel, "concordancia_pct": round(po, 1), "kappa": round(k, 3)})
salvar(pd.DataFrame(rows), "qC_validacao_humana_1.csv", index=False)
salvar(pd.crosstab(d.tema_F, d.tema_A), "qC_validacao_humana_2_matriz.csv")
dist = pd.DataFrame({"Fabian": d.tema_F.map(GR).value_counts(normalize=True), "IA original": d.tema_A.map(GR).value_counts(normalize=True)}).mul(100).round(1)
salvar(dist, "qC_validacao_humana_3_grupos.csv")
print(f"{len(d)} comentários"); print(pd.DataFrame(rows).to_string(index=False)); print(dist)
