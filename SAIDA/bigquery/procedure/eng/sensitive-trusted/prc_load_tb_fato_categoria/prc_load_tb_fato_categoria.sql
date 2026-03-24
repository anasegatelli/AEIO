-- ========================================================================
-- Objeto......: prc_load_tb_fato_categoria
-- Camada......: sensitive-trusted
-- Version.....: 0.0.1
-- Squad.......: eng
-- Data Criacao: 2026-03-22
-- Descricao...: Procedure de carga FULL para a tabela tb_fato_categoria, consolidando dados de categoria de vendas a partir da origem sensitive-raw.raw_iqvia.fact_category_ds_gc
-- ========================================================================

CREATE OR REPLACE PROCEDURE `sp.prc_load_tb_fato_categoria`(
    VAR_PRJ_RAW STRING,
    VAR_PRJ_RAW_CUSTOM STRING,
    VAR_PRJ_TRUSTED STRING,
    VAR_PRJ_REFINED STRING,
    VAR_PRJ_SENSITIVE_RAW STRING,
    VAR_PRJ_SENSITIVE_TRUSTED STRING,
    VAR_PRJ_SENSITIVE_REFINED STRING
)
BEGIN

    -- Parametros usados para tabela de controle e log
    DECLARE VAR_PROCEDURE  DEFAULT 'prc_load_tb_fato_categoria';
    DECLARE VAR_DELTA_INI  DATE;
    DECLARE VAR_DELTA_FIM  DATE;
    DECLARE VAR_TABELA     STRING;
    DECLARE VAR_DTH_INICIO TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

    -- Inicio do bloco de TRY/CATCH (tratamento de erros)
    BEGIN

        -- Recupera parametros da TB_AUX_CONFIG_CARGA_BUS
        CALL sp.prc_get_params(VAR_PROCEDURE, VAR_DELTA_INI, VAR_DELTA_FIM, VAR_TABELA);

        BEGIN TRANSACTION;

            -- Criação da tabela temporária com dados da RAW
            EXECUTE IMMEDIATE """
                CREATE TEMP TABLE temp_tb_fato_categoria AS
                SELECT
                    CAST(cod_periodo_grupo_fk AS STRING) AS cod_periodo_grupo_fk,
                    CAST(cod_mercado_fk AS STRING) AS cod_mercado_fk,
                    CAST(cod_pdv_negocio_fk AS STRING) AS cod_pdv_negocio_fk,
                    CAST(cod_grupo_produto_negocio_fk AS STRING) AS cod_grupo_produto_negocio_fk,
                    CAST(id_fcc_rds AS STRING) AS id_fcc_rds,
                    CAST(qt_unidade_categoria AS INT64) AS qt_unidade_categoria,
                    CAST(qt_unidade_designada_categoria AS INT64) AS qt_unidade_designada_categoria,
                    CAST(vlr_preco_lista_moeda_local_categoria AS NUMERIC) AS vlr_preco_lista_moeda_local_categoria,
                    CAST(vlr_ppp_moeda_local_categoria AS NUMERIC) AS vlr_ppp_moeda_local_categoria,
                    CAST(vlr_consumo_moeda_local_categoria AS NUMERIC) AS vlr_consumo_moeda_local_categoria,
                    CAST(vlr_preco_personalizado_moeda_local_cat AS NUMERIC) AS vlr_preco_personalizado_moeda_local_cat,
                    CAST(vlr_preco_privado_moeda_local_categoria AS NUMERIC) AS vlr_preco_privado_moeda_local_categoria,
                    CAST(vlr_preco_nao_varejo_moeda_local_cat AS NUMERIC) AS vlr_preco_nao_varejo_moeda_local_cat,
                    CAST(vlr_preco_pmc_moeda_local_categoria AS NUMERIC) AS vlr_preco_pmc_moeda_local_categoria,
                    CAST(vlr_preco_ppp_tipo_pdv_moeda_local_cat AS NUMERIC) AS vlr_preco_ppp_tipo_pdv_moeda_local_cat,
                    CAST(vlr_preco_consumo_tipo_pdv_moeda_local_cat AS NUMERIC) AS vlr_preco_consumo_tipo_pdv_moeda_local_cat,
                    CAST(vlr_preco_ppp_consumo_moeda_local_cat AS NUMERIC) AS vlr_preco_ppp_consumo_moeda_local_cat,
                    CAST(vlr_preco_lista_usd_categoria AS NUMERIC) AS vlr_preco_lista_usd_categoria,
                    CAST(vlr_ppp_usd_categoria AS NUMERIC) AS vlr_ppp_usd_categoria,
                    CAST(vlr_consumo_usd_categoria AS NUMERIC) AS vlr_consumo_usd_categoria,
                    CAST(vlr_preco_personalizado_usd_categoria AS NUMERIC) AS vlr_preco_personalizado_usd_categoria,
                    CAST(vlr_preco_privado_usd_categoria AS NUMERIC) AS vlr_preco_privado_usd_categoria,
                    CAST(vlr_preco_nao_varejo_usd_categoria AS NUMERIC) AS vlr_preco_nao_varejo_usd_categoria,
                    CAST(vlr_preco_pmc_usd_categoria AS NUMERIC) AS vlr_preco_pmc_usd_categoria,
                    CAST(vlr_preco_ppp_tipo_pdv_usd_categoria AS NUMERIC) AS vlr_preco_ppp_tipo_pdv_usd_categoria,
                    CAST(vlr_preco_consumo_tipo_pdv_usd_categoria AS NUMERIC) AS vlr_preco_consumo_tipo_pdv_usd_categoria,
                    CAST(vlr_preco_ppp_consumo_usd_categoria AS NUMERIC) AS vlr_preco_ppp_consumo_usd_categoria,
                    CAST(ftr_unidade_categoria AS FLOAT64) AS ftr_unidade_categoria,
                    CAST(ftr_unidade_alternativa_categoria AS FLOAT64) AS ftr_unidade_alternativa_categoria,
                    CAST(ftr_unidade_designada_categoria AS FLOAT64) AS ftr_unidade_designada_categoria,
                    CAST(ftr_preco_lista_moeda_local_categoria AS FLOAT64) AS ftr_preco_lista_moeda_local_categoria,
                    CAST(ftr_preco_ppp_moeda_local_categoria AS FLOAT64) AS ftr_preco_ppp_moeda_local_categoria,
                    CAST(ftr_consumo_moeda_local_categoria AS FLOAT64) AS ftr_consumo_moeda_local_categoria,
                    CAST(ftr_preco_privado_moeda_local_categoria AS FLOAT64) AS ftr_preco_privado_moeda_local_categoria,
                    CAST(ftr_preco_nao_varejo_moeda_local_cat AS FLOAT64) AS ftr_preco_nao_varejo_moeda_local_cat,
                    CAST(ftr_preco_pmc_moeda_local_categoria AS FLOAT64) AS ftr_preco_pmc_moeda_local_categoria,
                    CAST(ftr_preco_ppp_tipo_pdv_moeda_local_cat AS FLOAT64) AS ftr_preco_ppp_tipo_pdv_moeda_local_cat,
                    CAST(ftr_preco_consumo_tipo_pdv_moeda_local_cat AS FLOAT64) AS ftr_preco_consumo_tipo_pdv_moeda_local_cat,
                    CAST(ftr_preco_ppp_consumo_moeda_local_cat AS FLOAT64) AS ftr_preco_ppp_consumo_moeda_local_cat,
                    CAST(ftr_consumo_semanal_moeda_local_categoria AS FLOAT64) AS ftr_consumo_semanal_moeda_local_categoria,
                    CAST(ftr_preco_lista_usd_categoria AS FLOAT64) AS ftr_preco_lista_usd_categoria,
                    CAST(ftr_preco_ppp_usd_categoria AS FLOAT64) AS ftr_preco_ppp_usd_categoria,
                    CAST(ftr_consumo_usd_categoria AS FLOAT64) AS ftr_consumo_usd_categoria,
                    CAST(ftr_preco_pmc_usd_categoria AS FLOAT64) AS ftr_preco_pmc_usd_categoria,
                    CAST(ftr_preco_ppp_tipo_pdv_usd_categoria AS FLOAT64) AS ftr_preco_ppp_tipo_pdv_usd_categoria,
                    CAST(ftr_preco_consumo_tipo_pdv_usd_categoria AS FLOAT64) AS ftr_preco_consumo_tipo_pdv_usd_categoria,
                    CAST(ftr_preco_ppp_consumo_usd_categoria AS FLOAT64) AS ftr_preco_ppp_consumo_usd_categoria,
                    CAST(ftr_preco_privado_usd_categoria AS FLOAT64) AS ftr_preco_privado_usd_categoria,
                    CAST(ftr_preco_nao_varejo_usd_categoria AS FLOAT64) AS ftr_preco_nao_varejo_usd_categoria,
                    CAST(ftr_consumo_semanal_usd_categoria AS FLOAT64) AS ftr_consumo_semanal_usd_categoria,
                    CAST(dt_hr_processamento AS TIMESTAMP) AS dt_hr_processamento,
                    CURRENT_TIMESTAMP AS dt_carga
                FROM `""" || VAR_PRJ_SENSITIVE_RAW || """.raw_iqvia.fact_category_ds_gc`
            """;

            -- TRUNCATE na tabela final (FULL LOAD)
            EXECUTE IMMEDIATE """
                TRUNCATE TABLE `""" || VAR_PRJ_SENSITIVE_TRUSTED || """.sellout.tb_fato_categoria`
            """;

            -- INSERT dos dados da temp para tabela final
            EXECUTE IMMEDIATE """
                INSERT INTO `""" || VAR_PRJ_SENSITIVE_TRUSTED || """.sellout.tb_fato_categoria` (
                    cod_periodo_grupo_fk,
                    cod_mercado_fk,
                    cod_pdv_negocio_fk,
                    cod_grupo_produto_negocio_fk,
                    id_fcc_rds,
                    qt_unidade_categoria,
                    qt_unidade_designada_categoria,
                    vlr_preco_lista_moeda_local_categoria,
                    vlr_ppp_moeda_local_categoria,
                    vlr_consumo_moeda_local_categoria,
                    vlr_preco_personalizado_moeda_local_cat,
                    vlr_preco_privado_moeda_local_categoria,
                    vlr_preco_nao_varejo_moeda_local_cat,
                    vlr_preco_pmc_moeda_local_categoria,
                    vlr_preco_ppp_tipo_pdv_moeda_local_cat,
                    vlr_preco_consumo_tipo_pdv_moeda_local_cat,
                    vlr_preco_ppp_consumo_moeda_local_cat,
                    vlr_preco_lista_usd_categoria,
                    vlr_ppp_usd_categoria,
                    vlr_consumo_usd_categoria,
                    vlr_preco_personalizado_usd_categoria,
                    vlr_preco_privado_usd_categoria,
                    vlr_preco_nao_varejo_usd_categoria,
                    vlr_preco_pmc_usd_categoria,
                    vlr_preco_ppp_tipo_pdv_usd_categoria,
                    vlr_preco_consumo_tipo_pdv_usd_categoria,
                    vlr_preco_ppp_consumo_usd_categoria,
                    ftr_unidade_categoria,
                    ftr_unidade_alternativa_categoria,
                    ftr_unidade_designada_categoria,
                    ftr_preco_lista_moeda_local_categoria,
                    ftr_preco_ppp_moeda_local_categoria,
                    ftr_consumo_moeda_local_categoria,
                    ftr_preco_privado_moeda_local_categoria,
                    ftr_preco_nao_varejo_moeda_local_cat,
                    ftr_preco_pmc_moeda_local_categoria,
                    ftr_preco_ppp_tipo_pdv_moeda_local_cat,
                    ftr_preco_consumo_tipo_pdv_moeda_local_cat,
                    ftr_preco_ppp_consumo_moeda_local_cat,
                    ftr_consumo_semanal_moeda_local_categoria,
                    ftr_preco_lista_usd_categoria,
                    ftr_preco_ppp_usd_categoria,
                    ftr_consumo_usd_categoria,
                    ftr_preco_pmc_usd_categoria,
                    ftr_preco_ppp_tipo_pdv_usd_categoria,
                    ftr_preco_consumo_tipo_pdv_usd_categoria,
                    ftr_preco_ppp_consumo_usd_categoria,
                    ftr_preco_privado_usd_categoria,
                    ftr_preco_nao_varejo_usd_categoria,
                    ftr_consumo_semanal_usd_categoria,
                    dt_hr_processamento,
                    dt_carga
                )
                SELECT
                    cod_periodo_grupo_fk,
                    cod_mercado_fk,
                    cod_pdv_negocio_fk,
                    cod_grupo_produto_negocio_fk,
                    id_fcc_rds,
                    qt_unidade_categoria,
                    qt_unidade_designada_categoria,
                    vlr_preco_lista_moeda_local_categoria,
                    vlr_ppp_moeda_local_categoria,
                    vlr_consumo_moeda_local_categoria,
                    vlr_preco_personalizado_moeda_local_cat,
                    vlr_preco_privado_moeda_local_categoria,
                    vlr_preco_nao_varejo_moeda_local_cat,
                    vlr_preco_pmc_moeda_local_categoria,
                    vlr_preco_ppp_tipo_pdv_moeda_local_cat,
                    vlr_preco_consumo_tipo_pdv_moeda_local_cat,
                    vlr_preco_ppp_consumo_moeda_local_cat,
                    vlr_preco_lista_usd_categoria,
                    vlr_ppp_usd_categoria,
                    vlr_consumo_usd_categoria,
                    vlr_preco_personalizado_usd_categoria,
                    vlr_preco_privado_usd_categoria,
                    vlr_preco_nao_varejo_usd_categoria,
                    vlr_preco_pmc_usd_categoria,
                    vlr_preco_ppp_tipo_pdv_usd_categoria,
                    vlr_preco_consumo_tipo_pdv_usd_categoria,
                    vlr_preco_ppp_consumo_usd_categoria,
                    ftr_unidade_categoria,
                    ftr_unidade_alternativa_categoria,
                    ftr_unidade_designada_categoria,
                    ftr_preco_lista_moeda_local_categoria,
                    ftr_preco_ppp_moeda_local_categoria,
                    ftr_consumo_moeda_local_categoria,
                    ftr_preco_privado_moeda_local_categoria,
                    ftr_preco_nao_varejo_moeda_local_cat,
                    ftr_preco_pmc_moeda_local_categoria,
                    ftr_preco_ppp_tipo_pdv_moeda_local_cat,
                    ftr_preco_consumo_tipo_pdv_moeda_local_cat,
                    ftr_preco_ppp_consumo_moeda_local_cat,
                    ftr_consumo_semanal_moeda_local_categoria,
                    ftr_preco_lista_usd_categoria,
                    ftr_preco_ppp_usd_categoria,
                    ftr_consumo_usd_categoria,
                    ftr_preco_pmc_usd_categoria,
                    ftr_preco_ppp_tipo_pdv_usd_categoria,
                    ftr_preco_consumo_tipo_pdv_usd_categoria,
                    ftr_preco_ppp_consumo_usd_categoria,
                    ftr_preco_privado_usd_categoria,
                    ftr_preco_nao_varejo_usd_categoria,
                    ftr_consumo_semanal_usd_categoria,
                    dt_hr_processamento,
                    dt_carga
                FROM temp_tb_fato_categoria
            """;

            -- Log de sucesso
            CALL sp.prc_log_exec_transaction(VAR_TABELA, VAR_DTH_INICIO, @@row_count, VAR_PROCEDURE, @@error.message, VAR_PRJ_SENSITIVE_TRUSTED);
            COMMIT TRANSACTION;

    EXCEPTION WHEN ERROR THEN
        ROLLBACK TRANSACTION;
        CALL sp.prc_log_exec_transaction(VAR_TABELA, VAR_DTH_INICIO, @@row_count, VAR_PROCEDURE, @@error.message, VAR_PRJ_SENSITIVE_TRUSTED);
        RAISE USING MESSAGE = @@error.message;

    END;

END;