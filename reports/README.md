# Relatórios dos experimentos — 19/11/2026

## Resultados disponíveis

Há 29 resultados selecionados de validação e 29 avaliações finais de teste: 13 DINOv3 linear, 13 ResNet-50 linear e três DINOv3 com fine-tuning parcial em 10%. As frações reduzidas usam sementes 17, 42 e 2026; em 100%, há uma execução linear por modelo.

O teste tem 2.797 imagens. As previsões, métricas e matrizes foram conferidas contra o manifesto auditado na revisão de 19/11. Hiperparâmetros e checkpoints foram escolhidos pela validação. Não repetir seleção com o teste.

| Comparação em 10% | Congelado DINOv3 | Ajuste parcial | Ganho |
|---|---:|---:|---:|
| Macro-F1 médio de validação | 0,8854 | 0,9252 | 3,97 p.p. |
| Macro-F1 médio de teste | 0,8870 | 0,9245 | 3,75 p.p. |

No teste, DINOv3 congelado em 100% alcança 0,9277; ResNet-50, 0,9017. O desvio entre sementes é amostral, não intervalo de confiança. Em 100% não se estima desvio com uma observação.

## Organização

| Caminho relativo a reports/ | Conteúdo |
|---|---|
| `linear_probe/dinov3/pXX_seedSEMENTE_HASH/` | Relatórios de validação e teste DINOv3 |
| `linear_probe/resnet50/pXX_seedSEMENTE_HASH/` | Relatórios de validação e teste ResNet-50 |
| `partial_ft/dinov3/p10_seedSEMENTE/HASH/` | Históricos e relatórios do ajuste parcial |
| `results/validation_summary.csv` | Seleção por validação |
| `results/test_summary.csv` | 29 avaliações finais, com caminhos relativos à raiz |
| `results/test_learning_curve_summary.csv` | Médias e desvios por fração |
| `results/dinov3_partial_ft_paired_comparison.csv` | Ganhos pareados em 10% |
| `results/confusion_figures_index.csv` | Índice e diagnóstico das 29 matrizes |
| `results/cost_runs.csv` e `cost_summary.csv` | Tempos registrados por etapa |
| `results/confusion_pairs_by_run.csv` e `confusion_pairs_summary.csv` | Confusões por execução e médias |
| `results/artifact_index.json` | Origem, hashes, localização e limitações dos backups |
| `figures/` | 31 figuras em PNG e PDF |
| `interpretation.md` | Interpretação de desempenho, custo e erros |

Os diretórios antigos são preservados pela atualização para evitar exclusões acidentais. Após conferir os arquivos canônicos e o commit, cópias redundantes podem ser retiradas. Não alterar registros de seleção apenas para adaptar caminhos.

`run_path`, `metrics_path` e `predictions_path` são relativos à raiz; `source_run_path` identifica o backup original. Campos vazios indicam ausência ou não aplicabilidade, não zero. Tempos históricos de treinamento não são tempos da avaliação final.

## Dados e processamento

23.850 imagens após remover 138 cópias excedentes e colocar 12 conflitos em quarentena: treino 18.260, validação 2.793, teste 2.797. Frações: 180, 910, 1.824, 4.564 e 18.260. Classes: AMD, CNV, CSR, DME, DR, DRUSEN, MH, NORMAL.

As imagens são convertidas para RGB e redimensionadas integralmente a 224 × 224 por interpolação bicúbica. Não há recorte ou aumentos nos experimentos apresentados. A normalização é específica do modelo. O redimensionamento distorce a proporção original e difere da geometria oficial ResNet V2.

DINOv3 usa CLS de 1.024 dimensões; ResNet-50, global average pooling de 2.048. StandardScaler é ajustado somente no subconjunto de treino. Regressão logística: C em [0.001, 0.01, 0.1, 1, 10], lbfgs, máximo 1.000 iterações; descarte de não convergência; desempate pelo menor C.

Ajuste parcial DINOv3: dois últimos blocos e cabeça, 25.202.696 parâmetros treináveis; AdamW, weight decay 0,01, taxas 1e-5 e 3e-5, 15 épocas, paciência 5, batch 2, acumulação 8, avaliação batch 8 e precisão mista. A taxa 3e-5 foi selecionada nas três sementes; melhores épocas 8, 15 e 7. Semente 42 melhorou no limite.

## Reprodução e limites

Execute `notebooks/04_analise_resultados_teste.ipynb` em CPU. Os scripts em `scripts/` organizam relatórios e consolidam custo/erros. Pesos e embeddings completos permanecem externos; a ausência deles não impede análise das previsões.

A recuperação dos checkpoints para inferência foi relatada no chat, mas a retomada com otimizador não está comprovada. Localizações desconhecidas no índice devem ser preenchidas com dados reais. Não há revisão nominal de Ana Júlia registrada, nem resultados RETFound/ViT/CNN/OCTDL integrados.

Não foram comprovadas separação por paciente, independência do pré-treinamento ou ausência de quase duplicatas. Arquitetura e pré-treinamento diferem entre modelos. O teste é interno e não comprova generalização clínica. Consulte `../docs/protocol.md`, `../docs/data_approval.md` e `../docs/octdl_status.md`.
