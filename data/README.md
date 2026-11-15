# Dados do projeto — OCT-C8

Esta pasta contém os manifestos que definem quais imagens podem ser utilizadas nos experimentos de classificação de OCT. As imagens originais ficam no dataset anexado ao Kaggle; não devem ser adicionadas ao Git.

Os experimentos principais devem utilizar o manifesto final aprovado.

## O que é um manifesto?

Um manifesto é um arquivo CSV com **uma linha por imagem**. Ele registra o identificador, o caminho, a classe, a divisão e informações obtidas na auditoria.

Ele funciona como a lista oficial de imagens de uma execução. Não contém as imagens: o código combina a raiz do dataset com o caminho relativo de cada linha para abri-las.

**As imagens excluídas continuam nas pastas originais.** Por isso, listar diretamente todas as imagens dessas pastas ou usar `ImageFolder` sobre o dataset inteiro reincluiria arquivos removidos da seleção. Os próximos notebooks devem construir seus datasets a partir do manifesto.

## Organização desta pasta

Caminhos relativos à pasta `data/`:

| Caminho | Conteúdo e finalidade |
|---|---|
| `README.md` | Este guia |
| `manifests/octc8_inventory_v1.csv` | Inventário inicial com informações básicas das 24.000 imagens |
| `manifests/class_to_idx.json` | Mapeamento fixo entre nomes e índices das classes |
| `manifests/octc8_manifest_audit_v1.csv` | Manifesto completo, com hashes, dimensões e resultados da auditoria |
| `manifests/candidates/octc8_manifest_candidate_v1.csv` | Seleção de 23.850 imagens após a limpeza, ainda candidata |

Os relatórios e as decisões ficam em `reports/data_audit/`, a partir da raiz do repositório. O arquivo `cleaning_proposal_v1/cleaning_decisions_proposed.csv` registra a ação proposta para cada imagem. O manifesto candidato contém somente as imagens mantidas; os motivos das exclusões devem ser consultados na tabela de decisões.


## Dados auditados e política de limpeza

As 24.000 imagens originais foram lidas sem falhas. A auditoria encontrou 144 grupos de duplicatas exatas, incluindo 48 grupos presentes em mais de uma divisão. Seis grupos apresentaram rótulos conflitantes, envolvendo 12 arquivos. Essas categorias podem se sobrepor.

A seleção candidata aplica as seguintes regras:

1. Colocar todas as cópias de grupos com rótulos conflitantes em quarentena, sem adivinhar ou alterar classes.
2. Para duplicatas sem conflito, manter uma única cópia, priorizando `test`, depois `val` e depois `train`.
3. Dentro da mesma divisão, selecionar a cópia pelo caminho em ordem alfabética.
4. Preservar os arquivos originais; representar exclusões pelo manifesto.
5. Preservar as contagens resultantes, sem adicionar imagens para recuperar o balanceamento original.

Foram excluídas da seleção 138 cópias excedentes e colocados em quarentena 12 arquivos: **150 arquivos a menos, ou 0,625% do conjunto original**.

| Divisão | Original | Duplicatas excedentes | Quarentena | Candidato |
|---|---:|---:|---:|---:|
| Treino | 18.400 | 130 | 10 | 18.260 |
| Validação | 2.800 | 5 | 2 | 2.793 |
| Teste | 2.800 | 3 | 0 | 2.797 |
| **Total** | **24.000** | **138** | **12** | **23.850** |

As verificações automáticas confirmaram a correspondência entre decisões e candidato, a ausência de duplicatas exatas pelos hashes de arquivo e pixels RGB e a presença das oito classes em todas as divisões.

### Classes e distribuição candidata

Não alterar o mapeamento de classes entre modelos ou execuções.

| Classe | Índice | Treino | Validação | Teste |
|---|---:|---:|---:|---:|
| AMD | 0 | 2.300 | 350 | 350 |
| CNV | 1 | 2.257 | 347 | 350 |
| CSR | 2 | 2.300 | 350 | 350 |
| DME | 3 | 2.272 | 349 | 349 |
| DR | 4 | 2.300 | 350 | 350 |
| DRUSEN | 5 | 2.233 | 348 | 349 |
| MH | 6 | 2.300 | 350 | 350 |
| NORMAL | 7 | 2.298 | 349 | 349 |

