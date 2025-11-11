UPDATE Dim_Transporte
SET Modalidade = 'Pé'
WHERE Modalidade = 'Pie';

UPDATE Dim_Transporte
SET Modalidade = 'Cavalo'
WHERE Modalidade = 'Caballo';

UPDATE Dim_Transporte
SET Modalidade = 'Cadeira de rodas'
WHERE Modalidade = 'Silla de ruedas';

UPDATE Dim_Transporte
SET Modalidade = 'Barco'
WHERE Modalidade = 'Vela';

SELECT * FROM dim_transporte;