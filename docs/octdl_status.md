# Estado da avaliação externa OCTDL — 19/11/2026

O planejamento marca tarefas OCTDL como concluídas, mas o pacote de repositório revisado não contém evidências suficientes para verificá-las. OCTDL fica **fora dos resultados comprovados desta entrega documental**, até a integração dos artefatos. Não se afirma que nunca foi executado.

## Para incluir uma avaliação já realizada

- Registrar origem e versão dos dados, número de imagens e pacientes quando disponíveis.
- Documentar a compatibilidade de AMD, DME e NORMAL, e o mapeamento dos rótulos.
- Preservar manifesto externo, IDs, configuração de processamento e revisão do backbone.
- Preservar o classificador de três classes treinado no OCT-C8, escolhido somente na validação OCT-C8.
- Salvar previsões e métricas do mesmo classificador no teste OCT-C8 restrito às três classes e no OCTDL.
- Calcular delta = macro-F1 OCT-C8 (três classes) − macro-F1 OCTDL (três classes). Positivo indica queda externa.
- Registrar que nenhum ajuste foi escolhido pelos rótulos externos e interpretar diferenças de população, rótulos e aquisição.

Se esses artefatos não puderem ser recuperados, marcar a avaliação como não integrada/trabalho futuro no planejamento e no artigo. Não substituir a comparação por um resultado OCT-C8 de oito classes.
