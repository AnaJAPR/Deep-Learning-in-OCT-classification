# Classificação de OCT com poucos dados rotulados

**Modelos Fundacionais Visuais Gerais versus Especializados para Classificação de OCT com Poucos Dados Rotulados**

Alunas: **Paula Eduarda de Lima** e **Ana Júlia Amaro Pereira Rocha**. 

Investigamos se representações gerais do **DINOv3** podem igualar ou superar as do **RETFound OCT**, especializado em retina, quando há poucos exemplos rotulados para treinamento.



## 1 Objetivos e escopo

- Comparar modelos com 1%, 5%, 10%, 25% e 100% do treino do OCT-C8.
- Priorizar modelos congelados: extrair os vetores das imagens uma vez e treinar classificadores lineares sobre esses vetores.
- Comparar com ResNet-50, ViT supervisionado e uma CNN simples sem pré-treinamento.
- Fazer ajuste parcial de DINOv3 e RETFound em 10% e, se viável, 1% do treino.
- Como extensão opcional, avaliar transferência para OCTDL com AMD, DME e Normal.
- Registrar desempenho, tempo e memória usados.

O projeto é um estudo experimental de transferência de representações. 

## 2 Regras principais

1. **O Git guarda código, configurações, documentação e resultados pequenos selecionados.** Imagens, pesos, embeddings e arquivos de execução ficam fora do Git.
2. **Dados originais não são alterados.** Correções são registradas em novas versões dos manifestos e das divisões.
3. **Todos os modelos usam as mesmas amostras, classes e código de avaliação.**
4. **Validação escolhe configurações; teste fica reservado para a avaliação final.**
5. **Cada execução tem uma pasta e um identificador próprios.** Não sobrescrever uma execução concluída.
6. **Arquivos temporários não são backup.** Confirmar a cópia persistente antes de encerrar a sessão.
7. **Tokens nunca entram em código, configurações, logs ou Git.** Cada integrante usa sua própria conta autorizada.
8. **Resultados do teste de infraestrutura não são resultados científicos.** Identificá-los como `smoke`.



## 3 Organização do repositório

Nome sugerido do repositório: `oct-foundation-models`. Usar os caminhos abaixo a partir da raiz do clone.

| Caminho | Conteúdo | Versionar no Git? |
|---|---|---|
| `README.md` | Instruções gerais e padrões | Sim |
| `.gitignore` | Arquivos que não devem entrar no Git | Sim |
| `requirements/` | Dependências mínimas e versões verificadas por ambiente | Sim |
| `configs/` | Configurações compartilhadas de dados, modelos e experimentos | Sim |
| `notebooks/` | Notebooks numerados, sem saídas volumosas | Sim |
| `src/oct_project/` | Funções reutilizáveis do projeto | Sim, quando implementadas |
| `scripts/` | Entradas de execução e consolidação | Sim, quando implementadas |
| `tests/` | Verificações de divisões, alinhamento, métricas e retomada | Sim, quando implementadas |
| `metadata/` | Registro dos datasets e checkpoints, com referências sem credenciais | Sim |
| `manifests/` | Inventários aprovados com caminhos relativos e metadados não sensíveis | Sim |
| `splits/` | Listas de IDs de treino, validação, teste e subconjuntos | Sim |
| `docs/` | Protocolo, decisões, tarefas, fontes e instruções adicionais | Sim |
| `results/` | Métricas consolidadas e índice de arquivos externos | Sim, após revisão |
| `reports/figures/` | Figuras finais de tamanho moderado | Sim |
| `reports/tables/` | Tabelas finais em CSV ou LaTeX | Sim |
| `reports/paper/` | Fontes do relatório e referências bibliográficas | Sim |
| `reports/slides/` | Roteiro e fontes leves da apresentação | Sim |
| `data/` | Dados locais brutos ou derivados | Não |
| `artifacts/` | Pesos, embeddings, execuções, previsões e backups locais | Não |
| `cache/` | Downloads temporários | Não |

