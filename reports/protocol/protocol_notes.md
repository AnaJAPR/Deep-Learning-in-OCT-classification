# Protocolo experimental — registro

Status do protocolo: proposta para revisão conjunta.
Status dos dados: provisional.
SHA-256 do manifesto: 80d6eedc883410b47beeee6b1c72e72d69309ba38ac2595fc8f2590e6928103d.

A redução de rótulos se aplica apenas ao treino auditado. As 2.793 imagens de validação
continuam rotuladas e são utilizadas para escolher configurações. Portanto, o orçamento
de anotação para ajuste e seleção soma os rótulos do subconjunto de treino e os 2.793
rótulos de validação. Os 2.797 rótulos de teste são reservados à avaliação final.

As divisões são fixas e os subconjuntos aninhados são compartilhados por todos os modelos.
As contagens exatas estão em data/splits/counts.csv e annotation_budget.csv.
Em 100%, não repetir um classificador determinístico com a mesma configuração e dados.

O piloto de pixels testa integração e não constitui resultado de DINOv3 ou RETFound.
A normalização específica e o orçamento de busca ainda exigem revisão conjunta.
O teste levemente desbalanceado não exige igualdade de accuracy e balanced accuracy.
As limitações de paciente, pré-treinamento e geometria estão em protocol.json.

