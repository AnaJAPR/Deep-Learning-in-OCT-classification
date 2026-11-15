# Saídas históricas do notebook 02

Esta pasta preserva o pacote gerado na etapa de definição do protocolo. `protocol.json`, `data_status.json` e `protocol_notes.md` registram o estado provisório daquela etapa; não representam sozinhos o status posterior dos experimentos.

O protocolo atualmente documentado está em `configs/protocol_current.json` e `docs/protocol.md`. A seleção adotada está identificada em `docs/data_approval.md`. Não editar retrospectivamente os JSONs nem os checksums históricos.

O piloto em `pilot_pixels/` verifica integração com pixels; não é um resultado de DINOv3 ou RETFound.

Para montar o input dos notebooks: copiar `manifest_used.csv` desta pasta para a raiz do pacote e copiar a pasta `data/splits/` do repositório para `data/splits/` dentro do pacote. Preservar os bytes e conferir os hashes do registry.
