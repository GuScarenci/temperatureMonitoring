import json
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import griddata

# 1. Lista dos 8 sensores definidos
raw_sensors = [
    {
        "id": "887",
        "name": "1006-TEMPHUM-09",
        "location_x": 0.0,
        "location_y": 0.0,
    },
    {
        "id": "86808",
        "name": "1008-TEMPHUM-08",
        "location_x": 0.0,
        "location_y": 5.0,
    },  # Ancorado em y=5 (limite superior da sala)
    {
        "id": "86790",
        "name": "1006-TEMPHUM-02",
        "location_x": 3.0,
        "location_y": 1.0,
    },
    {
        "id": "86791",
        "name": "1006-TEMPHUM-03",
        "location_x": 5.0,
        "location_y": 1.0,
    },
    {
        "id": "1025",
        "name": "1008REUNIAO-TEMPHUM-03",
        "location_x": 3.0,
        "location_y": 3.0,
    },
    {
        "id": "86801",
        "name": "1008REUNIAO-TEMPHUM-04",
        "location_x": 5.0,
        "location_y": 3.0,
    },
    {
        "id": "891",
        "name": "1006-TEMPHUM-06",
        "location_x": 0.0,
        "location_y": 3.5,
    },
    {"id": "48", "name": "1006-TEMPHUM-07", "location_x": 8.0, "location_y": 5.0},
]

df_sensors = pd.DataFrame(raw_sensors)

# 2. Carregar dados consolidados de results.csv
df_results = pd.read_csv("results.csv")
df_results["sensor_id"] = df_results["sensor_id"].astype(str)
df_results["measured_in"] = pd.to_datetime(df_results["measured_in"])

# Filtro de sanidade física para DHT22
df_results = df_results[
    (df_results["temperature"] >= 12.0)
    & (df_results["temperature"] <= 38.0)
    & (df_results["humidity"] >= 20.0)
    & (df_results["humidity"] <= 95.0)
].copy()

# Filtrar apenas os 8 sensores de interesse
df_results = df_results[df_results["sensor_id"].isin(df_sensors["id"])].copy()

# 3. Discretizar o tempo em janelas regulares (10 minutos)
df_results["time_window"] = df_results["measured_in"].dt.floor("10min")

pivot_temp = df_results.pivot_table(
    index="time_window",
    columns="sensor_id",
    values="temperature",
    aggfunc="mean",
)
pivot_hum = df_results.pivot_table(
    index="time_window", columns="sensor_id", values="humidity", aggfunc="mean"
)

# Garantir que todos os 8 IDs existam nas colunas da tabela dinâmica
for sid in df_sensors["id"]:
    if sid not in pivot_temp.columns:
        pivot_temp[sid] = np.nan
    if sid not in pivot_hum.columns:
        pivot_hum[sid] = np.nan

# Interpolação/preenchimento para que nenhum sensor fique ausente em nenhum quadro
pivot_temp = pivot_temp.rolling(window=3, min_periods=1).mean().ffill().bfill()
pivot_hum = pivot_hum.rolling(window=3, min_periods=1).mean().ffill().bfill()

timestamps = pivot_temp.index
print(f"Total de quadros no tempo: {len(timestamps)}")
print(f"Sensores garantidos: {len(df_sensors)} de 8")

# 4. Grelha contínua da sala (X: 0 a 8, Y: 0 a 5)
grid_x, grid_y = np.mgrid[0:8:200j, 0:5:200j]

# Malha auxiliar para a Zona Fria Fixa (x in [0, 6], y in [4, 5] a 16°C)
fixed_coords = []
fixed_temps = []
fixed_hums = []
for fx in np.linspace(0, 6, 7):
    for fy in np.linspace(4, 5, 3):
        fixed_coords.append([fx, fy])
        fixed_temps.append(16.0)
        fixed_hums.append(45.0)

fixed_coords = np.array(fixed_coords)
fixed_temps = np.array(fixed_temps)


# 5. Avaliação do Conforto Térmico (ASHRAE 55)
def avaliar_conforto(t, h):
    if pd.isna(t) or pd.isna(h):
        return "Sem Dados", "#7f8c8d"
    if 20.0 <= t <= 26.0 and 30.0 <= h <= 65.0:
        return "Confortável", "#2ecc71"
    elif t > 26.0:
        return "Quente", "#e74c3c"
    elif t < 20.0:
        return "Frio", "#3498db"
    return "Desconfortável", "#e67e22"


