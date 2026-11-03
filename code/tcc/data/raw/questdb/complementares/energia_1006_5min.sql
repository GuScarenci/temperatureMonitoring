SELECT measured_in, sensor_id, avg(energy) AS valor_medio,
 min(energy) AS minimo, max(energy) AS maximo, count(*) AS quantidade,
 count(energy) AS quantidade_validos FROM sensor_energy WHERE environment = '1006'
 AND measured_in >= '2026-06-10T00:00:00Z' AND measured_in < '2026-07-26T00:00:00Z'
 SAMPLE BY 5m ORDER BY measured_in, sensor_id