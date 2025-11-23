-- 1. PRIMEIRO: Garantimos que a procedure existe (Recriamos ela do zero)
CREATE OR REPLACE PROCEDURE calcular_total_peregrinos_dinamico(
    nome_tabela TEXT,       
    coluna_agrupadora TEXT, 
    coluna_valor TEXT       
)
LANGUAGE plpgsql
AS $$
DECLARE
    cursor_dados REFCURSOR; 
    registro RECORD;        
    comando_sql TEXT;       
BEGIN
    RAISE NOTICE '--- Iniciando cálculo na tabela % ---', nome_tabela;

    -- Monta a query (Note que uso %s para não ter problema com aspas)
    comando_sql := format(
        'SELECT %I AS grupo, SUM(%I) AS total_calculado FROM %I GROUP BY %I ORDER BY total_calculado DESC', 
        coluna_agrupadora, coluna_valor, nome_tabela, coluna_agrupadora
    );

    OPEN cursor_dados FOR EXECUTE comando_sql;

    LOOP
        FETCH cursor_dados INTO registro;
        EXIT WHEN NOT FOUND; 
        RAISE NOTICE 'Grupo ID: %, Total: %', registro.grupo, registro.total_calculado;
    END LOOP;

    CLOSE cursor_dados;
END;
$$;

-- 2. SEGUNDO: Inserimos dados de teste (caso esteja vazio)
INSERT INTO Dim_Transporte (SK_Transporte, Modalidade) 
VALUES (999, 'Teste Final') ON CONFLICT DO NOTHING;

INSERT INTO Dim_Tempo (SK_Tempo, Ano, Numero_Mes, Mes_Nome, Trimestre, Estacao_Ano) 
VALUES (999, 2024, 12, 'Dezembro', '4T', 'Verao') ON CONFLICT DO NOTHING;

INSERT INTO Fato_Peregrinos_Por_Transporte (FK_Tempo, FK_Transporte, qtd_peregrinos) 
VALUES (999, 999, 1000) ON CONFLICT DO NOTHING;

-- 3. TERCEIRO: Chamamos a procedure (Com os nomes em minúsculo)
CALL calcular_total_peregrinos_dinamico('fato_peregrinos_por_transporte', 'fk_transporte', 'qtd_peregrinos');