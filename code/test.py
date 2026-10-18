import json
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import griddata

# 1. Sensores com posições corrigidas para o grid (0 a 8 em X, 0 a 5 em Y)
raw_sensors = [
    {
        "id": 887,
        "name": "1006-TEMPHUM-09",
        "location_x": 0.0,
        "location_y": 0.0,
    },
    {
        "id": 86808,
        "name": "1008-TEMPHUM-08",
        "location_x": 0.0,
        "location_y": 5.0,
    },  # Corrigido para a parede superior (y=5)
    {
        "id": 86790,
        "name": "1006-TEMPHUM-02",
        "location_x": 3.0,
        "location_y": 1.0,
    },
    {
        "id": 86791,
        "name": "1006-TEMPHUM-03",
        "location_x": 5.0,
        "location_y": 1.0,
    },
    {
        "id": 1025,
        "name": "1008REUNIAO-TEMPHUM-03",
        "location_x": 3.0,
        "location_y": 3.0,
    },
    {
        "id": 86801,
        "name": "1008REUNIAO-TEMPHUM-04",
        "location_x": 5.0,
        "location_y": 3.0,
    },
    {
        "id": 891,
        "name": "1006-TEMPHUM-06",
        "location_x": 0.0,
        "location_y": 3.5,
    },
    {
        "id": 48,
        "name": "1006-TEMPHUM-07",
        "location_x": 8.0,
        "location_y": 5.0,
    },
]

df_sensors = pd.DataFrame(raw_sensors)
df_sensors["id"] = df_sensors["id"].astype(str)

# 2. Carregar e Limpar Dados
df_results = pd.read_csv("results.csv")
df_results["sensor_id"] = df_results["sensor_id"].astype(str)
df_results["measured_in"] = pd.to_datetime(df_results["measured_in"])

# Filtro de sanidade física (leituras válidas de DHT22 em sala)
df_results = df_results[
    (df_results["temperature"] >= 12.0)
    & (df_results["temperature"] <= 38.0)
    & (df_results["humidity"] >= 20.0)
    & (df_results["humidity"] <= 90.0)
].copy()

# Manter apenas os sensores mapeados
df_results = df_results[df_results["sensor_id"].isin(df_sensors["id"])].copy()

# 3. Amostragem em janelas de 10 min + Suavização
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

# Média móvel para mitigar o jitter de leitura do sensor
pivot_temp = pivot_temp.rolling(window=3, min_periods=1).mean().ffill().bfill()
pivot_hum = pivot_hum.rolling(window=3, min_periods=1).mean().ffill().bfill()

timestamps = pivot_temp.index
print(f"Total de janelas de tempo a renderizar: {len(timestamps)}")

# 4. Grelha de Interpolação Exata: X=[0, 8] e Y=[0, 5]
grid_x, grid_y = np.mgrid[0:8:200j, 0:5:200j]

# Malha de pontos fixos para a zona fria (AC/Cluster) em x in [0, 6] e y in [4, 5]
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
fixed_hums = np.array(fixed_hums)


def classificar_conforto(t, h):
    if 20.0 <= t <= 26.0 and 30.0 <= h <= 65.0:
        return "Confortável", "#2ecc71"
    elif t > 26.0:
        return "Quente", "#e74c3c"
    elif t < 20.0:
        return "Frio", "#3498db"
    return "Desconfortável", "#e67e22"


VMIN, VMAX = 15.0, 30.0
fig, ax = plt.subplots(figsize=(10, 6.5))


def update(frame_idx):
    ax.clear()
    ts = timestamps[frame_idx]

    current_t = pivot_temp.loc[ts]
    current_h = pivot_hum.loc[ts]

    sensor_coords = []
    sensor_t = []
    sensor_h = []
    sensor_names = []

    for _, sensor in df_sensors.iterrows():
        sid = sensor["id"]
        if sid in current_t and not pd.isna(current_t[sid]):
            sensor_coords.append([sensor["location_x"], sensor["location_y"]])
            sensor_t.append(current_t[sid])
            sensor_h.append(current_h[sid])
            sensor_names.append(sensor["name"])

    # Unir dados reais e âncoras da zona de 16°C
    all_points = np.vstack([np.array(sensor_coords), fixed_coords])
    all_temps = np.concatenate([np.array(sensor_t), fixed_temps])

    # Interpolação espacial suave
    grid_temp = griddata(all_points, all_temps, (grid_x, grid_y), method="linear")
    grid_near = griddata(
        all_points, all_temps, (grid_x, grid_y), method="nearest"
    )
    grid_temp[np.isnan(grid_temp)] = grid_near[np.isnan(grid_temp)]

    # Heatmap dentro do limite da sala (0 a 8 em X, 0 a 5 em Y)
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

    # Retângulo indicativo da zona fixa
    ax.fill_between(
        [0, 6],
        4,
        5,
        color="cyan",
        alpha=0.2,
        hatch="//",
        label="Zona AC (16°C fixo)",
    )

    # Plotar cada sensor físico
    for i in range(len(sensor_coords)):
        x, y = sensor_coords[i]
        t = sensor_t[i]
        h = sensor_h[i]
        status, cor = classificar_conforto(t, h)

        ax.scatter(
            x,
            y,
            color=cor,
            s=120,
            edgecolors="black",
            linewidths=1.2,
            zorder=5,
        )
        ax.annotate(
            f"{sensor_names[i]}\n{t:.1f}°C | {h:.0f}%\n[{status}]",
            (x, y),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontsize=7.5,
            fontweight="semibold",
            bbox=dict(
                boxstyle="round,pad=0.2",
                facecolor="white",
                alpha=0.9,
                edgecolor=cor,
            ),
            zorder=6,
        )

    ax.set_xlim(-0.5, 8.5)
    ax.set_ylim(-0.5, 5.5)
    ax.set_xticks(range(0, 9))
    ax.set_yticks(range(0, 6))
    ax.set_xlabel("X da sala (m)")
    ax.set_ylabel("Y da sala (m)")
    ax.set_title(
        f"Distribuição Térmica Sala 1006\n{ts.strftime('%Y-%m-%d %H:%M')}",
        fontsize=12,
        fontweight="bold",
    )
    ax.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.3)
    ax.legend(loc="lower right", fontsize=8)

    return (im,)


# Barra de cores lateral
cax_init = ax.imshow(
    np.zeros((200, 200)), cmap="coolwarm", vmin=VMIN, vmax=VMAX
)
cbar = fig.colorbar(cax_init, ax=ax, pad=0.02)
cbar.set_label("Temperatura (°C)", fontsize=11, fontweight="bold")

print("Gerando 'mapa_sala_1006.gif'...")
ani = animation.FuncAnimation(
    fig, update, frames=len(timestamps), interval=400, blit=False
)
ani.save("mapa_sala_1006.gif", writer="pillow", fps=3)
print("GIF gerado com sucesso!")