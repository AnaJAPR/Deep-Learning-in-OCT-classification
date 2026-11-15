<!-- reports/README.md -->

# Relatórios dos experimentos OCT-C8

Esta pasta reúne os registros de auditoria, configurações, resultados e informações de execução do projeto.

## Estado atual

A tabela `results/validation_summary.csv` contém **29 execuções selecionadas**:

- 13 classificadores lineares com embeddings do DINOv3 ViT-L/16.
- 13 classificadores lineares com embeddings da ResNet-50.
- 3 ajustes parciais do DINOv3 em 10% do treino, nas sementes 17, 42 e 2026.

Para cada backbone congelado, foram executadas as frações de 1%, 5%, 10% e 25% nas três sementes. A fração de 100% foi executada uma vez para evitar repetições determinísticas.

No ajuste parcial, foram comparadas duas taxas de aprendizado por semente, totalizando seis treinamentos candidatos e três configurações selecionadas.

**Os resultados consolidados são de validação. A avaliação final no teste ainda está pendente.**

Os resultados de RETFound, ViT supervisionado e CNN simples ainda não estão documentados neste conjunto de arquivos.

## Dados utilizados

O manifesto adotado contém 23.850 imagens:

| Divisão | Imagens |
|---|---:|
| Treino | 18.260 |
| Validação | 2.793 |
| Teste | 2.797 |
| Total | 23.850 |

SHA-256 do manifesto:

`80d6eedc883410b47beeee6b1c72e72d69309ba38ac2595fc8f2590e6928103d`

Ordem das classes:

`AMD, CNV, CSR, DME, DR, DRUSEN, MH, NORMAL`

Somente o treino é reduzido. A validação permanece fixa e utiliza 2.793 imagens rotuladas, cujo custo de anotação também deve ser considerado.

| Fração | Imagens de treino |
|---|---:|
| 1% | 180 |
| 5% | 910 |
| 10% | 1.824 |
| 25% | 4.564 |
| 100% | 18.260 |

As frações são calculadas por classe sobre o treino auditado, com arredondamento para baixo. Os subconjuntos são aninhados por semente e compartilhados entre os modelos.

O registro de adoção dos dados está em [docs/data_approval.md](../docs/data_approval.md).

## Modelos congelados e classificadores lineares

Os pesos dos backbones permanecem fixos durante a extração, realizada em modo de avaliação.

- **DINOv3:** representação CLS final, com 1.024 dimensões.
- **ResNet-50:** saída do global average pooling antes da camada classificadora, com 2.048 dimensões.

As imagens são convertidas para RGB e redimensionadas integralmente para 224 × 224 pixels, com interpolação bicúbica e sem recorte. A normalização é específica de cada modelo.

Os embeddings são extraídos uma vez por backbone e reutilizados nas diferentes frações e sementes.

O classificador é uma regressão logística precedida de StandardScaler. O scaler é ajustado exclusivamente no subconjunto de treino daquela execução.

Valores de regularização comparados:

`C = [0.001, 0.01, 0.1, 1.0, 10.0]`

A rotina utiliza solver `lbfgs` e limite de 1.000 iterações. Candidatos com aviso de não convergência são descartados.

A seleção utiliza macro-F1 de validação. Em caso de empate, é escolhido o menor C.

## Ajuste parcial do DINOv3

Foram utilizadas 1.824 imagens de treino e 2.793 de validação.

O ajuste alterou os dois últimos blocos do DINOv3 e a camada classificadora, totalizando 25.202.696 parâmetros treináveis de 303.137.800 parâmetros.

Configuração:

- Sementes: 17, 42 e 2026.
- Taxas de aprendizado: 1e-5 e 3e-5.
- Otimizador: AdamW.
- Weight decay: 0,01.
- Limite: 15 épocas.
- Parada antecipada: cinco épocas sem melhora.
- Batch de treino: 2.
- Acumulação de gradientes: 8 passos.
- Batch efetivo nominal: 16.
- Batch de validação: 8.
- Precisão mista.
- Sem aumentos de dados.

As imagens são processadas novamente durante o ajuste. Os embeddings extraídos com os pesos congelados não são reutilizados nessa etapa.

A melhor época de cada treinamento e a taxa selecionada são determinadas pelo macro-F1 de validação. Em caso de empate entre taxas, é escolhida a menor.

| Semente | Taxa selecionada | Épocas executadas | Melhor época | Macro-F1 de validação |
|---|---:|---:|---:|---:|
| 17 | 3e-5 | 13 | 8 | 0,919664 |
| 42 | 3e-5 | 15 | 15 | 0,927597 |
| 2026 | 3e-5 | 12 | 7 | 0,928251 |

A execução selecionada da semente 42 melhorou na última época disponível. Portanto, o limite de 15 épocas deve ser registrado como uma limitação.

## Comparação em 10% do treino

A comparação abaixo utiliza as mesmas sementes e amostras de treino.

| Método | Macro-F1 médio de validação | Desvio-padrão amostral |
|---|---:|---:|
| DINOv3 congelado + classificador linear | 0,8854 | 0,0079 |
| DINOv3 com ajuste parcial | 0,9252 | 0,0048 |

O ganho médio observado foi de aproximadamente **3,97 pontos percentuais**.

