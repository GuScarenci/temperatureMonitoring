import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
from scipy.spatial.distance import cdist

# ==========================================
# 1. ARQUIVOS E DIMENSÕES DA SALA
# ==========================================
TEMP_CSV = "sensor_temperature_24_09_2026.csv"
HUM_CSV = "sensor_humidity_24_09_2026.csv"
JSON_FILE = "sensores_meus.json"

X_MIN, X_MAX = 0.0, 8.0
Y_MIN, Y_MAX = 0.0, 5.0
TIME_STEP = "1h"

# ==========================================
# 2. CARREGAR COORDENADAS DOS SENSORES
# ==========================================
with open(JSON_FILE, "r", encoding="utf-8") as f:
    sensors_list = json.load(f)

sensor_coords = {}
for s in sensors_list:
    s_id = str(s["id"])
    x = float(s["location_x"])
    y = float(s["location_y"])
    if X_MIN <= x <= X_MAX and Y_MIN <= y <= Y_MAX:
        sensor_coords[s_id] = (x, y)

# ==========================================
# 3. CARREGAR, SINCRONIZAR E ALINHAR DADOS
# ==========================================
# Temperatura
df_temp = pd.read_csv(TEMP_CSV)
df_temp["measured_in"] = pd.to_datetime(df_temp["measured_in"])
df_temp["sensor_id"] = df_temp["sensor_id"].astype(str)
pivot_temp = df_temp.pivot_table(
    index="measured_in", columns="sensor_id", values="temperature", aggfunc="mean"
)

# Umidade
df_hum = pd.read_csv(HUM_CSV)
df_hum["measured_in"] = pd.to_datetime(df_hum["measured_in"])
df_hum["sensor_id"] = df_hum["sensor_id"].astype(str)
pivot_hum = df_hum.pivot_table(
    index="measured_in", columns="sensor_id", values="humidity", aggfunc="mean"
)

# Interseção de sensores ativos válidos
active_sensors = [
    s for s in sensor_coords if s in pivot_temp.columns and s in pivot_hum.columns
]

if len(active_sensors) < 3:
    raise ValueError(
        f"Poucos sensores coincidentes mapeados ({len(active_sensors)}). Mínimo de 3 necessário."
    )

# Reamostragem e alinhamento temporal comum
resampled_temp = (
    pivot_temp[active_sensors].resample(TIME_STEP).mean().ffill().bfill()
)
resampled_hum = (
    pivot_hum[active_sensors].resample(TIME_STEP).mean().ffill().bfill()
)

# Garante o mesmo índice temporal para ambos
common_timeline = resampled_temp.index.intersection(resampled_hum.index)
resampled_temp = resampled_temp.loc[common_timeline]
resampled_hum = resampled_hum.loc[common_timeline]

sensor_pts = np.array([sensor_coords[s] for s in active_sensors])

# ==========================================
# 4. INTERPOLAÇÃO ESPACIAL BIDIMENSIONAL
# ==========================================
grid_x, grid_y = np.meshgrid(
    np.linspace(X_MIN, X_MAX, 100), np.linspace(Y_MIN, Y_MAX, 80)
)
flat_grid = np.column_stack([grid_x.ravel(), grid_y.ravel()])

# Matriz de pesos RBF (Thin-plate / linear RBF via pinv)
A = cdist(sensor_pts, sensor_pts, metric="euclidean")
H = cdist(flat_grid, sensor_pts, metric="euclidean")
interp_weights = H @ np.linalg.pinv(A)

print(f"Calculando {len(common_timeline)} quadros...")

# Interpola campos contínuos de Temperatura e Umidade
T_grid = (resampled_temp.values @ interp_weights.T).reshape(
    len(common_timeline), grid_y.shape[0], grid_x.shape[1]
)
UR_grid = (resampled_hum.values @ interp_weights.T).reshape(
    len(common_timeline), grid_y.shape[0], grid_x.shape[1]
)

# Cálculo do Índice de Desconforto de Thom (DI)
# DI = T - 0.55 * (1 - 0.01 * UR) * (T - 14.5)
DI_grid = T_grid - 0.55 * (1.0 - 0.01 * UR_grid) * (T_grid - 14.5)

