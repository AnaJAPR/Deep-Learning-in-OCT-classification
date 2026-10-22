# Auditoria e limpeza do OCT-C8


## Resultado

Todas as 24.000 imagens foram lidas sem falhas.

Foram encontrados 144 grupos de duplicatas exatas, dos quais 48
estavam presentes em mais de uma divisão. Seis grupos apresentaram
rótulos conflitantes, envolvendo 12 arquivos.

Os grupos com conflito podem também apresentar duplicação entre
divisões; essas contagens não devem ser somadas como categorias
independentes.

| Divisão | Original | Cópias excedentes removidas | Quarentena | Candidato |
|---|---:|---:|---:|---:|
| Treino | 18.400 | 130 | 10 | 18.260 |
| Validação | 2.800 | 5 | 2 | 2.793 |
| Teste | 2.800 | 3 | 0 | 2.797 |
| Total | 24.000 | 138 | 12 | 23.850 |

## Política aplicada

1. Imagens idênticas com rótulos diferentes:
   todas as cópias foram colocadas em quarentena.
   Não houve correção de rótulos sem evidência.

2. Duplicatas sem conflito:
   foi mantida uma cópia por grupo, com prioridade
   teste > validação > treino.

3. Cópias dentro da mesma divisão:
   foi mantido o primeiro caminho em ordem alfabética.

4. Os arquivos originais foram preservados.
   As exclusões são representadas pelo manifesto.

5. A pequena diferença nas contagens entre classes foi preservada.
   Nenhuma imagem foi adicionada para recuperar o balanceamento.

## Validações realizadas

- Identificadores únicos.
- Correspondência entre decisões e manifesto candidato.
- Preservação de caminhos, classes, divisões e hashes das imagens mantidas.
- Ausência de hashes de arquivo e de pixels RGB repetidos no candidato.
- Contagens consistentes antes e depois da limpeza.
- Presença das oito classes em treino, validação e teste.

## Arquivos de referência

- `data/manifests/octc8_manifest_audit_v1.csv`:
  inventário auditado completo das 24.000 imagens.

- `reports/data_audit/cleaning_proposal_v1/cleaning_decisions_proposed.csv`:
  decisões propostas por imagem.

- `reports/data_audit/cleaning_proposal_v1/label_conflicts_quarantine.csv`:
  os 12 arquivos com conflito de rótulo.

- `data/manifests/candidates/octc8_manifest_candidate_v1.csv`:
  seleção candidata de 23.850 imagens.

- `reports/data_audit/cleaning_proposal_v1/counts_validation_v1.csv`:
  contagens verificadas por classe e divisão.

- `reports/data_audit/cleaning_proposal_v1/split_totals_validation_v1.csv`:
  totais verificados por divisão.

Os caminhos acima são relativos à raiz do repositório.

## Orientações para os próximos notebooks

- Carregar as imagens a partir das linhas do manifesto final.
- Não usar a listagem completa das pastas como seleção de dados:
  os arquivos excluídos continuam presentes no dataset original.
- Construir o caminho de cada imagem usando DATA_ROOT / relative_path.
- Respeitar as colunas split, class_name e class_id.
- Não criar novas divisões de treino, validação e teste.
- Não reincluir imagens excluídas ou em quarentena.
- Gerar os subconjuntos de poucos rótulos apenas a partir do treino final.
- Compartilhar os mesmos subconjuntos e seeds entre os modelos.
- Manter validação e teste fixos entre os experimentos.
- Registrar a versão e o checksum do manifesto em cada execução.
- Associar embeddings e previsões ao image_id correspondente.

## Limitações

A ausência de duplicatas exatas não comprova ausência de imagens
quase duplicadas ou separação por paciente.

A origem clínica e os identificadores de pacientes não foram
confirmados. Também não foi comprovada a independência em relação
aos dados de pré-treinamento dos modelos.

A limpeza alterou as divisões originais, inclusive a avaliação.
Os resultados devem ser descritos como obtidos na versão auditada
do OCT-C8, com essas contagens e critérios de seleção.

