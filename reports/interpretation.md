# Interpretação dos resultados de Paula

## Desempenho no teste

DINOv3 congelado supera ResNet-50 nas 13 comparações pareadas. A vantagem média em macro-F1 é 4,87 p.p. em 1%, 3,87 em 5%, 3,53 em 10%, 3,46 em 25% e 2,60 em 100%. A diferença diminui conforme o treino cresce. Isso sugere eficiência dos rótulos de treino neste protocolo; os 2.793 rótulos da validação continuam necessários à seleção.

Em 10%, o fine-tuning parcial eleva macro-F1 de 0,8870 ± 0,0062 para 0,9245 ± 0,0037. Os ganhos pareados são 3,99, 3,35 e 3,90 p.p. para sementes 17, 42 e 2026. A proximidade com 0,9277 do DINOv3 congelado em 100% não demonstra equivalência estatística.

## Principais confusões em 10%

Proporções abaixo são médias nas três sementes, divididas pelo suporte da classe verdadeira; não são proporções entre todos os erros.

| Classe verdadeira → predita | DINOv3 congelado | Ajuste parcial |
|---|---:|---:|
| CNV → DRUSEN | 13,05% | 10,95% |
| DRUSEN → NORMAL | 12,89% | 10,70% |

O ajuste reduz essas confusões, mas elas permanecem entre as mais frequentes. No ajuste parcial, DME → NORMAL corresponde a 6,78% das imagens DME em média. A análise é descritiva e não atribui causas clínicas aos erros sem inspeção especializada. As três sementes avaliam as mesmas imagens de teste; não somar seus suportes como pacientes independentes.

## Custos registrados

| Modelo/etapa | Minutos |
|---|---:|
| DINOv3: chamada de extração registrada | 32,27 |
| ResNet-50: chamada de extração registrada | 17,09 |
| DINOv3: soma dos tempos de ajuste da busca linear | 4,51 |
| ResNet-50: soma dos tempos de ajuste da busca linear | 8,15 |
| DINOv3: seis candidatos de ajuste parcial | 157,87 |
| DINOv3: três candidatos selecionados (subconjunto dos seis) | 71,24 |

Não somar a última linha à anterior. A extração reflete a chamada registrada em `complete.json`; a busca linear soma `seconds` dos candidatos; ajuste parcial soma treino, validação e checkpoint por época. Esses escopos diferem e não incluem necessariamente carregamento, transferências, avaliação final ou todas as sessões. Não representar a soma como tempo integral do projeto. Memória `peak_allocated_gib` é alocação PyTorch, não todo consumo da GPU.

A comparação central com RETFound permanece pendente. Não há evidência documental OCTDL integrada. Relatar as limitações de pacientes, origem, pré-treinamento e ausência de teste externo.