## Colunas do manifesto auditado e candidato

| Coluna | Significado |
|---|---|
| `image_id` | Identificador derivado do caminho relativo; não identifica o paciente nem detecta duplicação de conteúdo |
| `relative_path` | Caminho da imagem em relação à raiz do dataset |
| `class_name`, `class_id` | Nome da classe e índice fixo |
| `split` | `train`, `val` ou `test` |
| `file_size_bytes` | Tamanho do arquivo em bytes |
| `width`, `height` | Dimensões originais, antes de qualquer transformação |
| `mode`, `channels` | Modo de cor e número de canais originais |
| `image_format`, `n_frames` | Formato e quantidade de quadros |
| `file_sha256` | SHA-256 dos bytes do arquivo |
| `pixel_sha256` | SHA-256 das dimensões e dos pixels após conversão para RGB, conforme o código da auditoria |
| `read_ok` | Resultado da verificação e decodificação da imagem |
| `error_type`, `error_message` | Informações sobre falhas, quando presentes |
| `patient_id`, `patient_id_source` | Paciente e evidência de identificação, quando disponíveis |
| `source_dataset`, `source_evidence` | Origem e evidência, quando confirmadas |
| `dataset_release` | Identificação da distribuição utilizada: `retinal-oct-c8` |

Os campos de paciente e origem permanecem vazios quando não há evidência. Não preencher identificadores de pacientes por suposição a partir dos nomes dos arquivos.

## Como carregar e inspecionar os dados no Kaggle

Adicione o dataset OCT-C8 ao notebook. Os caminhos abaixo correspondem ao ambiente utilizado na auditoria. Confira as entradas e ajuste os caminhos se estiver usando outra sessão ou organização.

O exemplo requer `pandas` e `Pillow`. Não exige GPU nem carregamento de um modelo.

### 1. Abrir o manifesto candidato

```python
from pathlib import Path
import pandas as pd

DATA_ROOT = Path(
    "/kaggle/input/datasets/obulisainaren/retinal-oct-c8"
)

MANIFEST_PATH = Path(
    "/kaggle/working/oct_project/audit/"
    "cleaning_proposal_v1/octc8_manifest_candidate_v1.csv"
)

# Este caminho existe após gerar a proposta ou restaurar seus arquivos.
# Se o manifesto foi anexado como entrada, ajuste MANIFEST_PATH
# para a localização correspondente em /kaggle/input/.
assert DATA_ROOT.is_dir(), "Confira o caminho do dataset."
assert MANIFEST_PATH.is_file(), "Restaure ou localize o manifesto."

manifest = pd.read_csv(
    MANIFEST_PATH,
    dtype={"image_id": str},
    keep_default_na=False,
)

required = {
    "image_id", "relative_path", "class_name", "class_id", "split",
    "file_sha256", "pixel_sha256", "read_ok",
}
assert required.issubset(manifest.columns)
assert manifest["image_id"].is_unique
assert manifest["relative_path"].is_unique
assert set(manifest["split"]) == {"train", "val", "test"}
assert manifest["read_ok"].astype(str).str.lower().eq("true").all()

class_to_idx = {
    "AMD": 0, "CNV": 1, "CSR": 2, "DME": 3,
    "DR": 4, "DRUSEN": 5, "MH": 6, "NORMAL": 7,
}
assert manifest["class_name"].isin(class_to_idx).all()
assert manifest["class_name"].map(class_to_idx).eq(
    manifest["class_id"]
).all()

for column in ["file_sha256", "pixel_sha256"]:
    assert manifest[column].str.fullmatch(r"[0-9a-f]{64}").all()
    assert manifest[column].is_unique

print("Quantidade de imagens:", len(manifest))
print(manifest.groupby("split").size())
display(manifest.head())
```

Para esta versão candidata, esperamos 23.850 linhas. As verificações acima conferem a tabela; não recalculam os hashes de todos os arquivos originais.

Se o repositório estiver disponível no ambiente, uma alternativa para localizar o CSV é:

