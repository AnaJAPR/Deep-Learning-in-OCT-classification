# Classificação de OCT com poucos dados rotulados

**Modelos Fundacionais Visuais Gerais versus Especializados para Classificação de OCT com Poucos Dados Rotulados**

Paula Eduarda de Lima e Ana Júlia Amaro Pereira Rocha.

Investigamos se representações gerais do DINOv3 podem igualar ou superar RETFound OCT, especializado em retina, quando há poucos exemplos rotulados de treino.

## Estado documentado em 15/11/2026

- DINOv3 ViT-L/16 e ResNet-50: extração completa e 13 classificadores lineares selecionados por modelo.
- DINOv3: ajuste parcial em 10% do treino nas sementes 17, 42 e 2026; duas taxas por semente.
- Tabela consolidada: 29 resultados selecionados de validação.
- Avaliação final no teste e resultados dos modelos de Ana Júlia: ainda não documentados neste conjunto de arquivos.
- Ajuste parcial em 1% e OCTDL: extensões não executadas nos relatórios disponíveis.

## Dados e protocolo

O OCT-C8 auditado contém 23.850 imagens: 18.260 de treino, 2.793 de validação e 2.797 de teste. O manifesto adotado, seu hash e a aprovação registrada estão em [docs/data_approval.md](docs/data_approval.md).

| Fração de treino | Imagens |
|---|---:|
| 1% | 180 |
| 5% | 910 |
| 10% | 1.824 |
| 25% | 4.564 |
| 100% | 18.260 |

As frações usam piso por classe após a auditoria. As sementes são 17, 42 e 2026; as amostras são aninhadas em cada semente. Validação e teste permanecem fixos. O custo de rótulos da validação também deve ser reportado. Em 100%, os classificadores determinísticos são executados uma vez.

Treino ajusta os modelos e o StandardScaler. Validação seleciona configurações por macro-F1. Teste é reservado à avaliação final. Nunca listar todas as imagens das pastas como substituição do manifesto.

## Organização real do repositório

| Caminho | Conteúdo |
|---|---|
| `data/manifests/` | Inventários, manifesto adotado e mapeamento de classes |
| `data/splits/` | Subconjuntos, validação/teste fixos e registro histórico |
| `configs/protocol_current.json` | Consolidação do protocolo utilizado por Paula |
| `docs/` | Aprovação dos dados, protocolo e pendências |
| `notebooks/` | Preparação, protocolo/piloto e execução dos modelos |
| `src/oct_protocol.py` | Subconjuntos, processamento e métricas |
| `src/oct_experiments.py` | Verificação das listas, embeddings e classificadores |
| `src/oct_gpu.py` | Backbones, benchmark e ajuste parcial |
| `reports/data_audit/` | Auditoria e decisões de limpeza |
| `reports/protocol/` | Saídas históricas do notebook 02, incluindo piloto de pixels |
| `reports/embeddings/` | Identidade e conclusão das extrações |
| `reports/pilots/` | Benchmarks disponíveis |
| `reports/linear_probe/` | Busca e avaliação dos classificadores lineares |
| `reports/partial_ft/` | Ajuste parcial, históricos e seleção |
| `reports/results/` | Tabela por execução e índice de artefatos |
| `figures/` | Exemplos de imagens já presentes |

Pastas planejadas só devem ser anunciadas como implementadas quando contiverem arquivos. Pesos, embeddings, ZIPs e classificadores serializados ficam fora do Git.

## Execução

1. Anexar as imagens OCT-C8 e o pacote do protocolo no Kaggle.
2. Usar o mesmo manifesto e listas deste repositório, conferindo hashes.
3. Executar a instalação antes dos imports. O notebook verifica as versões carregadas e informa quando é necessário reiniciar.
4. Selecionar apenas as etapas desejadas nos controles do notebook 03.
5. Para retomar, restaurar os artefatos e usar a mesma configuração. `last.pt` permite retomar na fronteira entre épocas.
6. Preservar arquivos de saída e verificar checkpoints antes da avaliação final.

O pacote esperado por `verify_lists` contém `manifest_used.csv` e `data/splits/registry.json` sob uma mesma raiz. No repositório, o primeiro está em `reports/protocol/manifest_used.csv` e as listas estão em `data/splits/`. Monte esse pacote sem alterar os bytes dos arquivos ao anexar ao Kaggle.

O notebook 03 exporta módulos embutidos. Ao editar o código, mantenha essa cópia e `src/` sincronizados. Alterações de código/configuração podem mudar os identificadores das execuções; não altere os hashes históricos manualmente.

## Modelos de Paula

DINOv3 usa `facebook/dinov3-vitl16-pretrain-lvd1689m`, revisão `ea8dc2863c51be0a264bab82070e3e8836b02d51`, vetor CLS final de 1.024 dimensões. ResNet-50 usa `ResNet50_Weights.IMAGENET1K_V2`, global average pooling antes da FC, com 2.048 dimensões. Metadados completos em `reports/embeddings/`.

O ambiente verificado usa Transformers 4.56.2, Hugging Face Hub 0.36.2 e Safetensors 0.8.0. Não substituir PyTorch/CUDA indiscriminadamente; consultar os registros de ambiente de cada execução. Tokens ficam nos Secrets e não devem ser versionados.

Imagens são convertidas para RGB e redimensionadas integralmente para 224 × 224, com interpolação bicúbica e sem recorte. Isso altera a proporção original e difere da geometria oficial dos pesos ResNet V2. Transformações de RETFound e ViT precisam de registros próprios.

## Resultados e limitações

Consulte [reports/README.md](reports/README.md). Os resultados disponíveis são de validação. Não foi comprovada separação por paciente nem independência dos dados de pré-treinamento. A auditoria remove duplicatas exatas, mas não garante ausência de imagens quase duplicadas. Diferenças de arquitetura, escala e objetivo de pré-treinamento também afetam a comparação.

## Próximas entregas

Integrar resultados de Ana Júlia, encerrar as escolhas, avaliar no teste, consolidar figuras e preparar relatório/slides para 24/11/2026. Acompanhar em [docs/status.md](docs/status.md).
