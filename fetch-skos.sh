rm skos.json
curl https://opentheso.huma-num.fr/openapi/v1/thesaurus/refar-institutions-corporations > skos.json
cat skos.json | jq