### Arquivos de documentação

| Arquivo previsto | Responsabilidade |
|---|---|
| `docs/protocol.md` | Explicar as regras experimentais aprovadas |
| `docs/data_audit.md` | Registrar duplicatas, arquivos ilegíveis, pacientes, origem e decisões |
| `metadata/datasets.csv` | Fonte, versão e condições de uso dos datasets |
| `metadata/model_registry.csv` | Origem e versão exata dos checkpoints |
| `results/artifact_index.csv` | Localizar artefatos persistidos fora do Git |
| `results/experiment_summary.csv` | Consolidar execuções validadas |


### Código compartilhado

Quando implementados, usar módulos com responsabilidades claras: `data.py`, `transforms.py`, `sampling.py`, `models.py`, `features.py`, `training.py`, `evaluation.py` e `io.py`, dentro de `src/oct_project/`.

Os notebooks coordenam a execução e mostram resultados; funções repetidas devem migrar para esses módulos. Não criar dois avaliadores independentes, um por integrante. Documentar em cada script suas entradas e saídas antes de anunciar comandos de execução neste README.

## 4 Nomes de arquivos e identificadores

### Vocabulário fixo

| Campo | Valores |
|---|---|
| Dataset | `octc8`, `octdl` |
| Tarefa | `c8` para oito classes; `c3` para AMD, DME e Normal |
| Divisão | `train`, `val`, `test` |
| Modelo | `dinov3_vitl16`, `retfound_mae_oct`, `resnet50`, `vit_l16_sup`, `cnn_scratch` |
| Método | `smoke`, `extract`, `linear`, `ft_partial`, `scratch` |
| Fração | `p01`, `p05`, `p10`, `p25`, `p100` |
| Semente | `seed17`, `seed42`, `seed2026` |
| Integrante | `paula`, `ana_julia` |

`p01` significa 1%; no YAML, representa-se a mesma fração como `0.01`. Os nomes curtos dos modelos não substituem o registro do checkpoint, arquitetura e pré-treinamento exatos.

### Notebooks

Padrão: `NN_objetivo_modelo.ipynb`. Numeração define a ordem lógica, não a data de criação.

| Nome planejado | Responsável |
|---|---|
| `01_octc8_preparacao_dinov3_kaggle.ipynb` | Paula; notebook inicial preparado, execução real a verificar |
| `02_octc8_auditoria.ipynb` | Paula |
| `03_octc8_subconjuntos.ipynb` | Paula|
| `04_extracao_dinov3.ipynb` | Paula |
| `05_extracao_retfound.ipynb` | Ana Júlia |
| `06_extracao_baselines.ipynb` | Paula na ResNet-50; Ana Júlia no ViT |
| `07_linear_probing.ipynb` | Rotina comum; cada uma executa seus modelos |
| `08_cnn_scratch.ipynb` | Ana Júlia |
| `09_finetuning_dinov3.ipynb` | Paula |
| `10_finetuning_retfound.ipynb` | Ana Júlia |
| `11_octdl_avaliacao.ipynb` | Paula e Ana Júlia, se viável |
| `12_analise_resultados.ipynb` | Paula e Ana Júlia |

Exportar a versão do Kaggle/Colab para o mesmo arquivo do Git. Retirar saídas grandes e verificar se não há credenciais antes do commit. A saída completa fica na versão persistida da execução.

### Identificador de execução

Para treino ou avaliação de uma configuração:

```text
{dataset}_{task}_{model}_{method}_{fraction}_{seed}_{owner}_{utc}_{config_hash}
```

Exemplo ilustrativo:

```text
octc8_c8_dinov3_vitl16_linear_p01_seed17_paula_20261025T143000Z_a1b2c3d4
```

O timestamp registra o início da execução. `config_hash` é o prefixo de oito caracteres do SHA-256 da configuração efetiva, serializada em JSON com chaves ordenadas, excluindo timestamp, responsável e caminhos locais. Guardar também o hash completo. Se houver colisão, ampliar o prefixo; nunca sobrescrever.

