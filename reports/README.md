# Relatórios dos experimentos OCT-C8

Esta pasta reúne configurações, registros de execução e resultados
do projeto de classificação de imagens OCT com poucos rótulos.

## Estado atual

Foram concluídas a extração completa de embeddings e a seleção de
classificadores lineares para DINOv3 ViT-L/16 e ResNet-50.

Cada modelo possui 13 configurações selecionadas:
- Frações de 1%, 5%, 10% e 25%, com sementes 17, 42 e 2026.
- Fração de 100%, executada uma vez para evitar repetições determinísticas.

Os resultados consolidados são de validação.
A avaliação final no teste ainda está pendente.

O piloto de uma época do ajuste parcial DINOv3 foi executado.
As execuções principais do ajuste parcial ainda não estão consolidadas
nesta tabela.

## Dados utilizados

O manifesto revisado contém 23.850 imagens:

| Divisão | Imagens |
|---|---:|
| Treino | 18.260 |
| Validação | 2.793 |
| Teste | 2.797 |

SHA-256 do manifesto:

`80d6eedc883410b47beeee6b1c72e72d69309ba38ac2595fc8f2590e6928103d`

Ordem das classes:

`AMD, CNV, CSR, DME, DR, DRUSEN, MH, NORMAL`

Somente o treino é reduzido. A validação permanece fixa e utiliza
2.793 imagens rotuladas, cujo custo de anotação também deve ser considerado.

| Fração | Imagens de treino |
|---|---:|
| 1% | 180 |
| 5% | 910 |
| 10% | 1.824 |
| 25% | 4.564 |
| 100% | 18.260 |

Os modelos reutilizam as mesmas listas de imagens para cada fração
e semente.

## Protocolo dos modelos congelados

Os pesos dos backbones permanecem fixos durante a extração.

- DINOv3: representação CLS final, com 1.024 dimensões.
- ResNet-50: saída do global average pooling antes da camada
  classificadora, com 2.048 dimensões.

As imagens são convertidas para RGB e redimensionadas integralmente
para 224 × 224 com interpolação bicúbica. A normalização é específica
de cada modelo.

O classificador é uma regressão logística precedida de StandardScaler.
O scaler é ajustado exclusivamente no subconjunto de treino da execução.

São comparados os valores de C:
`0.001, 0.01, 0.1, 1.0, 10.0`.

A seleção utiliza macro-F1 na validação.
Candidatos com aviso de não convergência são descartados pela rotina.
Em caso de empate, é escolhido o menor C.

Os dados de teste não são usados para escolher configurações.

## Organização

- `embeddings/`: metadados dos modelos e configurações de extração.
- `pilots/`: medições de desempenho e relatórios dos pilotos disponíveis.
- `linear_probe/dinov3/`: relatórios das execuções lineares DINOv3.
- `linear_probe/resnet50/`: relatórios das execuções lineares ResNet-50.
- `results/validation_summary.csv`: uma linha por execução selecionada.

As subpastas das execuções preservam os identificadores de fração,
semente e configuração.

## Como interpretar a tabela consolidada

`validation_summary.csv` contém 26 linhas, correspondentes a
13 execuções selecionadas por modelo.

Macro-F1 é a métrica principal. Também são registrados accuracy,
balanced accuracy, AUROC e recall por classe.

Os valores são resultados de validação utilizados na seleção de C.
Não devem ser apresentados como desempenho final no teste.

Campos vazios indicam informação não disponível ou não aplicável.
Por exemplo, melhor época não se aplica ao classificador linear.

Os tempos de ajuste extraídos de trials.json não incluem
necessariamente todas as etapas de avaliação e salvamento.

Para comparar modelos, parear a mesma fração e semente e conferir
o identificador da amostra de treino.

Médias e desvios entre sementes devem ser calculados separadamente.
O desvio-padrão entre sementes não é um intervalo de confiança.

## Artefatos preservados fora do Git

Embeddings, classificadores treinados, checkpoints e arquivos ZIP
são preservados fora do repositório.

Backups de referência:
- DINOv3: `DINOV3_extracao_completa.zip`.
- ResNet-50: `80d6eedc8834_a305b2c7_backup (5)(2).zip`.

Ambos contêm embeddings e resultados dos classificadores lineares.

Adicionar aqui a localização efetiva de armazenamento de cada backup,
sua versão e seu SHA-256. O nome do arquivo, sozinho, não garante
que outra integrante consiga acessá-lo.

Os caminhos em selection_lock.json são relativos à raiz do backup.
Se os relatórios forem reorganizados no repositório, preservar
os registros originais e documentar o mapeamento de caminhos.

## Limitações

- A separação por paciente não foi comprovada.
- A independência em relação aos dados de pré-treinamento não foi comprovada.
- A auditoria removeu duplicatas exatas; imagens quase duplicadas
  não foram excluídas por essa verificação.
- O redimensionamento integral pode alterar a proporção da imagem.
- A geometria de processamento da ResNet-50 difere da transformação
  oficial de seus pesos.
- Diferenças entre modelos envolvem arquitetura, dados, escala e
  objetivo de pré-treinamento.
- Os resultados atuais não incluem avaliação externa.





### Ajuste parcial do DINOv3 — 10% do treino, semente 17

Foram utilizadas 1.824 imagens de treino e 2.793 de validação.
O ajuste alterou somente os dois últimos blocos do DINOv3 e a
camada classificadora: 25.202.696 parâmetros treináveis.

Foram comparadas as taxas 1e-5 e 3e-5, com limite de 15 épocas
e parada após cinco épocas sem melhora na validação.

| Taxa | Épocas executadas | Melhor época | Macro-F1 de validação |
|---|---:|---:|---:|
| 1e-5 | 15 | 12 | 0,902925 |
| 3e-5 | 13 | 8 | 0,919664 |

A configuração selecionada foi lr=3e-5, com o checkpoint da época 8.
Ela apresentou accuracy de 0,920158, balanced accuracy de 0,919962
e AUROC macro de 0,993183.

DRUSEN teve o menor recall (0,772989), seguida por DME (0,851003)
e CNV (0,853026).

Os tempos registrados por época, somados, foram aproximadamente
26,9 minutos para lr=1e-5 e 23,6 minutos para lr=3e-5.
Esses tempos não representam toda a duração da sessão.

Os resultados são de validação e correspondem a uma única semente.
A avaliação final no teste ainda não foi executada.
