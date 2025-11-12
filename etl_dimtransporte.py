import pandas as pd

#Processo de ETL da Fato Transporte

# --- 1. EXTRAIR ---
filename = "dim_transporte.csv"

try:
    # Carrega o arquivo CSV original, usando ';' como delimitador
    df_largo = pd.read_csv(filename, delimiter=';')

    print("Arquivo 'dim_transporte.csv' carregado com sucesso.")

    # --- 2. TRANSFORMAR ---
    
    # Definindo colunas que são IDs (para manter)
    id_cols = ['ID', 'Ano', 'Mes']
    
    # Define quais colunas são as métricas (para derreter/unpivot)
    # Pegamos os nomes em português do seu arquivo
    value_cols = ['Pé', 'Bicicleta', 'Cavalo', 'Cadeira de rodas', 'Barco']

    df_longo = df_largo.melt(
        id_vars=id_cols,
        value_vars=value_cols,
        var_name="Modalidade_Texto",  # Nome da nova coluna com ("Pé", "Bicicleta", etc.)
        value_name="qtd_peregrinos"    # Nome da nova coluna com os números
    )

    print("Operação 'Unpivot' (melt) concluída.")

    # Mapeia os nomes em português para as SKs da sua Dim_Transporte
    # VERIFIQUE SE ESSES NÚMEROS BATEM COM SEU BANCO DE DADOS!
    sk_map = {
        'Pé': 1,               # Assumindo que 'A pé' é SK = 1
        'Bicicleta': 2,        # Assumindo que 'Bicicleta' é SK = 2
        'Cavalo': 3,           # Assumindo que 'A cavalo' é SK = 3
        'Cadeira de rodas': 4, # Assumindo que 'Cadeira de rodas' é SK = 4
        'Barco': 5             # Assumindo que 'Vela' ('Barco') é SK = 5
    }
    
    # Cria a nova coluna FK_Transporte usando o mapa
    df_longo['FK_Transporte'] = df_longo['Modalidade_Texto'].map(sk_map)

    # Renomeia a coluna 'ID' para 'FK_Tempo' para bater com o DW
    df_final = df_longo.rename(columns={'ID': 'FK_Tempo'})
    
    # Seleciona apenas as colunas que a Fato_... precisa
    df_pronto = df_final[['FK_Tempo', 'FK_Transporte', 'qtd_peregrinos']]

    # --- 3. CARREGAR (Salvar novo arquivo) ---
    output_filename = "fato_transporte_pronto.csv"
    
    # Salva o novo CSV limpo, também com ponto e vírgula
    df_pronto.to_csv(output_filename, index=False, sep=';')

    print(f"\nArquivo '{output_filename}' criado com sucesso!")
    print("Formato dos dados prontos para o DW:")
    print(df_pronto.head())

except Exception as e:
    print(f"Ocorreu um erro: {e}")
    print(f"Verifique se o nome do arquivo '{filename}' está correto.")