import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.spatial.distance import cdist

# ==========================================
# 1. ARQUIVOS E DIMENSÕES DA SALA
# ==========================================
CSV_FILE = "sensor_humidity_24_09_2026.csv"  # Coloque o nome do seu arquivo CSV de umidade
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
    
    # Filtra sensores que pertencem ao perímetro da sala
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
    values='humidity',
    aggfunc='mean'
)

# Filtra colunas válidas que existem no JSON e no CSV
active_sensors = [s for s in pivot_df.columns if s in sensor_coords]

if len(active_sensors) < 3:
    raise ValueError(f"Poucos sensores ativos mapeados ({len(active_sensors)}). Mínimo de 3 necessário.")

resampled_df = pivot_df[active_sensors].resample(TIME_STEP).mean().ffill().bfill()
sensor_pts = np.array([sensor_coords[s] for s in active_sensors])

# ==========================================
# 4. PRÉ-CÁLCULO MATRICIAL (RÁPIDO)
# ==========================================
grid_x, grid_y = np.meshgrid(
    np.linspace(X_MIN, X_MAX, 100),
    np.linspace(Y_MIN, Y_MAX, 80)
)
flat_grid = np.column_stack([grid_x.ravel(), grid_y.ravel()])

# Matriz RBF
A = cdist(sensor_pts, sensor_pts, metric='euclidean')
H = cdist(flat_grid, sensor_pts, metric='euclidean')
interp_weights = H @ np.linalg.pinv(A)

print(f"Calculando {len(resampled_df)} frames...")
all_humidity = resampled_df.values
interpolated_all = (all_humidity @ interp_weights.T).reshape(len(resampled_df), grid_y.shape[0], grid_x.shape[1])

# ==========================================
# 5. CONFIGURAÇÃO DA FIGURA E ANIMAÇÃO
# ==========================================
fig, ax = plt.subplots(figsize=(10, 6.5))

vmin = np.nanmin(interpolated_all)
vmax = np.nanmax(interpolated_all)

heatmap = ax.imshow(
    interpolated_all[0],
    origin='lower',
    extent=[X_MIN, X_MAX, Y_MIN, Y_MAX],
    cmap='YlGnBu',  # Paleta ideal para umidade (seco/amarelo para úmido/azul escuro)
    vmin=vmin,
    vmax=vmax,
    interpolation='bicubic'
)

cbar = fig.colorbar(heatmap, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('Umidade Relativa (%)', fontsize=11)

# Plota sensores
ax.scatter(
    sensor_pts[:, 0], 
    sensor_pts[:, 1], 
    c='yellow', 
    edgecolors='black', 
    linewidths=1.5, 
    s=90, 
    zorder=10
)

# Textos com os rótulos de cada sensor
sensor_labels = []
for (sx, sy) in sensor_pts:
    t = ax.text(
        sx, sy + 0.18, "", 
        fontsize=8, 
        fontweight='bold', 
        color='black', 
        ha='center',
        zorder=11,
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.85, edgecolor="gray", linewidth=0.5)
    )
    sensor_labels.append(t)

ax.set_xlim(X_MIN, X_MAX)
ax.set_ylim(Y_MIN, Y_MAX)
ax.set_xlabel('Comprimento da Sala - X (m)', fontsize=10)
ax.set_ylabel('Largura da Sala - Y (m)', fontsize=10)

def update_frame(frame_idx):
    heatmap.set_data(interpolated_all[frame_idx])
    
    # Cabeçalho com data e hora atualizada
    current_time = resampled_df.index[frame_idx]
    ax.set_title(
        f"DISTRIBUIÇÃO DE UMIDADE RELATIVA DA SALA\nRegistro: {current_time.strftime('%d/%m/%Y às %H:%M:%S')}",
        fontsize=11,
        fontweight='bold',
        pad=10
    )
    
    # Atualiza cada sensor com ID e umidade (%)
    for label, s_id, hum in zip(sensor_labels, active_sensors, all_humidity[frame_idx]):
        label.set_text(f"{s_id} ({hum:.1f}%)")

ani = animation.FuncAnimation(
    fig,
    update_frame,
    frames=len(interpolated_all),
    interval=100,
    blit=False  # Mantido False para evitar o erro do Tkinter no Windows
)

plt.tight_layout()
plt.show()