Uma retomada mantém o mesmo `run_id`. Uma nova tentativa do zero ganha outro `run_id`, ainda que use a mesma configuração. Registrar `retry_of` quando substituir uma tentativa com falha. Ao consolidar resultados, selecionar uma execução válida por condição e semente; não contar tentativas como repetições independentes.



## 7 Dados e prevenção de vazamento

### Classes do OCT-C8

Manter o mesmo arquivo `metadata/class_to_idx.json` para todos os modelos:

```json
{
  "AMD": 0,
  "CNV": 1,
  "CSR": 2,
  "DME": 3,
  "DR": 4,
  "DRUSEN": 5,
  "MH": 6,
  "NORMAL": 7
}
```

Para a tarefa externa de três classes, criar um arquivo separado `metadata/class_to_idx_c3.json`: `AMD=0`, `DME=1`, `NORMAL=2`. Não sobrescrever o mapeamento de oito classes.

### Inventário e auditoria

O inventário inicial `octc8_inventory_v1.csv` contém `image_id`, `relative_path`, `split`, `class_name` e `class_id`. O `image_id` do primeiro notebook é um hash do caminho relativo: **não detecta duplicatas de conteúdo**.

Após a auditoria, salvar `octc8_manifest_v1.csv`, com os campos adicionais abaixo. Não chamar de auditado um arquivo que só teve contagens conferidas.

| Campo | Conteúdo |
|---|---|
| `image_id` | Identificador estável e único no dataset |
| `relative_path` | Caminho a partir de `DATA_ROOT`, usando `/` |
| `split` | `train`, `val` ou `test` |
| `class_name`, `class_id` | Rótulo e código do mapeamento compartilhado |
| `width`, `height`, `channels` | Dimensões verificadas |
| `sha256_file` | Hash dos bytes do arquivo, para cópias exatas |
| `patient_id` | Identificador disponível; vazio se desconhecido |
| `source` | Origem documentada; vazia se desconhecida |
| `readable` | `true` ou `false` após tentar decodificar a imagem |
| `included` | `true` ou `false` para o protocolo aprovado |
| `exclusion_reason` | Motivo documentado de exclusão, se houver |

Hash de arquivo não detecta necessariamente a mesma imagem recodificada. Complementar com comparação dos pixels ou similaridade visual quando apropriado. Não inventar pacientes ou origens a partir de nomes ambíguos. Se metadados individuais não forem adequados para publicação, manter a versão completa em armazenamento restrito e versionar somente uma versão não sensível.

Se o caminho de origem mudar, preservar a relação entre IDs antigos e novos. Congelar o manifesto aprovado, registrar sua versão e SHA-256 completo. Alterações posteriores geram outra versão e exigem revisão dos subconjuntos e caches afetados.

### Subconjuntos

Padrão de arquivo:

```text
splits/octc8_v1/train_p01_seed17.csv
splits/octc8_v1/train_p05_seed17.csv
splits/octc8_v1/val.csv
splits/octc8_v1/test.csv
```

Cada arquivo contém a coluna `image_id`, sem índice extra. As listas são criadas uma vez e reutilizadas por todos os modelos.

| Fração | Por classe no plano | Total no plano |
|---|---:|---:|
| `p01` | 23 | 184 |
| `p05` | 115 | 920 |
| `p10` | 230 | 1.840 |
| `p25` | 575 | 4.600 |
| `p100` | 2.300 | 18.400 |

Contagens são as previstas na proposta, sujeitas à auditoria. Se mudar o total elegível, definir arredondamento e contagens reais no protocolo. Não excluir imagens apenas para reproduzir a tabela.

Usar sementes 17, 42 e 2026. Dentro de cada semente, os subconjuntos devem ser aninhados: 1% está contido em 5%, depois 10%, 25% e 100%. Validação e teste permanecem fixos. Quando pacientes forem conhecidos, a separação entre divisões deve respeitá-los. Qualquer alteração das divisões oficiais deve ser documentada.

