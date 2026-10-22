Ambiente validado com Tesla T4 e Transformers 4.56.2. OCT-C8 identificado com 24.000 imagens e oito classes. DINOv3 ViT-L/16 carregado com sucesso. Extração realizada em 16 imagens, gerando vetores de dimensão 1.024. Salvamento e reutilização de oito blocos confirmados na mesma sessão. Pendências: acesso ao RETFound, auditoria completa dos dados e teste de retomada em uma nova sessão.


Auditoria dos dados: 24.000 imagens verificadas, sem falhas de leitura. Foram encontrados 144 grupos de duplicatas exatas, incluindo 48 grupos presentes em mais de uma divisão, e seis grupos com rótulos conflitantes. A proposta de limpeza está em revisão. 

Arquivos com SHA-256 de conteúdo e de pixels coincidentes, associados a classes diferentes. Os metadados disponíveis não permitem determinar o rótulo correto. Todas as cópias do grupo foram excluídas dos experimentos e preservadas nos dados originais.