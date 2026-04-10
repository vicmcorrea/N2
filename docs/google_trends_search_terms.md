# Google Trends Search Terms

Source used for these lists

username = atvictor_8Mria
password = nnD2_ICpH0~AiW


curl 'https://realtime.oxylabs.io/v1/queries' \
--user "atvictor_8Mria:nnD2_ICpH0~AiW" \
-H "Content-Type: application/json" \
-d '{
        "source": "amazon_product",
        "query": "B07FZ8S74R",
        "geo_location": "90210",
        "parse": true
    }'



curl 'https://realtime.oxylabs.io/v1/queries' \
--user 'atvictor_8Mria:nnD2_ICpH0~AiW' \
-H 'Content-Type: application/json' \
-d '{
        "source": "universal",
        "url": "https://sandbox.oxylabs.io/"
    }'




import requests
from pprint import pprint

# Structure payload.
payload = {
    'source': 'universal',
    'url': 'https://sandbox.oxylabs.io/',
    # 'render': 'html', # If page type requires
}

# Get response.
response = requests.request(
    'POST',
    'https://realtime.oxylabs.io/v1/queries',
# Your credentials go here
    auth=('atvictor_8Mria', 'nnD2_ICpH0~AiW'),
    json=payload,
)

# Instead of response with job status and results url,
# this will return the JSON response with results.
pprint(response.json())



- `docs/results/frozen_results_snapshot_2026_03_24.md`

## 1. Word2Vec Drift Terms

```text
intervenção
planalto
renovação
troca
inaceitável
oposto
perigoso
crítico
contradição
excepcional
inédito
exposição
bloqueio
típico
alvo
```

## 2. TF-IDF Drift Terms

```text
crise
trabalhador
saúde
salário
emenda
eleição
previdência
provisório
preço
mínimo
político
voto
real
partido
destaque
```

## 3. Stable Controls

```text
juridicidade
orçamentária
recurso
trabalho
público
social
ensino
votação
potável
direito
inteligente
complicado
gigantesco
expresso
prejudicial
posterior
vento
altíssimo
sincero
altivez
```

## 4. Theory Seeds

```text
democracia
corrupção
reforma
economia
liberdade
```

## 5. Full Shared Panel

```text
intervenção
planalto
renovação
troca
inaceitável
oposto
perigoso
crítico
contradição
excepcional
inédito
exposição
bloqueio
típico
alvo
crise
trabalhador
saúde
salário
emenda
eleição
previdência
provisório
preço
mínimo
político
voto
real
partido
destaque
juridicidade
orçamentária
recurso
trabalho
público
social
ensino
votação
potável
direito
inteligente
complicado
gigantesco
expresso
prejudicial
posterior
vento
altíssimo
sincero
altivez
democracia
corrupção
reforma
economia
liberdade
```
