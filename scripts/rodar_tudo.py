# -*- coding: utf-8 -*-
"""Reproduz o estudo do início ao fim, na ordem certa. Uso: python rodar_tudo.py  (de dentro da pasta scripts/)
Para retomar de um ponto: python rodar_tudo.py <nome_do_script> [<nome_do_último>]  (ex.: rodar_tudo.py qH_ativacao_lojistas)

Pré-requisitos: os CSVs da base em dados/brutos/ (Kaggle: Brazilian E-Commerce Public Dataset by Olist) e os
pacotes de requirements.txt. Na primeira execução, base.py cria a cópia SQLite em dados/olist.sqlite.
Se a pasta do projeto estiver em um disco sincronizado ou em rede, o SQLite pode falhar com "disk I/O error";
nesse caso, aponte a variável de ambiente OLIST_SQLITE para um caminho local (ex.: C:\\temp\\olist.sqlite).

A classificação dos comentários com IA (qC_rotulos_por_pedido.csv e qC_validacao_rotulos_*.csv) não é refeita
aqui: foi feita por agentes de IA e por revisão humana, e os rótulos publicados são a entrada dos scripts qC_*."""
import os, runpy, sys, time

AQUI = os.path.dirname(os.path.abspath(__file__)); os.chdir(AQUI); sys.path.insert(0, AQUI)
ETAPAS = [
    ("1. validação da base", "validar_dados"),
    ("2. perguntas Q1 a Q10 (SQL)", "rodar_sql"),
    ("3. revisões Q7b e Q8b", "q07b_recompra_90d"), (None, "q08b_renda_prazo"),
    ("4. sugestões A a G", "qA_onde_nasce_atraso"), (None, "qB_frete_estado"), (None, "qC_temas_nota1"),
    (None, "qC_validacao_ia"), (None, "qC_validacao_humana"), (None, "qD_lojistas_problema"),
    (None, "qE_retencao_lojistas"), (None, "qF_rfm_lojistas"), (None, "qG_prazo_prometido"),
    ("5. revisão final: H a K", "qH_ativacao_lojistas"), (None, "qI_vendas_categorias"), (None, "qJ_safras_lojistas"), (None, "qK_estabilidade_amostra"),
    ("6. indicadores padrão, gráficos e painel", "indicadores_padrao"), (None, "graficos"), (None, "painel_dados"), (None, "painel_montar"),
    ("7. conferência do relatório", "conferir_relatorio"),
]
nomes = [m for _, m in ETAPAS]
de = nomes.index(sys.argv[1]) if len(sys.argv) > 1 else 0
ate = nomes.index(sys.argv[2]) if len(sys.argv) > 2 else len(nomes) - 1
inicio = time.time()
for titulo, mod in ETAPAS[de:ate + 1]:
    if titulo: print(f"\n=== {titulo}")
    print(f"--- {mod}.py"); t = time.time()
    runpy.run_path(os.path.join(AQUI, mod + ".py"), run_name="__main__")
    print(f"    ({time.time() - t:.0f} s)")
print(f"\nconcluído em {(time.time() - inicio) / 60:.1f} min")