VMIN, VMAX = 15.0, 30.0
fig, ax = plt.subplots(figsize=(11, 7))


def update(frame_idx):
    ax.clear()
    ts = timestamps[frame_idx]

    current_t = pivot_temp.loc[ts]
    current_h = pivot_hum.loc[ts]

    sensor_coords = []
    sensor_t = []
    sensor_h = []
    sensor_names = []

    # Extrai dados de TODOS os 8 sensores
    for _, sensor in df_sensors.iterrows():
        sid = sensor["id"]
        sensor_coords.append([sensor["location_x"], sensor["location_y"]])
        sensor_t.append(current_t.get(sid, 23.0))  # fallback de segurança
        sensor_h.append(current_h.get(sid, 50.0))
        sensor_names.append(sensor["name"])

    # Combina leituras com a zona de insuflamento
    all_points = np.vstack([np.array(sensor_coords), fixed_coords])
    all_temps = np.concatenate([np.array(sensor_t), fixed_temps])

    # Interpolação espacial
    grid_temp = griddata(all_points, all_temps, (grid_x, grid_y), method="linear")
    grid_near = griddata(
        all_points, all_temps, (grid_x, grid_y), method="nearest"
    )
    grid_temp[np.isnan(grid_temp)] = grid_near[np.isnan(grid_temp)]

    # Heatmap de fundo
    im = ax.imshow(
        grid_temp.T,
        extent=(0, 8, 0, 5),
        origin="lower",
        cmap="coolwarm",
        aspect="auto",
        alpha=0.85,
        vmin=VMIN,
        vmax=VMAX,
    )

    # Destaque da zona fixa de ar frio
    ax.fill_between(
        [0, 6],
        4,
        5,
        color="cyan",
        alpha=0.2,
        hatch="//",
        label="Zona AC (16°C fixo)",
    )

    # Plotar TODOS os 8 sensores com as caixas de informação
    for i in range(len(sensor_coords)):
        x, y = sensor_coords[i]
        t = sensor_t[i]
        h = sensor_h[i]
        status, cor = avaliar_conforto(t, h)

        # Marcador pontual do sensor
        ax.scatter(
            x,
            y,
            color=cor,
            s=130,
            edgecolors="black",
            linewidths=1.5,
            zorder=6,
        )

        # Deslocamento vertical do rótulo para não cobrir a borda superior
        y_offset = -22 if y >= 4.5 else 12

        ax.annotate(
            f"{sensor_names[i]}\n{t:.1f}°C | {h:.0f}%\n[{status}]",
            (x, y),
            textcoords="offset points",
            xytext=(0, y_offset),
            ha="center",
            fontsize=7.5,
            fontweight="bold",
            bbox=dict(
                boxstyle="round,pad=0.2",
                facecolor="white",
                alpha=0.92,
                edgecolor=cor,
                linewidth=1.2,
            ),
            zorder=7,
        )

    # Configuração dos eixos da sala
    ax.set_xlim(-0.6, 8.6)
    ax.set_ylim(-0.6, 5.6)
    ax.set_xticks(range(0, 9))
    ax.set_yticks(range(0, 6))
    ax.set_xlabel("Eixo X da Sala (metros)", fontsize=10, fontweight="bold")
    ax.set_ylabel("Eixo Y da Sala (metros)", fontsize=10, fontweight="bold")
    ax.set_title(
        f"Distribuição Térmica e Conforto no Tempo - Sala 1006\nHorário: {ts.strftime('%Y-%m-%d %H:%M')}",
        fontsize=12,
        fontweight="bold",
        pad=10,
    )
    ax.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.35)
    ax.legend(loc="lower right", fontsize=8)

    return (im,)


# Barra de escala de temperatura fixa
cax_init = ax.imshow(
    np.zeros((200, 200)), cmap="coolwarm", vmin=VMIN, vmax=VMAX
)
cbar = fig.colorbar(cax_init, ax=ax, pad=0.02)
cbar.set_label("Temperatura (°C)", fontsize=11, fontweight="bold")

print("A compilar 'mapa_completo_8_sensores.gif'...")
ani = animation.FuncAnimation(
    fig, update, frames=len(timestamps), interval=400, blit=False
)
ani.save("mapa_completo_8_sensores.gif", writer="pillow", fps=3)
print(
    "Sucesso! O ficheiro 'mapa_completo_8_sensores.gif' foi gerado com os 8 sensores."
)