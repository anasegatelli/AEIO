-- ========================================================================
-- Objeto......: create_tb_fato_categoria
-- Camada......: sensitive-trusted
-- Version.....: 0.0.1
-- Data Criacao: 2026-03-22
-- Data Update.: 2026-03-22
-- Squad.......: eng
-- Descricao...: Tabela que centraliza as informações de categoria de mercado da Iqvia, utilizada para análises de vendas e performance de produtos no contexto Sellout
-- ========================================================================

CREATE TABLE IF NOT EXISTS sellout.tb_fato_categoria (
    -- Identificadores
    cod_periodo_grupo_fk STRING OPTIONS(description="Código do período do grupo (chave estrangeira)"),
    cod_mercado_fk STRING OPTIONS(description="Código do mercado (chave estrangeira)"),
    cod_pdv_negocio_fk STRING OPTIONS(description="Código do ponto de venda de negócio (chave estrangeira)"),
    cod_grupo_produto_negocio_fk STRING OPTIONS(description="Código do grupo de produto de negócio (chave estrangeira)"),
    id_fcc_rds STRING OPTIONS(description="Identificador FCC RDS"),

    -- Quantidades
    qt_unidade_categoria INT64 OPTIONS(description="Quantidade de unidades na categoria"),
    qt_unidade_designada_categoria INT64 OPTIONS(description="Quantidade de unidades designadas na categoria"),

    -- Valores (Moeda Local)
    vlr_preco_lista_moeda_local_categoria NUMERIC OPTIONS(description="Valor do preço de lista em moeda local da categoria"),
    vlr_ppp_moeda_local_categoria NUMERIC OPTIONS(description="Valor PPP em moeda local da categoria"),
    vlr_consumo_moeda_local_categoria NUMERIC OPTIONS(description="Valor de consumo em moeda local da categoria"),
    vlr_preco_personalizado_moeda_local_cat NUMERIC OPTIONS(description="Valor do preço personalizado em moeda local da categoria"),
    vlr_preco_privado_moeda_local_categoria NUMERIC OPTIONS(description="Valor do preço privado em moeda local da categoria"),
    vlr_preco_nao_varejo_moeda_local_cat NUMERIC OPTIONS(description="Valor do preço não varejo em moeda local da categoria"),
    vlr_preco_pmc_moeda_local_categoria NUMERIC OPTIONS(description="Valor do preço PMC em moeda local da categoria"),
    vlr_preco_ppp_tipo_pdv_moeda_local_cat NUMERIC OPTIONS(description="Valor PPP por tipo de PDV em moeda local da categoria"),
    vlr_preco_consumo_tipo_pdv_moeda_local_cat NUMERIC OPTIONS(description="Valor de consumo por tipo de PDV em moeda local da categoria"),
    vlr_preco_ppp_consumo_moeda_local_cat NUMERIC OPTIONS(description="Valor PPP de consumo em moeda local da categoria"),

    -- Valores (USD)
    vlr_preco_lista_usd_categoria NUMERIC OPTIONS(description="Valor do preço de lista em USD da categoria"),
    vlr_ppp_usd_categoria NUMERIC OPTIONS(description="Valor PPP em USD da categoria"),
    vlr_consumo_usd_categoria NUMERIC OPTIONS(description="Valor de consumo em USD da categoria"),
    vlr_preco_personalizado_usd_categoria NUMERIC OPTIONS(description="Valor do preço personalizado em USD da categoria"),
    vlr_preco_privado_usd_categoria NUMERIC OPTIONS(description="Valor do preço privado em USD da categoria"),
    vlr_preco_nao_varejo_usd_categoria NUMERIC OPTIONS(description="Valor do preço não varejo em USD da categoria"),
    vlr_preco_pmc_usd_categoria NUMERIC OPTIONS(description="Valor do preço PMC em USD da categoria"),
    vlr_preco_ppp_tipo_pdv_usd_categoria NUMERIC OPTIONS(description="Valor PPP por tipo de PDV em USD da categoria"),
    vlr_preco_consumo_tipo_pdv_usd_categoria NUMERIC OPTIONS(description="Valor de consumo por tipo de PDV em USD da categoria"),
    vlr_preco_ppp_consumo_usd_categoria NUMERIC OPTIONS(description="Valor PPP de consumo em USD da categoria"),

    -- Fatores (Moeda Local)
    ftr_unidade_categoria FLOAT64 OPTIONS(description="Fator unidade da categoria"),
    ftr_unidade_alternativa_categoria FLOAT64 OPTIONS(description="Fator unidade alternativa da categoria"),
    ftr_unidade_designada_categoria FLOAT64 OPTIONS(description="Fator unidade designada da categoria"),
    ftr_preco_lista_moeda_local_categoria FLOAT64 OPTIONS(description="Fator preço de lista em moeda local da categoria"),
    ftr_preco_ppp_moeda_local_categoria FLOAT64 OPTIONS(description="Fator PPP em moeda local da categoria"),
    ftr_consumo_moeda_local_categoria FLOAT64 OPTIONS(description="Fator de consumo em moeda local da categoria"),
    ftr_preco_privado_moeda_local_categoria FLOAT64 OPTIONS(description="Fator preço privado em moeda local da categoria"),
    ftr_preco_nao_varejo_moeda_local_cat FLOAT64 OPTIONS(description="Fator preço não varejo em moeda local da categoria"),
    ftr_preco_pmc_moeda_local_categoria FLOAT64 OPTIONS(description="Fator preço PMC em moeda local da categoria"),
    ftr_preco_ppp_tipo_pdv_moeda_local_cat FLOAT64 OPTIONS(description="Fator PPP por tipo de PDV em moeda local da categoria"),
    ftr_preco_consumo_tipo_pdv_moeda_local_cat FLOAT64 OPTIONS(description="Fator consumo por tipo de PDV em moeda local da categoria"),
    ftr_preco_ppp_consumo_moeda_local_cat FLOAT64 OPTIONS(description="Fator PPP de consumo em moeda local da categoria"),
    ftr_consumo_semanal_moeda_local_categoria FLOAT64 OPTIONS(description="Fator consumo semanal em moeda local da categoria"),

    -- Fatores (USD)
    ftr_preco_lista_usd_categoria FLOAT64 OPTIONS(description="Fator preço de lista em USD da categoria"),
    ftr_preco_ppp_usd_categoria FLOAT64 OPTIONS(description="Fator PPP em USD da categoria"),
    ftr_consumo_usd_categoria FLOAT64 OPTIONS(description="Fator de consumo em USD da categoria"),
    ftr_preco_pmc_usd_categoria FLOAT64 OPTIONS(description="Fator preço PMC em USD da categoria"),
    ftr_preco_ppp_tipo_pdv_usd_categoria FLOAT64 OPTIONS(description="Fator PPP por tipo de PDV em USD da categoria"),
    ftr_preco_consumo_tipo_pdv_usd_categoria FLOAT64 OPTIONS(description="Fator consumo por tipo de PDV em USD da categoria"),
    ftr_preco_ppp_consumo_usd_categoria FLOAT64 OPTIONS(description="Fator PPP de consumo em USD da categoria"),
    ftr_preco_privado_usd_categoria FLOAT64 OPTIONS(description="Fator preço privado em USD da categoria"),
    ftr_preco_nao_varejo_usd_categoria FLOAT64 OPTIONS(description="Fator preço não varejo em USD da categoria"),
    ftr_consumo_semanal_usd_categoria FLOAT64 OPTIONS(description="Fator consumo semanal em USD da categoria"),

    -- Datas
    dt_hr_processamento TIMESTAMP OPTIONS(description="Data e hora de processamento do registro")
)

PARTITION BY DATE(dt_hr_processamento)
CLUSTER BY cod_periodo_grupo_fk, cod_mercado_fk, cod_pdv_negocio_fk, cod_grupo_produto_negocio_fk

OPTIONS(
    description="Tabela que centraliza as informações de categoria de mercado da Iqvia, utilizada para análises de vendas e performance de produtos no contexto Sellout",
    labels=[("projeto", "sensitive-trusted"), ("dataset", "sellout"), ("squad", "eng")]
)
;