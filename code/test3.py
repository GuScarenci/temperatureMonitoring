import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.interpolate import RBFInterpolator

# ==========================================
# 1. CAMINHO DOS ARQUIVOS E CONFIGURAÇÕES
# ==========================================
CSV_FILE = "sensor_temperature_24_09_2026.csv"
JSON_FILE = "sensores_meus.json"

# Dimensões da sala: 0 < x < 8 e 0 < y < 5
X_MIN, X_MAX = 0.0, 8.0
Y_MIN, Y_MAX = 0.0, 5.0

# Resolução do tempo (ajuste para 1s, 5s, 10s, 1min, etc. conforme seu volume de dados)
TIME_STEP = "5s"

# ==========================================
# 2. CARREGAR DADOS DOS ARQUIVOS
# ==========================================
# Carrega coordenadas dos sensores do JSON
with open(JSON_FILE, "r", encoding="utf-8") as f:
    raw_coords = json.load(f)
    # Garante que as chaves fiquem como string
    sensor_coords = {
        str(sensor["id"]): (float(sensor["location_x"]), float(sensor["location_y"]))
        for sensor in raw_coords
    }

# Carrega medidas do CSV
df = pd.read_csv(CSV_FILE)
df['measured_in'] = pd.to_datetime(df['measured_in'])
df['sensor_id'] = df['sensor_id'].astype(str)

# ==========================================
# 3. ALINHAMENTO TEMPORAL
# ==========================================
# Transforma em tabela onde linhas são timestamps e colunas são os sensores
pivot_df = df.pivot_table(
    index='measured_in', 
    columns='sensor_id', 
    values='temperature', 
    aggfunc='mean'
)

# Reamostra uniformemente no tempo e propaga a última leitura válida
resampled_df = pivot_df.resample(TIME_STEP).mean().ffill().bfill()

# Sensores válidos que possuem coordenadas mapeadas
active_sensors = [s for s in resampled_df.columns if s in sensor_coords]
if not active_sensors:
    raise ValueError("Nenhum sensor do CSV foi encontrado no arquivo sensores.json!")

sensor_pts = np.array([sensor_coords[s] for s in active_sensors])

# ==========================================
# 4. DEFINIÇÃO DA MALHA E DA ÁREA FIXA (16 °C)
# ==========================================
grid_x, grid_y = np.meshgrid(
    np.linspace(X_MIN, X_MAX, 100),
    np.linspace(Y_MIN, Y_MAX, 100)
)
flat_grid = np.column_stack([grid_x.ravel(), grid_y.ravel()])

# Cria pontos de controle auxiliares na área 0 < x < 6 e 4 < y < 5
# para que a transição de temperatura com o resto da sala fique realista
fixed_x = np.linspace(0.0, 6.0, 10)
fixed_y = np.linspace(4.0, 5.0, 5)
FX, FY = np.meshgrid(fixed_x, fixed_y)
fixed_control_pts = np.column_stack([FX.ravel(), FY.ravel()])
fixed_control_vals = np.full(len(fixed_control_pts), 16.0)

# Máscara estrita para cravar 16 °C nessa região
fixed_mask = (grid_x <= 6.0) & (grid_y >= 4.0)

def interpolate_temperatures(temps):
    """Calcula o campo de temperatura contínuo para o instante atual."""
    pts = np.vstack([sensor_pts, fixed_control_pts])
    vals = np.concatenate([temps, fixed_control_vals])
    
    # RBF com kernel linear para interpolação suave sem criar picos absurdos
    rbf = RBFInterpolator(pts, vals, kernel='linear')
    grid_z = rbf(flat_grid).reshape(grid_x.shape)
    
    # Força os 16 °C exatos na região solicitada
    grid_z[fixed_mask] = 16.0
    return grid_z

# ==========================================
# 5. RENDERIZAÇÃO DA ANIMAÇÃO
# ==========================================
fig, ax = plt.subplots(figsize=(9, 6))

# Frame inicial
initial_temps = resampled_df.iloc[0][active_sensors].values
initial_grid = interpolate_temperatures(initial_temps)

# Escala de cores (vmin/vmax fixos evitam que a cor mude de escala a cada frame)
vmin = min(15.0, resampled_df[active_sensors].min().min())
vmax = max(30.0, resampled_df[active_sensors].max().max())

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

# Desenha o retângulo demarcando a região fixa de 16 °C
rect = plt.Rectangle((0, 4), 6, 1, fill=False, edgecolor='blue', linewidth=2, linestyle='--')
ax.add_patch(rect)
ax.text(3.0, 4.5, 'Zona Fixa (16 °C)', color='blue', ha='center', va='center', fontweight='bold')

# Pontos físicos onde estão os sensores com os respectivos IDs
ax.scatter(sensor_pts[:, 0], sensor_pts[:, 1], c='black', edgecolors='white', s=80, zorder=5)
for s_id, (sx, sy) in zip(active_sensors, sensor_pts):
    ax.text(sx + 0.1, sy + 0.1, f"ID: {s_id}", fontsize=9, fontweight='bold', color='black')

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

# Cria o objeto de animação
ani = animation.FuncAnimation(
    fig,
    update_frame,
    frames=len(resampled_df),
    interval=500,  # 500 ms entre cada frame na tela (meio segundo)
    blit=False
)

# Abre a janela interativa com a animação rodando
plt.tight_layout()
plt.show()

# Para exportar para vídeo ou GIF, descomente a linha correspondente:
# ani.save("animacao_sala.gif", writer="pillow", fps=2)
# ani.save("animacao_sala.mp4", writer="ffmpeg", fps=2)