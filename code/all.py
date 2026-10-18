import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import griddata

# 1. Carregar a configuração espacial dos dispositivos (JSON)
devices_json = """[
  {"id": 24, "name": "1006-TEMPHUM-05", "location_x": 0, "location_y": 0, "location_confirmed": false},
  {"id": 48, "name": "1006-TEMPHUM-07", "location_x": 8, "location_y": 5, "location_confirmed": true},
  {"id": 887, "name": "1006-TEMPHUM-09", "location_x": 0, "location_y": 0, "location_confirmed": true},
  {"id": 891, "name": "1006-TEMPHUM-06", "location_x": 0, "location_y": 4, "location_confirmed": true},
  {"id": 86789, "name": "1006-TEMPHUM-01", "location_x": 0, "location_y": 0, "location_confirmed": false},
  {"id": 86790, "name": "1006-TEMPHUM-02", "location_x": 3, "location_y": 1, "location_confirmed": true},
  {"id": 86791, "name": "1006-TEMPHUM-03", "location_x": 5, "location_y": 1, "location_confirmed": true},
  {"id": 86793, "name": "1006-TEMPHUM-08", "location_x": 8, "location_y": 0, "location_confirmed": true}
]"""

df_devices = pd.DataFrame(json.loads(devices_json))

# 2. Carregar as leituras consolidadas do results.csv (ou mock de teste)
try:
    df_results = pd.read_csv("results.csv")
    # Filtra pelo timestamp mais recente
    ultimo_ts = df_results["measured_in"].max()
    df_current = df_results[df_results["measured_in"] == ultimo_ts].copy()
except Exception:
    # Dados de exemplo caso esteja a testar sem o ficheiro local
    df_current = pd.DataFrame(
        {
            "sensor_id": [48, 887, 891, 86790, 86791, 86793],
            "temperature": [23.5, 21.8, 25.1, 22.4, 23.0, 26.2],
            "humidity": [55.0, 62.0, 48.0, 52.0, 50.0, 70.0],
        }
    )

df_devices["id"] = df_devices["id"].astype(str)
df_current["sensor_id"] = df_current["sensor_id"].astype(str)

# 3. Unificar dados espaciais com leituras
df_plot = pd.merge(
    df_devices, df_current, left_on="id", right_on="sensor_id", how="inner"
)

# Considerar apenas posições confirmadas para evitar sobreposição em (0,0) não calibrado
df_plot = df_plot[df_plot["location_confirmed"] == True].copy()


# 4. Avaliação do Conforto Térmico (Base ASHRAE 55 / NR-17)
def avaliar_conforto(temp, hum):
    if 20.0 <= temp <= 26.0 and 30.0 <= hum <= 65.0:
        return "Confortável", "#2ecc71"  # Verde
    elif temp > 26.0:
        return "Quente", "#e74c3c"  # Vermelho
    elif temp < 20.0:
        return "Frio", "#3498db"  # Azul
    else:
        return "Desconfortável", "#e67e22"  # Laranja


df_plot[["comfort_status", "comfort_color"]] = df_plot.apply(
    lambda r: pd.Series(avaliar_conforto(r["temperature"], r["humidity"])),
    axis=1,
)

# 5. Interpolação Espacial da Temperatura na Grelha (x: 0 a 8, y: 0 a 5)
grid_x, grid_y = np.mgrid[0:8:200j, 0:5:200j]

pontos = df_plot[["location_x", "location_y"]].values
valores_temp = df_plot["temperature"].values

# Interpolação Linear com preenchimento Nearest para as bordas da sala
grid_temp = griddata(
    pontos, valores_temp, (grid_x, grid_y), method="linear"
)  # Região central
grid_temp_nearest = griddata(
    pontos, valores_temp, (grid_x, grid_y), method="nearest"
)  # Bordas
grid_temp[np.isnan(grid_temp)] = grid_temp_nearest[np.isnan(grid_temp)]

# 6. Renderização do Gráfico
fig, ax = plt.subplots(figsize=(11, 7))

# Mapa de Calor contínuo
cax = ax.imshow(
    grid_temp.T,
    extent=(0, 8, 0, 5),
    origin="lower",
    cmap="coolwarm",
    aspect="auto",
    alpha=0.85,
)
cbar = fig.colorbar(cax, ax=ax, pad=0.02)
cbar.set_label("Temperatura (°C)", fontsize=11, fontweight="bold")

# Marcação dos sensores físicos e caixas informativas
for _, row in df_plot.iterrows():
    x, y = row["location_x"], row["location_y"]

    # Ponto do sensor
    ax.scatter(
        x,
        y,
        color=row["comfort_color"],
        s=130,
        edgecolors="black",
        linewidths=1.5,
        zorder=5,
    )

    # Rótulo com as métricas detalhadas
    texto = (
        f"{row['name']}\n"
        f"T: {row['temperature']:.1f}°C | H: {row['humidity']:.0f}%\n"
        f"[{row['comfort_status']}]"
    )

    ax.annotate(
        texto,
        (x, y),
        textcoords="offset points",
        xytext=(0, 12),
        ha="center",
        fontsize=8.5,
        fontweight="semibold",
        color="black",
        bbox=dict(
            boxstyle="round,pad=0.3",
            facecolor="white",
            alpha=0.9,
            edgecolor=row["comfort_color"],
            linewidth=1.2,
        ),
        zorder=6,
    )

# Configurações do layout da grelha da sala
ax.set_xlim(-0.5, 8.5)
ax.set_ylim(-0.5, 5.5)
ax.set_xticks(range(0, 9))
ax.set_yticks(range(0, 6))
ax.set_xlabel("Dimensão X da Sala (metros ou grelha)", fontsize=11)
ax.set_ylabel("Dimensão Y da Sala (metros ou grelha)", fontsize=11)
ax.set_title(
    "Distribuição Térmica e Conforto nos Sensores - Sala 1006 (LASDPC)",
    fontsize=13,
    fontweight="bold",
    pad=15,
)
ax.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.5)

plt.tight_layout()
plt.savefig("mapa_calor_sala_1006.png", dpi=300)
plt.show()