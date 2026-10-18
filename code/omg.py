import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.spatial.distance import cdist

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

active_sensors = [s for s in pivot_df.columns if s in sensor_coords]

if len(active_sensors) < 3:
    raise ValueError(f"Poucos sensores ativos mapeados ({len(active_sensors)}). Mínimo de 3 necessário.")

resampled_df = pivot_df[active_sensors].resample(TIME_STEP).mean().ffill().bfill()
sensor_pts = np.array([sensor_coords[s] for s in active_sensors])

# ==========================================
# 4. PRÉ-CÁLCULO MATRICIAL E MALHA
# ==========================================
NX, NY = 100, 80
dx = (X_MAX - X_MIN) / (NX - 1)
dy = (Y_MAX - Y_MIN) / (NY - 1)

grid_x, grid_y = np.meshgrid(
    np.linspace(X_MIN, X_MAX, NX),
    np.linspace(Y_MIN, Y_MAX, NY)
)
flat_grid = np.column_stack([grid_x.ravel(), grid_y.ravel()])

A = cdist(sensor_pts, sensor_pts, metric='euclidean')
H = cdist(flat_grid, sensor_pts, metric='euclidean')
interp_weights = H @ np.linalg.pinv(A)

print(f"Calculando {len(resampled_df)} frames...")
all_temps = resampled_df.values
interpolated_all = (all_temps @ interp_weights.T).reshape(len(resampled_df), NY, NX)

# ==========================================
# 5. CONFIGURAÇÃO DA FIGURA E DO QUIVER (SETAS)
# ==========================================
fig, ax = plt.subplots(figsize=(10, 6.5))

vmin = np.nanmin(interpolated_all)
vmax = np.nanmax(interpolated_all)

heatmap = ax.imshow(
    interpolated_all[0],
    origin='lower',
    extent=[X_MIN, X_MAX, Y_MIN, Y_MAX],
    cmap='coolwarm',
    vmin=vmin,
    vmax=vmax,
    interpolation='bicubic'
)

cbar = fig.colorbar(heatmap, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('Temperatura (°C)', fontsize=11)

# Amostragem das setas (pega 1 a cada N pontos para não sobrecarregar o visual)
STEP = 4
qx = grid_x[::STEP, ::STEP]
qy = grid_y[::STEP, ::STEP]

# Calcula o gradiente do primeiro frame (-dT/dx e -dT/dy representam o fluxo de calor)
dT_dy_init, dT_dx_init = np.gradient(interpolated_all[0], dy, dx)
u_init = -dT_dx_init[::STEP, ::STEP]
v_init = -dT_dy_init[::STEP, ::STEP]

# Normaliza para que as setas tenham comprimento visual proporcional e estável
mag_init = np.hypot(u_init, v_init)
mag_init[mag_init == 0] = 1e-6

quiver = ax.quiver(
    qx, qy, 
    u_init / mag_init, 
    v_init / mag_init,
    # u_init / mag_init, 
    # v_init / mag_init,
    color='black',
    alpha=0.55,
    scale=32,
    width=0.0022,
    headwidth=3.5,
    headlength=4,
    zorder=8
)

# Plota os sensores físicos
ax.scatter(
    sensor_pts[:, 0], 
    sensor_pts[:, 1], 
    c='yellow', 
    edgecolors='black', 
    linewidths=1.5, 
    s=90, 
    zorder=10
)

# Rótulos de cada sensor
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

# ==========================================
# 6. ATUALIZAÇÃO DA ANIMAÇÃO
# ==========================================
def update_frame(frame_idx):
    T_curr = interpolated_all[frame_idx]
    
    # 1. Atualiza o mapa térmico
    heatmap.set_data(T_curr)
    
    # 2. Atualiza os vetores de fluxo térmico (-gradiente)
    dT_dy, dT_dx = np.gradient(T_curr, dy, dx)
    u = -dT_dx[::STEP, ::STEP]
    v = -dT_dy[::STEP, ::STEP]
    
    mag = np.hypot(u, v)
    mag[mag == 0] = 1e-6
    quiver.set_UVC(u / mag, v / mag)
    
    # 3. Cabeçalho com data/hora
    current_time = resampled_df.index[frame_idx]
    ax.set_title(
        f"DISTRIBUIÇÃO E FLUXO TÉRMICO DA SALA\nRegistro: {current_time.strftime('%d/%m/%Y às %H:%M:%S')}",
        fontsize=11,
        fontweight='bold',
        pad=10
    )
    
    # 4. Atualiza valores nos nós dos sensores
    for label, s_id, temp in zip(sensor_labels, active_sensors, all_temps[frame_idx]):
        label.set_text(f"{s_id} ({temp:.1f}°C)")

ani = animation.FuncAnimation(
    fig,
    update_frame,
    frames=len(interpolated_all),
    interval=100,  # 100ms por frame para permitir visualização suave
    blit=False
)

plt.tight_layout()
plt.show()