# Protocolo efetivamente utilizado por Paula

Referência estruturada: `configs/protocol_current.json`. Configurações de cada execução e registros de seleção são a evidência primária. A revisão conjunta deve ser documentada com os nomes reais; o indicador `budget_reviewed=true` sozinho não identifica a revisora.

## Modelos congelados

Uma extração por backbone, pesos fixos e modo de avaliação. Embeddings armazenados em float32. Regressão logística com StandardScaler ajustado somente na fração de treino usada. Busca C = [0.001, 0.01, 0.1, 1, 10], solver lbfgs e máximo de 1.000 iterações. Seleção por macro-F1 de validação; empate favorece menor C. Candidatos sem convergência são descartados.

## Ajuste parcial DINOv3

10% do treino, 1.824 imagens, sementes 17/42/2026; duas taxas por semente: 1e-5 e 3e-5. AdamW, weight decay 0.01, limite 15 épocas, paciência 5. Dois últimos blocos e cabeça: 25.202.696 parâmetros treináveis de 303.137.800. Batch 2, acumulação 8, batch efetivo nominal 16, validação batch 8, precisão mista. Imagens processadas novamente, sem reutilização de embeddings congelados e sem aumentos de dados.

Selecionar época e taxa pela validação; empate entre taxas favorece a menor. Foram seis treinamentos candidatos e três configurações selecionadas, não seis repetições independentes. A semente 42 selecionada melhorou na época 15; registrar o limite de treinamento.

## Avaliação e relato

Macro-F1 principal; accuracy, balanced accuracy, AUROC um-contra-resto por classe e média, recall por classe e matrizes de confusão. Ordem fixa: AMD, CNV, CSR, DME, DR, DRUSEN, MH, NORMAL. Validação e teste auditados não são perfeitamente balanceados. Igualdade de accuracy e balanced accuracy é testada em dados sintéticos balanceados, não exigida nos dados auditados.

Comparações pareadas por fração, semente, manifesto e IDs. Média e desvio-padrão amostral entre sementes; não interpretar o desvio como intervalo de confiança. Teste apenas após encerrar escolhas. Resultados finais de teste ainda não estão disponíveis no pacote revisado.

## Tempo e retomada

Separar extração, busca linear, treino parcial e custo total da busca. `selected_run_epoch_seconds` soma treino, validação e checkpoint das épocas de um candidato, sem carregar o modelo, avaliar novamente o melhor estado ou compactar backups. `peak_allocated_gib` é memória alocada pelo PyTorch, não todo o uso da GPU.

Checkpoints incluem pesos treináveis, otimizador, scaler e estados aleatórios. Retomada na fronteira de época. Uma recuperação real em nova sessão ainda precisa ser demonstrada. Preservar os pesos originais/revisão e os checkpoints ajustados correspondentes aos hashes de seleção.
