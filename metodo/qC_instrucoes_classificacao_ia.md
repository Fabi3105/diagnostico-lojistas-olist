# Classificação de comentários de avaliações com nota 1 (e-commerce brasileiro, 2016-2018)

Cada linha do arquivo de entrada é: `cid<TAB>texto` (o texto pode ter "título | mensagem").
Nomes como "lannister", "stark", "targaryen" são o nome anonimizado da plataforma/loja.

Para CADA linha, atribua:

1. `tema` — o problema PRINCIPAL que o cliente relata (um só), entre:
   - `nao_recebido` — produto ainda não chegou / não foi entregue / está esperando (sem outro problema principal)
   - `atraso` — chegou, mas depois do prazo ou com demora (o cliente diz que recebeu, ou reclama só da demora de forma genérica: "demorou muito", "muita demora na entrega")
   - `falha_entrega` — consta como entregue mas não recebeu; teve que retirar nos Correios; entrega devolvida ao remetente; extravio; pedido preso/retido nos Correios
   - `incompleto` — faltou item, unidade ou peça (pedido parcial, "comprei 2 recebi 1", "faltou peça")
   - `produto_errado` — recebeu produto diferente do comprado (outro modelo, cor, tamanho, voltagem)
   - `defeito_avaria` — produto com defeito, não funciona, quebrado, danificado, vazando, manchado
   - `qualidade_anuncio` — qualidade ruim, material fraco, diferente da foto/descrição, não original/réplica, incompatível com o anunciado
   - `cancelamento_estoque` — loja cancelou, produto indisponível/sem estoque, cancelou mas mesmo assim enviaram, problema com reembolso/estorno de pedido cancelado
   - `atendimento` — a reclamação principal é sobre atendimento/falta de resposta/dificuldade de devolução ou troca, sem outro problema mais específico
   - `outro` — frete caro, cobrança, nota fiscal, elogio, texto sem conteúdo ("xxx", "bom"), ou não se encaixa

   Regras de desempate: problema concreto do produto/pedido vence `atendimento`. Se recebeu parte e falta o resto → `incompleto`. Se nunca recebeu e reclama do prazo → `nao_recebido`.

2. `sem_resposta` — 1 se o cliente menciona que tentou contato e não teve resposta/retorno/solução da loja ou plataforma; senão 0.

## Saída

Escreva o arquivo de saída com a ferramenta Write, uma linha por comentário, NA MESMA ORDEM, sem cabeçalho:
`cid;tema;sem_resposta`

Use exatamente os rótulos acima. O número de linhas da saída deve ser igual ao da entrada. Ao final, confira com `wc -l` e com um pequeno script que os cids da saída batem com os da entrada; corrija se faltar algum. Leia o arquivo de entrada em partes (ex.: 250 linhas por vez com Read offset/limit) e escreva a saída acumulando (pode usar Write na primeira parte e depois acrescentar com Bash `cat >> arquivo <<'EOF'`).

Responda ao final só com: número de linhas escritas e contagem por tema.