Nunca ajustar normalização aprendida, seleção de variáveis, hiperparâmetros ou escolha de checkpoints usando o teste. No linear probing, eventual padronizador deve ser ajustado somente sobre os embeddings do subconjunto de treino usado na execução.

O regime de poucos rótulos se refere ao treino; a validação fixa também utiliza rótulos. O nome OCT-C8 não prova independência dos dados de pré-treinamento: registrar a investigação da procedência e o que não puder ser confirmado.

## 8 Modelos e dependências

| Identificador interno | Origem planejada | Responsável |
|---|---|---|
| `dinov3_vitl16` | `facebook/dinov3-vitl16-pretrain-lvd1689m` | Paula |
| `retfound_mae_oct` | `YukunZhou/RETFound_mae_natureOCT` | Ana Júlia |
| `resnet50` | Checkpoint supervisionado em ImageNet, a fixar | Paula |
| `vit_l16_sup` | Checkpoint supervisionado, a fixar e documentar | Ana Júlia |
| `cnn_scratch` | Arquitetura pequena, fixa e sem pré-treinamento | Ana Júlia |

Em `metadata/model_registry.csv`, registrar: `model_id`, `source_url`, `repo_id`, `revision`, `weight_filename`, `weight_sha256` quando disponível, `pretraining_data`, `pretraining_method`, `architecture`, `input_size`, `embedding_method`, `license_url`, `access_status` e `owner`.

Não substituir silenciosamente DINOv3 de imagens naturais por uma versão de satélites, nem RETFound OCT por CFP ou DINOv2. O carregamento do RETFound deve seguir sua implementação própria. Os checkpoints supervisionados ainda precisam ser fixados antes dos experimentos.

### Ambiente

- O primeiro notebook usa `transformers==4.56.2`, com suporte ao DINOv3, e registra as versões efetivamente instaladas.
- Manter arquivos separados por necessidade, como `requirements/dinov3.txt` e `requirements/retfound.txt`, após validar os ambientes.
- Registrar Python, PyTorch, torchvision, Transformers, timm quando usado, NumPy, pandas e scikit-learn quando usado.
- Não reinstalar PyTorch/CUDA indiscriminadamente no ambiente fornecido. Se houver incompatibilidade, registrar a correção e testar um lote pequeno.
- Se uma instalação alterar bibliotecas já importadas, reiniciar a sessão antes de continuar.
- As duas implementações podem usar ambientes diferentes, mas devem compartilhar dados, protocolo e formato das saídas.
- Usar o checkpoint fixado por commit/revisão. `main` não identifica permanentemente uma versão.

Tokens ficam no Kaggle Secrets ou no gerenciador de segredos do ambiente escolhido, nunca no registro de modelos. Não exportar todo o ambiente do processo para logs. Respeitar as condições de uso dos dados e pesos; não redistribuir pesos restritos junto das saídas.

## 9 Configurações dos experimentos

Guardar configurações compartilhadas em `configs/`; salvar a configuração efetivamente usada como `config_resolved.json` dentro de cada execução.

Exemplo de arquivo previsto: `configs/experiments/octc8_dinov3_linear_p01_seed17.yaml`.

```yaml
# Esquema proposto: ainda precisa ser conectado ao código de execução.
dataset: octc8
task: c8
manifest_version: octc8_v1
manifest_sha256: null       # preencher antes da execução científica
train_ids: splits/octc8_v1/train_p01_seed17.csv
val_ids: splits/octc8_v1/val.csv
test_ids: splits/octc8_v1/test.csv
class_mapping: metadata/class_to_idx.json
model_id: dinov3_vitl16
checkpoint_repo: facebook/dinov3-vitl16-pretrain-lvd1689m
checkpoint_revision: null   # preencher com revisão confirmada
method: linear
train_fraction: 0.01
subset_seed: 17
training_seed: 17
input_size: [224, 224]
preprocessing_id: null      # fixar após revisar o piloto
feature_id: null            # identificar o cache aprovado
selection_metric: macro_f1
selection_split: val
owner: paula
```

