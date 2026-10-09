# Tarefa: rotular reclamações de compradores (avaliações nota 1, e-commerce brasileiro)

Você vai ler comentários de compradores que deram a pior nota possível a um pedido. Cada linha do arquivo é `cid<TAB>texto` (o texto pode vir como "título | mensagem"). Palavras como "lannister", "stark", "targaryen", "baratheon" são nomes anonimizados de lojas/plataforma.

Para cada comentário, decida **qual é a queixa central** e marque **um único** rótulo:

| Rótulo | Use quando a queixa central é… |
|---|---|
| `nao_recebido` | o produto não chegou / o comprador ainda espera, sem outra queixa mais específica |
| `atraso` | o produto chegou, mas tarde; ou queixa genérica de demora ("demorou demais") |
| `falha_entrega` | aparece como entregue sem ter chegado; precisou buscar nos Correios; devolvido ao remetente; extraviado; parado/retido nos Correios |
| `incompleto` | veio só parte do pedido: faltou item, unidade ou peça |
| `produto_errado` | chegou outro produto (modelo, cor, tamanho ou voltagem diferente do comprado) |
| `defeito_avaria` | o produto não funciona, chegou quebrado, danificado, vazando ou manchado |
| `qualidade_anuncio` | qualidade ruim, material frágil, diferente da foto/descrição, falsificado, incompatível com o anunciado |
| `cancelamento_estoque` | a loja cancelou, não tinha estoque, entregou mesmo após cancelamento, ou há problema de estorno ligado a cancelamento |
| `atendimento` | a queixa é só sobre atendimento, falta de retorno ou dificuldade de troca/devolução, sem problema mais concreto |
| `outro` | frete caro, cobrança, nota fiscal, elogio, texto vazio ou sem sentido, ou nada acima |

Critérios de desempate:
- Um problema concreto com o pedido ou produto prevalece sobre `atendimento`.
- Se recebeu uma parte e falta o restante, é `incompleto`.
- Se nunca recebeu e reclama do prazo, é `nao_recebido`.

Marque também `sem_resposta` = 1 quando o comprador diz que tentou contato com a loja/plataforma e não obteve resposta, retorno ou solução; caso contrário 0.

## Formato da saída
Um arquivo de texto, uma linha por comentário, na mesma ordem da entrada, sem cabeçalho: `cid;rotulo;sem_resposta`.
Leia a entrada em blocos (ex.: 250 linhas por vez com Read offset/limit), classifique cada comentário lendo-o você mesmo (proibido usar palavras-chave ou scripts para classificar) e grave a saída aos poucos. No fim, confira com um script que o número de linhas e os cids batem com a entrada. Responda só com o total de linhas e a contagem por rótulo.
