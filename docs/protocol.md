# Protocolo efetivamente utilizado por Paula

Referência estruturada: `configs/protocol_current.json`. Configurações de cada execução e registros de seleção são a evidência primária. A revisão conjunta deve ser documentada com os nomes reais; o indicador `budget_reviewed=true` sozinho não identifica a revisora.

## Modelos congelados

Uma extração por backbone, pesos fixos e modo de avaliação. Embeddings armazenados em float32. Regressão logística com StandardScaler ajustado somente na fração de treino usada. Busca C = [0.001, 0.01, 0.1, 1, 10], solver lbfgs e máximo de 1.000 iterações. Seleção por macro-F1 de validação; empate favorece menor C. Candidatos sem convergência são descartados.

## Ajuste parcial DINOv3

10% do treino, 1.824 imagens, sementes 17/42/2026; duas taxas por semente: 1e-5 e 3e-5. AdamW, weight decay 0.01, limite 15 épocas, paciência 5. Dois últimos blocos e cabeça: 25.202.696 parâmetros treináveis de 303.137.800. Batch 2, acumulação 8, batch efetivo nominal 16, validação batch 8, precisão mista. Imagens processadas novamente, sem reutilização de embeddings congelados e sem aumentos de dados.

Selecionar época e taxa pela validação; empate entre taxas favorece a menor. Foram seis treinamentos candidatos e três configurações selecionadas, não seis repetições independentes. A semente 42 selecionada melhorou na época 15; registrar o limite de treinamento.

## Avaliação e relato

Macro-F1 principal; accuracy, balanced accuracy, AUROC um-contra-resto por classe e média, recall por classe e matrizes de confusão. Ordem fixa: AMD, CNV, CSR, DME, DR, DRUSEN, MH, NORMAL. Validação e teste auditados não são perfeitamente balanceados. Igualdade de accuracy e balanced accuracy é testada em dados sintéticos balanceados, não exigida nos dados auditados.

Comparações pareadas por fração, semente, manifesto e IDs. Média e desvio-padrão amostral entre sementes; não interpretar o desvio como intervalo de confiança. Teste apenas após encerrar escolhas. Foram concluídas 29 avaliações finais no teste fixo de 2.797 imagens: 26 classificadores lineares e três checkpoints DINOv3 de ajuste parcial em 10%. A tabela está em `reports/results/test_summary.csv`; a validação permanece separada em `validation_summary.csv`.

## Tempo e retomada

Separar extração, busca linear, treino parcial e custo total da busca. `selected_run_epoch_seconds` soma treino, validação e checkpoint das épocas de um candidato, sem carregar o modelo, avaliar novamente o melhor estado ou compactar backups. `peak_allocated_gib` é memória alocada pelo PyTorch, não todo o uso da GPU.

Checkpoints incluem pesos treináveis, otimizador, scaler e estados aleatórios. Retomada na fronteira de época. A recuperação dos três checkpoints para inferência foi relatada durante a avaliação final e os resultados estão preservados. Isso não demonstra a retomada do treinamento com o estado do otimizador, que permanece sem teste comprovado. Preservar os pesos originais/revisão e os checkpoints ajustados correspondentes aos hashes de seleção.

## Caminhos e reprodução

Após organização, `run_path`, `metrics_path` e `predictions_path` do consolidado são relativos à raiz. `source_run_path` preserva a localização no backup. Não reescrever hashes nem os caminhos internos dos registros históricos de seleção. O script de organização faz cópias verificadas, sem apagar arquivos originais.