O exemplo não é um experimento pronto para rodar: campos `null` precisam ser resolvidos. Parâmetros do classificador, otimizador, transformações e busca devem constar na configuração final. Registrar também o hash das listas de amostras.

Separar `subset_seed` da semente de treinamento. Em 100%, as listas de treino são iguais entre sementes; uma execução determinística idêntica não deve ser repetida como se fosse uma nova amostragem.

## 10 Embeddings reutilizáveis

Guardar vetores congelados em:

```text
<ARTIFACT_ROOT>/features/<feature_id>/<split>/chunk_00000.npz
```

Definir `feature_id` como `{dataset}_{model}_{feature_hash}`. O hash deve identificar dataset/manifesto e sua integridade, checkpoint/revisão, transformação, seleção dos tokens ou pooling, resolução, precisão numérica e versões relevantes. Guardar a especificação completa em `feature_spec.json`.

**O cache não depende da fração de treino ou da semente do classificador**, desde que a extração seja determinística. Selecionar as linhas dos mesmos vetores para 1%, 5%, 10%, 25% e 100%.

Cada bloco contém `embeddings`, `image_ids`, `class_ids` e a assinatura da configuração. Registrar dimensões e ordem dos IDs; validar contagem, unicidade e ausência de `NaN`/infinito. Manter treino, validação e teste em pastas separadas.

O teste inicial usa `smoke/dinov3_vitl16_smoke_<assinatura>/`, conforme seu notebook. Essa saída contém apenas uma pequena amostra; não é o cache completo dos experimentos.

Mudar o checkpoint, a transformação ou o método de extração exige outro cache. Não reutilizar embeddings congelados durante fine-tuning, pois os pesos do backbone mudam.

## 11 Arquivos de cada execução

Pasta: `<ARTIFACT_ROOT>/runs/<run_id>/`.

| Arquivo ou subpasta | Conteúdo |
|---|---|
| `config_resolved.json` | Configuração efetiva e hashes completos |
| `environment.json` | Versões, plataforma, GPU, memória e CUDA |
| `code_version.json` | Commit do Git e indicação de alterações locais |
| `status.json` | Estado, início, fim, progresso e motivo de falha |
| `metrics_val.json` | Métricas de validação |
| `metrics_test.json` | Criado somente após a avaliação final autorizada pelo protocolo |
| `predictions_val.csv` | Previsões por imagem na validação |
| `predictions_test.csv` | Previsões por imagem no teste final |
| `training_history.csv` | Evolução por época, quando houver treinamento |
| `timing.json` | Tempos por etapa e pico de memória |
| `logs/` | Logs sem credenciais |
| `checkpoints/last.pt` | Último estado retomável de treinamento |
| `checkpoints/best.pt` | Melhor estado segundo a validação |

Arquivos específicos de treinamento não são exigidos em uma simples extração. No linear probing em CPU, salvar o classificador, seu padronizador quando houver e a versão da biblioteca; usar o formato apropriado, documentado na execução.

Estados de execução: `running`, `interrupted`, `failed`, `completed`. Avaliar apenas na validação não equivale a concluir a avaliação final no teste; guardar `evaluation_stage` separadamente.

Para resultados científicos, preferir código já commitado. Se houver alterações locais, salvar também o patch ou snapshot do código; um hash de commit isolado não reproduz mudanças não commitadas.

### Previsões e métricas

`predictions_<split>.csv` deve conter `run_id`, `image_id`, `y_true`, `y_pred` e uma probabilidade por classe, como `prob_amd`, na ordem definida pelo mapeamento. Para `c3`, usar somente as três classes correspondentes. Não misturar logits e probabilidades sem identificá-los.

