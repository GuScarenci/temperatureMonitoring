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

# Dimensões da sala: 0 < x < 8 e 0 < y < 5
X_MIN, X_MAX = 0.0, 8.0
Y_MIN, Y_MAX = 0.0, 5.0

# Passo de tempo para sincronizar leituras (ex: "5s", "10s", "1min")
TIME_STEP = "5s"

# ==========================================
# 2. CARREGAR COORDENADAS DO JSON
# ==========================================
with open(JSON_FILE, "r", encoding="utf-8") as f:
    sensors_list = json.load(f)

# Mapeia id -> (location_x, location_y) apenas para sensores dentro dos limites da sala
sensor_coords = {}
for s in sensors_list:
    s_id = str(s["id"])
    x = float(s["location_x"])
    y = float(s["location_y"])
    
    # Filtra sensores que pertencem à geometria desta sala
    if X_MIN <= x <= X_MAX and Y_MIN <= y <= Y_MAX:
        sensor_coords[s_id] = (x, y)

# ==========================================
# 3. CARREGAR E ALINHAR MEDIDAS DO CSV
# ==========================================
df = pd.read_csv(CSV_FILE)
df['measured_in'] = pd.to_datetime(df['measured_in'])
df['sensor_id'] = df['sensor_id'].astype(str)

# Pivot table: timestamps nas linhas, IDs nas colunas
pivot_df = df.pivot_table(
    index='measured_in',
    columns='sensor_id',
    values='temperature',
    aggfunc='mean'
)

# Reamostra o tempo e preenche eventuais lacunas
resampled_df = pivot_df.resample(TIME_STEP).mean().ffill().bfill()

# Identifica sensores presentes simultaneamente no CSV e com coordenadas mapeadas
active_sensors = [s for s in resampled_df.columns if s in sensor_coords]

if len(active_sensors) < 3:
    raise ValueError(f"Poucos sensores ativos mapeados ({len(active_sensors)}). Necessário pelo menos 3 para interpolação 2D.")

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
    """Interpola as temperaturas em toda a sala baseando-se puramente nos sensores."""
    # RBF linear garante transições suaves sem extrapolações extremas
    rbf = RBFInterpolator(sensor_pts, temps, kernel='linear')
    return rbf(flat_grid).reshape(grid_x.shape)

# ==========================================
# 5. ANIMAÇÃO
# ==========================================
fig, ax = plt.subplots(figsize=(10, 6))

initial_temps = resampled_df.iloc[0][active_sensors].values
initial_grid = interpolate_temperatures(initial_temps)

# Escala de cores fixa ao longo de toda a gravação
vmin = resampled_df[active_sensors].min().min()
vmax = resampled_df[active_sensors].max().max()

heatmap = ax.imshow(
    initial_grid,
    origin='lower',
    extent=[X_MIN, X_MAX, Y_MIN, Y_MAX],
    cmap='coolwarm',
    vmin=vmin,
    vmax=vmax,
    interpolation='bicubic'
)

cbar = fig.colorbar(heatmap, ax=ax)
cbar.set_label('Temperatura (°C)', fontsize=11)

# Plotagem da posição física de cada sensor
ax.scatter(sensor_pts[:, 0], sensor_pts[:, 1], c='black', edgecolors='white', s=70, zorder=5)
for s_id, (sx, sy) in zip(active_sensors, sensor_pts):
    ax.text(sx + 0.1, sy + 0.1, s_id, fontsize=8, fontweight='bold', color='black', zorder=6)

ax.set_xlim(X_MIN, X_MAX)
ax.set_ylim(Y_MIN, Y_MAX)
ax.set_xlabel('X (metros)')
ax.set_ylabel('Y (metros)')

def update_frame(frame_idx):
    current_time = resampled_df.index[frame_idx]
    current_temps = resampled_df.iloc[frame_idx][active_sensors].values
    
    updated_grid = interpolate_temperatures(current_temps)
    heatmap.set_data(updated_grid)
    ax.set_title(
        f"Distribuição Térmica da Sala\nHorário: {current_time.strftime('%Y-%m-%d %H:%M:%S')}",
        fontsize=12
    )
    return heatmap,

ani = animation.FuncAnimation(
    fig,
    update_frame,
    frames=len(resampled_df),
    interval=1,  # 400ms por frame
    blit=False
)

plt.tight_layout()
plt.show()

# Para exportar para vídeo ou GIF:
# ani.save("animacao_sala.gif", writer="pillow", fps=2)
# ani.save("animacao_sala.mp4", writer="ffmpeg", fps=2)