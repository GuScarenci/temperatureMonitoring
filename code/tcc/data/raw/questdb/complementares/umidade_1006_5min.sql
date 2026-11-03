SELECT measured_in, sensor_id, avg(humidity) AS umidade_media,
 min(humidity) AS minimo, max(humidity) AS maximo,
 count(*) AS quantidade, count(humidity) AS quantidade_validos
 FROM sensor_humidity WHERE environment = '1006'
 AND measured_in >= '2026-06-10T00:00:00Z' AND measured_in < '2026-07-26T00:00:00Z'
 AND sensor_id IN ('1', '48', '887', '891', '86782', '86789', '86790', '86791', '86793') SAMPLE BY 5m ORDER BY measured_in, sensor_id