# DI local nos sensores para os rótulos de texto
sens_T = resampled_temp.values
sens_UR = resampled_hum.values
sens_DI = sens_T - 0.55 * (1.0 - 0.01 * sens_UR) * (sens_T - 14.5)

# ==========================================
# 5. CONFIGURAÇÃO VISUAL E COLORMAP
# ==========================================
# Escala de cores personalizada de conforto térmico:
# Azul (<19: frio) -> Verde (20-22: conforto) -> Amarelo (24: leve calor) -> Laranja/Vermelho (>=27: calor crítico)
colors = [
    (0.0, "#2b83ba"),  # Frio / Muito fresco
    (0.3, "#abdda4"),  # Conforto pleno
    (0.5, "#ffffbf"),  # Desconforto leve (<50%)
    (0.75, "#fdae61"),  # Desconforto moderado (>50%)
    (1.0, "#d7191c"),  # Desconforto severo
]
comfort_cmap = LinearSegmentedColormap.from_list("comfort_cmap", colors)

# Faixa fixa de escala térmica para permitir comparação coerente entre frames
DI_VMIN = 16.0
DI_VMAX = 30.0

fig, ax = plt.subplots(figsize=(10.5, 6.8))

heatmap = ax.imshow(
    DI_grid[0],
    origin="lower",
    extent=[X_MIN, X_MAX, Y_MIN, Y_MAX],
    cmap=comfort_cmap,
    vmin=DI_VMIN,
    vmax=DI_VMAX,
    interpolation="bicubic",
)

cbar = fig.colorbar(heatmap, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label(
    "Índice de Thom (°C eq.)\n[<21 Conforto | 21-24 Leve | 24-27 Moderado | >27 Severo]",
    fontsize=9.5,
)

# Posição física dos sensores
ax.scatter(
    sensor_pts[:, 0],
    sensor_pts[:, 1],
    c="white",
    edgecolors="black",
    linewidths=1.5,
    s=90,
    zorder=10,
)

# Textos sobre cada sensor
sensor_labels = []
for sx, sy in sensor_pts:
    t = ax.text(
        sx,
        sy + 0.18,
        "",
        fontsize=8,
        fontweight="bold",
        color="black",
        ha="center",
        zorder=11,
        bbox=dict(
            boxstyle="round,pad=0.2",
            facecolor="white",
            alpha=0.9,
            edgecolor="gray",
            linewidth=0.5,
        ),
    )
    sensor_labels.append(t)

ax.set_xlim(X_MIN, X_MAX)
ax.set_ylim(Y_MIN, Y_MAX)
ax.set_xlabel("Comprimento da Sala - X (m)", fontsize=10)
ax.set_ylabel("Largura da Sala - Y (m)", fontsize=10)


def classify_comfort(di_val):
    if di_val < 21:
        return "Confortável"
    elif di_val < 24:
        return "Desconforto Leve"
    elif di_val < 27:
        return "Desconforto Moderado"
    else:
        return "Desconforto Alto"


def update_frame(frame_idx):
    heatmap.set_data(DI_grid[frame_idx])

    current_time = common_timeline[frame_idx]
    mean_di = np.mean(DI_grid[frame_idx])

    ax.set_title(
        f"DISTRIBUIÇÃO ESPACIAL DE CONFORTO TÉRMICO (ÍNDICE DE THOM)\n"
        f"Data/Hora: {current_time.strftime('%d/%m/%Y às %H:%M:%S')}  |  Média da Sala: {mean_di:.1f} ({classify_comfort(mean_di)})",
        fontsize=10.5,
        fontweight="bold",
        pad=10,
    )

    for label, s_id, t_val, ur_val, di_val in zip(
        sensor_labels,
        active_sensors,
        sens_T[frame_idx],
        sens_UR[frame_idx],
        sens_DI[frame_idx],
    ):
        label.set_text(f"{s_id}\n{t_val:.1f}°C | {ur_val:.0f}%\nDI: {di_val:.1f}")


ani = animation.FuncAnimation(
    fig, update_frame, frames=len(DI_grid), interval=150, blit=False
)

plt.tight_layout()
plt.show()