Métrica principal: **macro-F1**. Reportar também accuracy, balanced accuracy, AUROC macro one-vs-rest, recall por classe e matrizes de confusão. Usar valores entre 0 e 1 nos arquivos; converter para porcentagem apenas na apresentação. Se uma métrica for indefinida, registrar `null` e o motivo; não substituir por zero.

Em `results/experiment_summary.csv`, usar uma linha por `run_id`, dataset avaliado e divisão. Campos mínimos: modelo, método, tarefa, fração, sementes, número de imagens de treino, métricas, tempo, GPU, parâmetros treináveis, estágio de avaliação e localização do artefato.

A consolidação deve ser gerada a partir dos arquivos por execução, não preenchida manualmente com números copiados de prints. Comparar modelos nas mesmas amostras e mostrar média e desvio entre sementes. Essa dispersão não é automaticamente um intervalo de confiança populacional.

## 12 Salvamento e retomada

### Extração de vetores

1. Processar em blocos pequenos, com IDs conhecidos.
2. Gravar primeiro em arquivo temporário e renomear somente após concluir a escrita.
3. Atualizar o progresso depois de validar o bloco.
4. Ao retomar, conferir assinatura, IDs, classes, tamanho e integridade dos blocos.
5. Reutilizar apenas blocos completos e compatíveis.
6. Se houver bloco corrompido, isolar o arquivo, registrar a falha e recalcular esse bloco.

### Treinamento

Salvar pesos, otimizador, scheduler quando usado, escalador de precisão mista quando usado, época, passo global, melhor métrica e estados dos geradores aleatórios. Se salvar no meio de uma época, registrar também o estado do amostrador/ordem dos lotes; caso contrário, definir a retomada no início de uma época e documentar a repetição de trabalho.

Carregar apenas checkpoints confiáveis. `best.pt` serve para avaliação e não substitui necessariamente `last.pt` para continuação fiel do treinamento. Mesmo com sementes fixas, versões e hardware podem causar pequenas diferenças: registrar o ambiente.

### Persistência fora da sessão

- Durante a execução, salvar localmente com frequência adequada ao custo de perda.
- Periodicamente e ao terminar, copiar para o destino durável da dupla. Não depender somente do salvamento ao final de um processamento longo.
- No Kaggle, confirmar que a versão salva preservou os arquivos de saída; salvar apenas o código não basta.
- No Colab, copiar explicitamente para o Drive montado ou outro destino persistente. `/content` é espaço de trabalho temporário.
- Conferir tamanho e SHA-256 dos arquivos copiados. Criar um marcador de conclusão somente depois da verificação.
- Registrar localização, versão e hash em `results/artifact_index.csv`.
- Testar uma retomada após reiniciar a sessão e reanexar/restaurar os arquivos.

Campos sugeridos do índice: `artifact_id`, `run_id`, `kind`, `owner`, `storage_uri`, `storage_version`, `sha256`, `size_bytes`, `created_at_utc`, `verified_at_utc`.

## 13 Fluxo de trabalho no Kaggle ou Colab

1. Obter a versão correta do código e registrar o commit.
2. Anexar/obter os dados e definir as raízes reais de armazenamento.
3. Configurar segredos e confirmar o acesso ao checkpoint da própria conta.
4. Instalar as dependências mínimas do modelo, preservando o ambiente quando possível.
5. Rodar inventário e inspeção das imagens em CPU.
6. Conferir manifesto, amostras, configuração e mapeamento de classes.
7. Ativar GPU para extração ou treinamento; repetir configuração se a sessão reiniciar.
8. Rodar um lote pequeno, medindo memória e tempo.
9. Executar a configuração planejada, com salvamento e cópias periódicas.
10. Validar, preservar resultados e atualizar o índice de artefatos.
11. Exportar alterações de código/notebook para a branch correspondente.
12. Desligar a GPU ao terminar.

Não há neste README comandos como `python train.py` que pressupõem scripts ainda inexistentes. Acrescentar comandos executáveis depois que as interfaces forem implementadas e testadas.

