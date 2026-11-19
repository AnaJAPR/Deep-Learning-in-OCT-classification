# Seleção de dados adotada

Registro documental atualizado em 15/11/2026. Esta data não é atribuída retrospectivamente como data da aprovação original.

Manifesto utilizado: `data/manifests/candidates/octc8_manifest_candidate_v1.csv`.

SHA-256: `80d6eedc883410b47beeee6b1c72e72d69309ba38ac2595fc8f2590e6928103d`.

O nome histórico contém “candidate”, mas os experimentos principais utilizaram exatamente essa seleção de 23.850 imagens. O protocolo da execução registra `data_approved=true` e `reviewers="Paula Eduarda de Lima"`. O manifesto revisado foi aceito sem alteração. 

A limpeza excluiu 138 cópias excedentes e colocou 12 imagens com conflito de rótulos em quarentena. Os arquivos originais não foram modificados. A versão de seleção é definida pelo hash, e não pelo nome do arquivo.

`data/splits/registry.json` e `reports/protocol/data_status.json` foram gerados quando o status era provisório. São registros históricos preservados. O protocolo atual está em `configs/protocol_current.json`, sem substituir os JSONs históricos ou regravar o manifesto.

Antes da avaliação final conjunta, Ana Júlia deve confirmar o uso da mesma seleção e registrar sua revisão efetiva. Não é necessário regenerar listas se dados e decisões permanecerem idênticos.

Pacientes, independência do pré-treinamento e ausência de quase duplicatas não foram comprovados.

## Revisão documental em 19/11/2026

O manifesto e seus bytes foram novamente conferidos: o SHA-256 acima permanece correto. Nenhuma nova aprovação de Ana Júlia é atribuída por esta atualização.

**Revisão nominal de Ana Júlia: ainda não registrada.** Quando realizada, acrescentar data real, nome da revisora, hash conferido, listas utilizadas, verificações realizadas e decisão. Não preencher retroativamente nem alterar os registros históricos provisórios. A revisão conjunta deve confirmar o uso da mesma seleção nos modelos de ambas.
