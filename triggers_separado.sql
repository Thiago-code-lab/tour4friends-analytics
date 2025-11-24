-- Active: 1763915470422@@127.0.0.1@5432@postgres
-- ==============================================================================
-- 1. Criação da Tabela de Logs (Onde as mudanças ficam salvas)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS Log_Auditoria_Peregrinos (
    ID_Log SERIAL PRIMARY KEY,
    Tabela_Afetada VARCHAR(100),
    Operacao VARCHAR(10),        -- INSERT, UPDATE, DELETE
    Usuario_Banco VARCHAR(100),  -- Quem fez a alteração
    Data_Evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Dados_Anteriores JSONB,      -- Como era antes (Backup)
    Dados_Novos JSONB            -- Como ficou depois
);

-- ==============================================================================
-- 2. Criação da Função do Trigger (A lógica que roda quando algo acontece)
-- ==============================================================================
CREATE OR REPLACE FUNCTION registrar_log_fato()
RETURNS TRIGGER AS $$
BEGIN
    -- Caso 1: Estão tentando APAGAR dados (DELETE)
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO Log_Auditoria_Peregrinos (Tabela_Afetada, Operacao, Usuario_Banco, Dados_Anteriores, Dados_Novos)
        VALUES (TG_TABLE_NAME, 'DELETE', CURRENT_USER, row_to_json(OLD), NULL);
        RETURN OLD;
    
    -- Caso 2: Estão tentando ATUALIZAR dados (UPDATE)
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO Log_Auditoria_Peregrinos (Tabela_Afetada, Operacao, Usuario_Banco, Dados_Anteriores, Dados_Novos)
        VALUES (TG_TABLE_NAME, 'UPDATE', CURRENT_USER, row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;

    -- Caso 3: Inserção de novos dados (INSERT)
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO Log_Auditoria_Peregrinos (Tabela_Afetada, Operacao, Usuario_Banco, Dados_Anteriores, Dados_Novos)
        VALUES (TG_TABLE_NAME, 'INSERT', CURRENT_USER, NULL, row_to_json(NEW));
        RETURN NEW;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- ==============================================================================
-- 3. Criação do Trigger (O "Vigia" que fica na tabela Fato)
-- ==============================================================================
DROP TRIGGER IF EXISTS trg_vigia_peregrinos ON Fato_Peregrinos_Por_Transporte;

CREATE TRIGGER trg_vigia_peregrinos
AFTER INSERT OR UPDATE OR DELETE ON Fato_Peregrinos_Por_Transporte
FOR EACH ROW
EXECUTE FUNCTION registrar_log_fato();