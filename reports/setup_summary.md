<!-- reports/setup_summary.md -->

# Resumo histórico da preparação do ambiente

Este documento descreve os testes iniciais de infraestrutura e leitura dos dados. As pendências registradas naquela etapa não representam, por si só, o estado atual do projeto.

O acompanhamento atualizado está em [docs/status.md](../docs/status.md), e os resultados consolidados estão em [reports/README.md](README.md).

## Ambiente e carregamento inicial

O ambiente foi validado com GPU Tesla T4 e Transformers 4.56.2.

O dataset OCT-C8 foi identificado com 24.000 imagens e oito classes:

`AMD, CNV, CSR, DME, DR, DRUSEN, MH, NORMAL`

O DINOv3 ViT-L/16 foi carregado com sucesso.

## Teste inicial de extração

A extração de teste utilizou 16 imagens e produziu vetores de 1.024 dimensões.

Foram confirmados o salvamento e a reutilização de oito blocos na mesma sessão.

Esse teste demonstrou o funcionamento inicial da extração e do armazenamento. Ele não comprova a recuperação dos resultados após o encerramento da sessão.

## Auditoria posterior

A auditoria verificou as 24.000 imagens sem falhas de leitura e identificou:

- 144 grupos de duplicatas exatas.
- 48 grupos presentes em mais de uma divisão.
- Seis grupos com rótulos conflitantes, envolvendo 12 imagens.

As contagens se sobrepõem: um grupo com conflito de rótulos também pode estar presente em mais de uma divisão.

Os metadados disponíveis não permitiram determinar o rótulo correto das imagens conflitantes. Todas as cópias desses grupos foram colocadas em quarentena, sem alteração dos arquivos originais.

## Seleção adotada após a limpeza

A seleção utilizada nos experimentos contém 23.850 imagens:

| Divisão | Imagens |
|---|---:|
| Treino | 18.260 |
| Validação | 2.793 |
| Teste | 2.797 |

Foram excluídas da seleção 138 cópias duplicadas excedentes e 12 imagens com conflito de rótulos.

As exclusões são representadas pelo manifesto. Os arquivos originais continuam preservados no dataset.

O registro da seleção adotada está em [docs/data_approval.md](../docs/data_approval.md).

## Evolução após a preparação

Os relatórios disponíveis documentam:

- Extração completa de embeddings DINOv3 e ResNet-50.
- Seleção de 13 classificadores lineares por backbone.
- Ajuste parcial do DINOv3 em 10% do treino nas sementes 17, 42 e 2026.

A avaliação final no teste permanece pendente.

Os resultados de RETFound, ViT supervisionado e CNN simples ainda precisam ser integrados ao conjunto de arquivos revisado. A recuperação de uma execução em nova sessão também permanece sem evidência de teste concluído.

## Referências

- [Auditoria e limpeza](data_audit/README.md)
- [Resultados dos experimentos](README.md)
- [Protocolo utilizado](../docs/protocol.md)
- [Acompanhamento do projeto](../docs/status.md)