# Validador de Dados - tb_fato_categoria

Este artefato YAML define as regras de validação de Data Quality para a tabela `tb_fato_categoria` no domínio `sensitive-trusted.sellout` do Grupo Boticário.

## Estrutura do Artefato
- **owner**: Responsável pelo validador (e-mail corporativo).
- **production_table**: Tabela de produção monitorada.
- **sandbox_table**: Tabela de desenvolvimento/validação.
- **checks**: Lista de regras de validação aplicadas, incluindo rastreabilidade da iniciativa.

## Check Implementado
- `emptyTable`: Valida se a tabela está vazia, garantindo que a carga foi realizada corretamente.

## Caminho do Artefato
```
validador_dados/eng/sensitive-trusted/sellout/tb_fato_categoria/
├── tb_fato_categoria.yaml
└── README.md
```

## Observações
- Sempre mantenha o campo `initiative_id` preenchido no padrão `inicXXXX`.
- Não modifique o campo `production_table` manualmente, ele deve refletir a tabela oficial de produção.
- Para novos checks, consulte o time de Engenharia de Dados.
