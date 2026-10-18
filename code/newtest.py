import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.interpolate import RBFInterpolator

# ==========================================
# 1. ARQUIVOS E DIMENSÕES DA SALA
# ==========================================
CSV_FILE = "sensor_temperature_24_09_2026.csv"
JSON_FILE = "sensores_meus.json"

X_MIN, X_MAX = 0.0, 8.0
Y_MIN, Y_MAX = 0.0, 5.0
TIME_STEP = "1h"

# ==========================================
# 2. CARREGAR COORDENADAS DO JSON
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
# 3. CARREGAR E ALINHAR MEDIDAS DO CSV
# ==========================================
df = pd.read_csv(CSV_FILE)
df['measured_in'] = pd.to_datetime(df['measured_in'])
df['sensor_id'] = df['sensor_id'].astype(str)

pivot_df = df.pivot_table(
    index='measured_in',
    columns='sensor_id',
    values='temperature',
    aggfunc='mean'
)

# Filtra colunas válidas ANTES de qualquer interpolação
active_sensors = [s for s in pivot_df.columns if s in sensor_coords]

if len(active_sensors) < 3:
    raise ValueError(f"Poucos sensores ativos mapeados ({len(active_sensors)}). Mínimo de 3 necessário.")

# Alinha e preenche somente os sensores ativos
resampled_df = pivot_df[active_sensors].resample(TIME_STEP).mean().ffill().bfill()
sensor_pts = np.array([sensor_coords[s] for s in active_sensors])

# ==========================================
# 4. MALHA ESPACIAL E INTERPOLAÇÃO
# ==========================================
grid_x, grid_y = np.meshgrid(
    np.linspace(X_MIN, X_MAX, 120),
    np.linspace(Y_MIN, Y_MAX, 100)
)
flat_grid = np.column_stack([grid_x.ravel(), grid_y.ravel()])

def interpolate_temperatures(temps):
    rbf = RBFInterpolator(sensor_pts, temps, kernel='linear')
    return rbf(flat_grid).reshape(grid_x.shape)

# ==========================================
# 5. PRÉ-CÁLCULO E ANIMAÇÃO
# ==========================================
print(f"Pré-calculando {len(resampled_df)} frames...")
frames_data = [
    interpolate_temperatures(resampled_df.iloc[i].values)
    for i in range(len(resampled_df))
]

fig, ax = plt.subplots(figsize=(10, 6))

# Limites baseados no resultado final das interpolações
vmin = min(f.min() for f in frames_data)
vmax = max(f.max() for f in frames_data)

heatmap = ax.imshow(
    frames_data[0],
    origin='lower',
    extent=[X_MIN, X_MAX, Y_MIN, Y_MAX],
    cmap='coolwarm',
    vmin=vmin,
    vmax=vmax,
    interpolation='bicubic'
)

cbar = fig.colorbar(heatmap, ax=ax)
cbar.set_label('Temperatura (°C)', fontsize=11)

ax.scatter(sensor_pts[:, 0], sensor_pts[:, 1], c='black', edgecolors='white', s=70, zorder=5)
for s_id, (sx, sy) in zip(active_sensors, sensor_pts):
    ax.text(sx + 0.1, sy + 0.1, s_id, fontsize=8, fontweight='bold', color='black', zorder=6)

ax.set_xlim(X_MIN, X_MAX)
ax.set_ylim(Y_MIN, Y_MAX)
ax.set_xlabel('X (metros)')
ax.set_ylabel('Y (metros)')
title_text = ax.set_title("", fontsize=12)

def update_frame(frame_idx):
    heatmap.set_data(frames_data[frame_idx])
    current_time = resampled_df.index[frame_idx]
    title_text.set_text(f"Horário: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    return heatmap, title_text

ani = animation.FuncAnimation(
    fig,
    update_frame,
    frames=len(frames_data),
    interval=20,
    blit=True
)

plt.tight_layout()
plt.show()