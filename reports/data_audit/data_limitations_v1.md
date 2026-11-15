<!-- reports/data_audit/data_limitations_v1.md -->

# Limitações da auditoria inicial

Este documento registra o alcance da auditoria inicial das 24.000 imagens, anterior à aplicação da seleção utilizada nos experimentos.

Naquela etapa, os dados ainda não estavam congelados e nenhuma exclusão havia sido aplicada à seleção experimental. Posteriormente, foi adotado o manifesto de 23.850 imagens descrito em [docs/data_approval.md](../../docs/data_approval.md).

Os arquivos originais foram preservados. As exclusões posteriores são representadas pelo manifesto.

## Alcance da verificação

A auditoria verificou:

- Leitura dos arquivos.
- Dimensões e canais das imagens.
- Duplicação exata do conteúdo dos arquivos.
- Duplicação exata dos pixels após conversão para RGB.
- Presença de duplicatas entre divisões.
- Conflitos de classe entre imagens idênticas.

Essas verificações não garantem ausência de imagens quase duplicadas, como versões com pequenas alterações de recorte, compressão, brilho ou resolução.

## Identificação de pacientes e origem

A origem clínica e os identificadores dos pacientes não foram confirmados por documentação ou metadados suficientes.

Portanto, não está comprovada a separação por paciente entre treino, validação e teste.

Imagens diferentes podem pertencer ao mesmo paciente ou exame, mesmo quando seus hashes são distintos.

## Relação com o pré-treinamento

Não foi comprovada a independência entre o OCT-C8 e os dados utilizados no pré-treinamento dos modelos avaliados.

A ausência de duplicatas exatas dentro do OCT-C8 não demonstra ausência de sobreposição com conjuntos externos de pré-treinamento.

## Conflitos de rótulos

Foram identificadas imagens idênticas associadas a classes diferentes.

Os metadados disponíveis não permitem decidir qual rótulo é correto. Nenhum rótulo foi corrigido sem evidência.

Na limpeza posterior, todas as cópias dos grupos conflitantes foram colocadas em quarentena e excluídas da seleção experimental.

## Efeito da limpeza posterior

A seleção adotada removeu:

- 138 cópias duplicadas excedentes.
- 12 imagens com conflito de rótulos.

O conjunto passou de 24.000 para 23.850 imagens.

As imagens mantidas conservaram suas divisões originais, mas a exclusão de arquivos alterou a composição e as contagens de treino, validação e teste.

Consequentemente, os resultados devem ser descritos como obtidos na **versão auditada do OCT-C8**, com os critérios de seleção documentados.

## Referências atuais

- [Auditoria e política de limpeza](README.md)
- [Seleção de dados adotada](../../docs/data_approval.md)
- [Protocolo experimental](../../docs/protocol.md)
- [Acompanhamento do projeto](../../docs/status.md)