```python
# Ajuste para a raiz real do seu checkout.
REPO_ROOT = Path("/caminho/para/o/repositorio")
MANIFEST_PATH = (
    REPO_ROOT / "data/manifests/candidates/octc8_manifest_candidate_v1.csv"
)
# Depois, execute novamente a leitura e as verificações acima.
```

### 2. Separar treino, validação e teste

```python
train = manifest.loc[manifest["split"] == "train"].copy()
val = manifest.loc[manifest["split"] == "val"].copy()
test = manifest.loc[manifest["split"] == "test"].copy()

print("Treino:", len(train))
print("Validação:", len(val))
print("Teste:", len(test))
```

Essas divisões já estão definidas. Não aplicar `train_test_split` novamente.

### 3. Localizar e abrir uma imagem de treino

```python
from PIL import Image

row = train.iloc[0]
image_path = DATA_ROOT / row["relative_path"]

assert image_path.is_file(), f"Imagem não encontrada: {image_path}"

with Image.open(image_path) as image:
    image_rgb = image.convert("RGB")

print("ID:", row["image_id"])
print("Classe:", row["class_name"])
print("Índice:", row["class_id"])
print("Caminho:", image_path)
display(image_rgb)
```

A conversão para RGB ocorre em memória e não modifica o arquivo original. Redimensionamento, normalização e demais transformações devem ser definidos e registrados no protocolo de cada modelo.

### 4. Registrar a identidade do manifesto utilizado

```python
import hashlib

manifest_sha256 = hashlib.sha256(
    MANIFEST_PATH.read_bytes()
).hexdigest()

print("Manifesto:", MANIFEST_PATH.name)
print("SHA-256:", manifest_sha256)
```

Registrar o nome e o SHA-256 na configuração de cada execução. O hash identifica os bytes dessa versão; calculá-lo não aprova nem congela automaticamente o manifesto candidato. Depois do congelamento, comparar esse valor com o checksum publicado para a versão final.

## Como obter os manifestos

Os arquivos são produzidos pelo notebook de preparação e auditoria:

- Inventário inicial: `/kaggle/working/oct_project/manifests/octc8_inventory_v1.csv`.
- Manifesto auditado: `/kaggle/working/oct_project/audit/octc8_manifest_audit_v1.csv`.
- Manifesto candidato: `/kaggle/working/oct_project/audit/cleaning_proposal_v1/octc8_manifest_candidate_v1.csv`.

Copiar os CSVs para os destinos indicados na organização desta pasta e preservá-los nas saídas salvas ou no backup. Um arquivo `.ipynb` sozinho não contém os CSVs gerados. Em uma sessão nova, restaurar ou anexar os manifestos; não presumir que `/kaggle/working/` manteve os arquivos anteriores.

## Regras 

- Usar o mesmo manifesto final para DINOv3, RETFound e baselines.
- Carregar somente as imagens listadas nessa versão.
- Preservar `image_id`, `split` e o mapeamento de classes em embeddings e previsões.
- Criar subconjuntos de poucos rótulos somente a partir do treino final, compartilhando as listas de IDs e as seeds entre modelos.
- Calcular as frações sobre o treino final; não reutilizar as contagens anteriores à limpeza.
- Manter validação e teste fixos. Usar validação para seleção de configurações e reservar o teste para avaliação final.
- Não reincluir arquivos excluídos nem corrigir rótulos sem evidência e registro.
- Se alguma decisão mudar, regenerar o manifesto, validar novamente e publicar uma nova versão. Não editar silenciosamente um manifesto congelado.

## Limitações e congelamento

A auditoria cobre leitura e duplicação exata de arquivos e pixels RGB. Não comprova ausência de imagens quase duplicadas, separação por paciente ou independência em relação aos dados de pré-treinamento dos modelos. Essas limitações devem acompanhar os resultados.

A limpeza alterou as divisões originais, inclusive o conjunto de teste. Descrever os experimentos como realizados na **versão auditada do OCT-C8**, informando as contagens e a política de seleção.

Para concluir o congelamento: registrar a revisão efetivamente realizada, salvar o manifesto final, seu checksum e as contagens, e compartilhar a mesma versão entre todos os notebooks. Até lá, o candidato serve para inspeção e preparação do código.
