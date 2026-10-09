# Sugestão C. Temas dos comentários das avaliações com nota 1 (método)

Liga com Q2 (atraso e nota), Q5/Q6 (cancelamentos), Q8/B (regiões), Q10 (Black Friday) e A (onde nasce o atraso).

1. **Extração (SQL):** avaliação mais recente de cada pedido; nota 1 com comentário preenchido: 8.706 de 11.363 (os 2.657 sem texto ficam de fora). Texto = título + mensagem.
2. **Classificação com IA:** o Claude leu uma amostra para definir 10 temas e as regras de desempate (`qC_instrucoes_classificacao_ia.md`). Depois, 9 agentes do Claude leram e classificaram os 8.706 comentários, um a um (1 tema principal + marcação "sem resposta"). Nenhuma regra de palavra-chave.
3. **Validação:** revisão manual de uma amostra aleatória de 100 rótulos: cerca de 95 concordantes; as divergências foram casos de fronteira (ex.: qualidade x defeito).
4. **Cruzamento (Python, `scripts/qC_temas_nota1.py`):** rótulos unidos aos pedidos para ver status, entrega, atraso, data da avaliação x data da entrega, número de itens e de lojistas, região e mês.
5. **Grupos:** Logística (não recebido, atraso, falha na entrega); Lojista (incompleto, produto errado, cancelamento/estoque); Produto (defeito/avaria, qualidade/anúncio); Atendimento; Outro.

Arquivos: `resultados/qC_comentarios_nota1_1..4.csv` e `resultados/qC_rotulos_por_pedido.csv` (só ids e rótulos, sem os textos).

```sql
-- Extração (DuckDB)
WITH aval AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_answer_timestamp DESC) AS n
    FROM avaliacoes
)
SELECT review_id, order_id,
       TRIM(COALESCE(review_comment_title, '') || ' | ' || review_comment_message, ' |') AS texto
FROM aval
WHERE n = 1 AND review_score = 1 AND review_comment_message IS NOT NULL;
```
