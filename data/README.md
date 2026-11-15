# Dados do projeto — OCT-C8

Esta pasta versiona metadados e listas, não as imagens originais.

## Arquivos

| Caminho relativo a data/ | Finalidade |
|---|---|
| `manifests/octc8_inventory_v1.csv` | Inventário inicial |
| `manifests/octc8_manifest_audit_v1.csv` | Auditoria das 24.000 imagens |
| `manifests/candidates/octc8_manifest_candidate_v1.csv` | Seleção adotada de 23.850 imagens |
| `manifests/class_to_idx.json` | Mapeamento fixo de classes |
| `splits/registry.json` | Hashes e listas geradas pelo notebook 02; status histórico provisório |
| `splits/train_*.csv` | Frações e sementes do treino |
| `splits/val_fixed.csv` e `splits/test_fixed.csv` | Divisões fixas |

O manifesto adotado tem SHA-256 `80d6eedc883410b47beeee6b1c72e72d69309ba38ac2595fc8f2590e6928103d`. O nome do arquivo foi preservado. Ver `docs/data_approval.md` (a partir da raiz) para aprovação e significado do status histórico.

## Contagens

Treino: 18.260. Validação: 2.793. Teste: 2.797. Total: 23.850.
Treino por fração: 1%=180; 5%=910; 10%=1.824; 25%=4.564; 100%=18.260.

As exclusões do manifesto representam 138 duplicatas excedentes e 12 imagens em quarentena. Arquivos originais continuam nas pastas do dataset; por isso, não carregar todas as pastas com ImageFolder sem aplicar a seleção.

## Como carregar

Exemplo executado a partir da raiz do repositório; ajuste DATA_ROOT para o dataset anexado.

```python
from pathlib import Path
import hashlib
import pandas as pd
from PIL import Image

MANIFEST_PATH = Path('data/manifests/candidates/octc8_manifest_candidate_v1.csv')
DATA_ROOT = Path('/kaggle/input/datasets/obulisainaren/retinal-oct-c8')
assert hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest() == '80d6eedc883410b47beeee6b1c72e72d69309ba38ac2595fc8f2590e6928103d'
manifest = pd.read_csv(MANIFEST_PATH, dtype={'image_id': str}, keep_default_na=False)
assert len(manifest) == 23850 and manifest.image_id.is_unique
row = manifest.loc[manifest.split.eq('train')].iloc[0]
path = DATA_ROOT / row.relative_path
assert path.is_file(), path
with Image.open(path) as image:
    example = image.convert('RGB').copy()
```

Para treinar em uma fração, use os IDs da lista correspondente em `splits/`; não faça novo sorteio. Preserve classe, divisão e ID em todas as saídas. A normalização e o redimensionamento devem seguir a configuração de cada modelo.

Colunas reais do manifesto incluem `image_id`, `relative_path`, `class_name`, `class_id`, `split`, `file_sha256`, `pixel_sha256` e `read_ok`. Não substituir por nomes antigos propostos como `sha256_file` ou `readable`.

## Limitações

A auditoria não comprova separação por paciente, ausência de imagens quase duplicadas nem independência do pré-treinamento. A limpeza também alterou a composição do teste. Descrever os dados como a versão auditada do OCT-C8.
