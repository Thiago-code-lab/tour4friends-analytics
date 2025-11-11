-- Active: 1756209144349@@127.0.0.1@5432@DW_projetointegrador
--Criando a Dimensão de Transporte
CREATE TABLE Dim_Transporte (
    SK_Transporte SERIAL NOT NULL,  -- Chave Surrogada (1, 2, 3...)
    Modalidade VARCHAR(100) NOT NULL, -- (Ex: 'Pie', 'Bicicleta')
    CONSTRAINT transporte_pk PRIMARY KEY (SK_Transporte)
);

--Criando a Dimensão de Tempo (Mensal)
CREATE TABLE Dim_Tempo (
    SK_Tempo INTEGER NOT NULL,  
    Ano INTEGER NOT NULL,
    Numero_Mes INTEGER NOT NULL,
    Mes_Nome VARCHAR(50) NOT NULL, 
    Trimestre CHAR(2) NOT NULL,  
    Estacao_Ano VARCHAR(50) NOT NULL, 
    CONSTRAINT tempo_pk PRIMARY KEY (SK_Tempo)
);

--Criando a Tabela Fato (Onde os números ficarão)
CREATE TABLE Fato_Peregrinos_Por_Transporte (
    FK_Tempo INTEGER NOT NULL,
    FK_Transporte INTEGER NOT NULL,
    qtd_peregrinos INTEGER NOT NULL,
        -- Definindo as ligações
    FOREIGN KEY (FK_Tempo) REFERENCES Dim_Tempo(SK_Tempo),
    FOREIGN KEY (FK_Transporte) REFERENCES Dim_Transporte(SK_Transporte)
);