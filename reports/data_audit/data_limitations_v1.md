# Limitações da auditoria

- A auditoria verifica leitura, dimensões e duplicação exata de arquivos
  e pixels RGB. Não exclui a existência de imagens quase duplicadas.
- A identificação de pacientes e a origem clínica das imagens ainda
  não foram confirmadas por documentação ou metadados.
- Portanto, não está comprovada a separação por paciente entre treino,
  validação e teste.
- Não foi comprovada a independência entre o OCT-C8 e os dados de
  pré-treinamento dos modelos avaliados.
- A ausência de duplicatas exatas não comprova independência clínica
  ou ausência de sobreposição com o pré-treinamento.
- As divisões originais foram preservadas nesta auditoria.
- Nenhuma imagem foi excluída ou teve seu rótulo alterado automaticamente.
- Os dados ainda não estão congelados para os experimentos principais.
