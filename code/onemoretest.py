import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.interpolate import RBFInterpolator

# -------------------------------------------------------------
# 1. Configuração e Dados
# -------------------------------------------------------------
# Substitua pelo caminho do seu arquivo: pd.read_csv("dados.csv")
csv_data = """measured_in,sensor_id,sensor_model,environment,temperature
2026-04-19T13:52:12.028000Z,891,DHT22,1006,22.3
2026-04-19T13:52:14.759000Z,86782,DHT22,1006,25.6
2026-04-19T13:52:17.527000Z,48,DHT22,1006,25.6
2026-04-19T13:52:18.976000Z,887,DHT22,1006,25.6
2026-04-19T13:52:28.332000Z,86791,DHT22,1006,26.1"""

df = pd.read_csv(io.StringIO(csv_data))
df['measured_in'] = pd.to_datetime(df['measured_in'])
df['sensor_id'] = df['sensor_id'].astype(str)

# Dimensões da sala
X_MIN, X_MAX = 0.0, 8.0
Y_MIN, Y_MAX = 0.0, 5.0

# Posições (x, y) de cada sensor dentro da sala (ajuste conforme a disposição real)
SENSOR_COORDS = {
    "891":   (2.0, 2.0),
    "86782": (7.0, 4.0),
    "48":    (7.0, 1.0),
    "887":   (4.0, 1.5),
    "86791": (1.0, 3.5)
}

# -------------------------------------------------------------
# 2. Resampling Temporal dos Sensores
# -------------------------------------------------------------
# Pivota o DataFrame para ter timestamps no índice e sensores nas colunas
pivot_df = df.pivot_table(index='measured_in', columns='sensor_id', values='temperature')

# Reamostra em passos de tempo uniformes (ex: 5s) e preenche valores anteriores
resampled_df = pivot_df.resample('5s').mean().ffill().bfill()

# -------------------------------------------------------------
# 3. Malha de Interpolação e Zona Fixa (16 °C)
# -------------------------------------------------------------
grid_x, grid_y = np.meshgrid(
    np.linspace(X_MIN, X_MAX, 100),
    np.linspace(Y_MIN, Y_MAX, 100)
)
flat_grid = np.column_stack([grid_x.ravel(), grid_y.ravel()])

# Cria pontos de controle na zona fixa (0 < x < 6 e 4 < y < 5) para suavizar a borda
fixed_x = np.linspace(0.0, 6.0, 8)
fixed_y = np.linspace(4.0, 5.0, 4)
FX, FY = np.meshgrid(fixed_x, fixed_y)
fixed_control_pts = np.column_stack([FX.ravel(), FY.ravel()])
fixed_control_vals = np.full(len(fixed_control_pts), 16.0)

# Máscara estrita para garantir 16 °C exatos na região
fixed_mask = (grid_x <= 6.0) & (grid_y >= 4.0)

# Coordenadas fixas dos sensores presentes nos dados
active_sensors = [s for s in resampled_df.columns if s in SENSOR_COORDS]
sensor_pts = np.array([SENSOR_COORDS[s] for s in active_sensors])

def compute_temperature_grid(temperatures_at_step):
    """Interpola a temperatura na sala considerando os sensores e a região de 16 °C."""
    all_pts = np.vstack([sensor_pts, fixed_control_pts])
    all_vals = np.concatenate([temperatures_at_step, fixed_control_vals])
    
    # Interpolação espacial RBF (kernel linear evita picos artificiais)
    rbf = RBFInterpolator(all_pts, all_vals, kernel='linear')
    grid_z = rbf(flat_grid).reshape(grid_x.shape)
    
    # Força a região especificada a permanecer em 16 °C
    grid_z[fixed_mask] = 16.0
    return grid_z

# -------------------------------------------------------------
# 4. Animação do Mapa de Calor
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 6))

initial_temps = resampled_df.iloc[0][active_sensors].values
initial_grid = compute_temperature_grid(initial_temps)

# Escala de cores (15 °C a 30 °C)
vmin, vmax = 15.0, 30.0
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
cbar.set_label('Temperatura (°C)')

# Destaque visual da zona de 16 °C
rect = plt.Rectangle((0, 4), 6, 1, fill=False, edgecolor='cyan', linewidth=2, linestyle='--')
ax.add_patch(rect)
ax.text(3.0, 4.5, 'Zona Fixa (16 °C)', color='cyan', ha='center', va='center', fontweight='bold')

# Plotagem dos sensores físicos
scatter = ax.scatter(sensor_pts[:, 0], sensor_pts[:, 1], c='black', edgecolors='white', s=70, zorder=5)
ax.set_xlim(X_MIN, X_MAX)
ax.set_ylim(Y_MIN, Y_MAX)
ax.set_xlabel('Largura (m)')
ax.set_ylabel('Comprimento (m)')

def update(frame_idx):
    current_time = resampled_df.index[frame_idx]
    current_temps = resampled_df.iloc[frame_idx][active_sensors].values
    
    updated_grid = compute_temperature_grid(current_temps)
    heatmap.set_data(updated_grid)
    ax.set_title(f"Distribuição Térmica da Sala\nHorário: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    return heatmap,

ani = animation.FuncAnimation(
    fig,
    update,
    frames=len(resampled_df),
    interval=600,
    blit=False
)

plt.show()

# Para salvar em arquivo:
# ani.save("mapa_calor.gif", writer="pillow", fps=2)