Esses resultados foram utilizados na seleção das configurações. A comparação final deverá ser realizada no teste após o encerramento das escolhas experimentais.

O desvio-padrão entre sementes descreve a variação das execuções e não representa automaticamente um intervalo de confiança.

## Organização dos arquivos

Os caminhos abaixo são relativos a esta pasta.

| Caminho | Conteúdo |
|---|---|
| `data_audit/` | Auditoria, decisões de limpeza e limitações |
| `protocol/` | Registros históricos do notebook 02 |
| `embeddings/` | Configurações, identidade dos modelos e registros das extrações |
| `pilots/` | Benchmarks e pilotos disponíveis |
| `linear_probe/dinov3/` | Busca e resultados dos classificadores DINOv3 |
| `linear_probe/resnet50/` | Busca e resultados dos classificadores ResNet-50 |
| `partial_ft/dinov3/` | Configurações, históricos, métricas e seleção do ajuste parcial |
| `partial_ft/dinov3/execution_metadata/seeds42_2026/` | Ambiente e protocolo das execuções recentes |
| `results/validation_summary.csv` | Uma linha por execução selecionada |
| `results/artifact_index.json` | Referências dos backups e checkpoints |

As subpastas preservam os identificadores de fração, semente e configuração.

## Como interpretar a tabela consolidada

`results/validation_summary.csv` contém 29 linhas.

A coluna `adaptation` distingue:

- `linear_probe`: classificador treinado sobre embeddings de um backbone congelado.
- `partial_finetuning`: ajuste parcial do backbone e da camada classificadora.

Nos modelos congelados, a validação seleciona C. No ajuste parcial, seleciona a taxa de aprendizado e a melhor época.

A tabela registra macro-F1, accuracy, balanced accuracy, AUROC e recall por classe, além de configurações, hashes, caminhos e informações de custo disponíveis.

Campos vazios indicam informação não disponível ou não aplicável. Por exemplo, melhor época não se aplica ao classificador linear.

Os caminhos `run_path`, `metrics_path` e `predictions_path` são relativos à raiz do repositório. `source_run_path` preserva a referência da execução no pacote de origem.

Os caminhos internos dos registros `selection_lock.json` permanecem relativos à estrutura original das saídas. Não devem ser reescritos apenas porque os relatórios foram reorganizados.

Para comparar modelos, conferir:

- Fração e semente.
- Hash do manifesto.
- Identificadores da amostra de treino.
- Divisão de avaliação.
- Forma de adaptação.

## Métricas e separação dos dados

Macro-F1 é a medida principal. Também são calculados:

- Accuracy.
- Balanced accuracy.
- AUROC por classe e média macro.
- Recall por classe.
- Matrizes de confusão em contagens e normalizadas por linha.

Treino ajusta os parâmetros e a padronização. Validação escolhe configurações. Teste é reservado à avaliação final.

As divisões auditadas não são perfeitamente balanceadas; portanto, accuracy e balanced accuracy não precisam coincidir exatamente.

## Tempo e memória

Os tempos de ajuste dos classificadores registrados em `trials.json` não incluem necessariamente avaliação e salvamento.

No ajuste parcial, `selected_run_epoch_seconds` soma os tempos registrados de treino, validação e checkpoint das épocas da configuração selecionada. Não representa toda a duração da sessão nem o custo completo da busca.

Para reportar o custo da busca, considerar também os candidatos não selecionados.

`peak_allocated_gib` representa a memória alocada pelo PyTorch, não todo o consumo de memória da GPU.

## Backups e checkpoints

O índice de artefatos está em `results/artifact_index.json`.

Backups de referência:

- `DINOV3_extracao_completa.zip`: embeddings e classificadores DINOv3.
- `80d6eedc8834_a305b2c7_backup (5)(2).zip`: embeddings e classificadores ResNet-50.
- `dinov3_partial_ft_reports.zip`: relatórios do ajuste parcial das sementes 42 e 2026; não contém os pesos ajustados.

As localizações externas e versões ainda precisam ser preenchidas no índice.

Os hashes esperados de `best.pt` foram registrados a partir dos resultados de seleção. A correspondência com os arquivos de pesos ainda precisa ser verificada.

A política do projeto é preservar embeddings, classificadores serializados e checkpoints fora do Git, mantendo no repositório os relatórios e as referências necessárias para recuperá-los.

Os checkpoints de ajuste parcial devem ser usados com a mesma revisão do backbone original. A retomada em uma nova sessão ainda precisa de evidência de teste concluído.

## Limitações

- A separação por paciente não foi comprovada.
- A independência em relação aos dados de pré-treinamento não foi comprovada.
- A auditoria removeu duplicatas exatas, mas não verificou completamente imagens quase duplicadas.
- O redimensionamento integral altera a proporção de imagens que não são quadradas.
- A geometria de processamento da ResNet-50 difere da transformação oficial de seus pesos.
- Diferenças entre modelos envolvem arquitetura, dados, escala e objetivo de pré-treinamento.
- A semente 42 do ajuste parcial ainda melhorou no limite de épocas.
- Os resultados disponíveis são de validação.
- A avaliação externa ainda não foi realizada.

O acompanhamento geral está em [docs/status.md](../docs/status.md).