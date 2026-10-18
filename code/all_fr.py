import json
import os
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import griddata

# 1. Carregar dispositivos e posições confirmadas
with open("devices_temphum.json", "r", encoding="utf-8") as f:
    devices = json.load(f)

df_devices = pd.DataFrame(devices)
df_devices["id"] = df_devices["id"].astype(str)

# Manter apenas sensores com posição física confirmada
df_sensors = df_devices[
    (df_devices["location_confirmed"] == True)
    & df_devices["location_x"].notna()
    & df_devices["location_y"].notna()
].copy()

# 2. Carregar dados consolidados
df_results = pd.read_csv("results.csv")
df_results["sensor_id"] = df_results["sensor_id"].astype(str)
df_results["measured_in"] = pd.to_datetime(df_results["measured_in"])

# Filtrar apenas leituras dos sensores que possuem coordenadas
df_results = df_results[df_results["sensor_id"].isin(df_sensors["id"])].copy()

# 3. Discretizar o tempo em janelas (ex: '5min', '10min' ou '15min')
# Isso sincroniza os sensores que transmitem com alguns segundos de diferença
df_results["time_window"] = df_results["measured_in"].dt.floor("5min")

# Tabela dinâmica indexada no tempo com interpolação para cobrir perdas pontuais de sinal
pivot_temp = df_results.pivot_table(
    index="time_window",
    columns="sensor_id",
    values="temperature",
    aggfunc="mean",
)
pivot_hum = df_results.pivot_table(
    index="time_window", columns="sensor_id", values="humidity", aggfunc="mean"
)

# Preenchimento contínuo para evitar que um frame falhe por falta de leitura
pivot_temp = pivot_temp.ffill().bfill()
pivot_hum = pivot_hum.ffill().bfill()

timestamps = pivot_temp.index
print(f"Total de janelas de tempo para animar: {len(timestamps)}")

# 4. Configurar a grelha de interpolação espacial (0 a 8 em X, 0 a 5 em Y)
grid_x, grid_y = np.mgrid[0:8:200j, 0:5:200j]

# Escala fixa de temperatura para que as cores sejam consistentes ao longo do tempo
vmin = np.nanpercentile(df_results["temperature"], 5)
vmax = np.nanpercentile(df_results["temperature"], 95)


def get_comfort(temp, hum):
    if 20.0 <= temp <= 26.0 and 30.0 <= hum <= 65.0:
        return "Confortável", "#2ecc71"
    elif temp > 26.0:
        return "Quente", "#e74c3c"
    elif temp < 20.0:
        return "Frio", "#3498db"
    return "Desconfortável", "#e67e22"


# 5. Criar a figura base
fig, ax = plt.subplots(figsize=(11, 7))
cax = None
cbar = None

# Diretório para salvar imagens estáticas se desejar
os.makedirs("frames", exist_ok=True)


def update(frame_idx):
    global cax, cbar
    ax.clear()

    ts = timestamps[frame_idx]
    current_temps = pivot_temp.loc[ts]
    current_hums = pivot_hum.loc[ts]

    # Montar coordenadas e valores do instante atual
    coords = []
    temps = []
    hums = []
    names = []

    for _, sensor in df_sensors.iterrows():
        sid = sensor["id"]
        if sid in current_temps and not pd.isna(current_temps[sid]):
            coords.append([sensor["location_x"], sensor["location_y"]])
            temps.append(current_temps[sid])
            hums.append(current_hums[sid])
            names.append(sensor.get("name", sid))

    pontos = np.array(coords)
    valores_temp = np.array(temps)

    # Interpolação espacial
    try:
        grid_temp = griddata(
            pontos, valores_temp, (grid_x, grid_y), method="linear"
        )
        grid_near = griddata(
            pontos, valores_temp, (grid_x, grid_y), method="nearest"
        )
        grid_temp[np.isnan(grid_temp)] = grid_near[np.isnan(grid_temp)]
    except Exception:
        grid_temp = griddata(
            pontos, valores_temp, (grid_x, grid_y), method="nearest"
        )

    # Renderiza o mapa de calor com escala fixa (vmin/vmax)
    im = ax.imshow(
        grid_temp.T,
        extent=(0, 8, 0, 5),
        origin="lower",
        cmap="coolwarm",
        aspect="auto",
        alpha=0.85,
        vmin=vmin,
        vmax=vmax,
    )

    # Anotações dos sensores
    for i in range(len(pontos)):
        x, y = pontos[i]
        t = valores_temp[i]
        h = hums[i]
        status, cor = get_comfort(t, h)

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
            f"{names[i]}\nT: {t:.1f}°C | H: {h:.0f}%\n[{status}]",
            (x, y),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontsize=8,
            fontweight="semibold",
            bbox=dict(
                boxstyle="round,pad=0.2",
                facecolor="white",
                alpha=0.9,
                edgecolor=cor,
            ),
            zorder=6,
        )

    # Ajustes estéticos dos eixos
    ax.set_xlim(-0.5, 8.5)
    ax.set_ylim(-0.5, 5.5)
    ax.set_xticks(range(0, 9))
    ax.set_yticks(range(0, 6))
    ax.set_xlabel("Eixo X (metros)")
    ax.set_ylabel("Eixo Y (metros)")
    ax.set_title(
        f"Distribuição Térmica no Tempo - Sala 1006\nHorário: {ts.strftime('%Y-%m-%d %H:%M')}",
        fontsize=12,
        fontweight="bold",
    )
    ax.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.4)

    # Salva imagem individual (frame)
    plt.savefig(
        f"frames/frame_{frame_idx:04d}.png", dpi=150, bbox_inches="tight"
    )

    return (im,)


# 6. Adicionar Barra de Cores fixa antes da animação
cax_init = ax.imshow(
    np.zeros((200, 200)), cmap="coolwarm", vmin=vmin, vmax=vmax
)
cbar = fig.colorbar(cax_init, ax=ax, pad=0.02)
cbar.set_label("Temperatura (°C)", fontsize=11, fontweight="bold")

# 7. Gerar e salvar a animação
ani = animation.FuncAnimation(
    fig, update, frames=len(timestamps), interval=500, blit=False
)

print("Gerando GIF animado ('mapa_termico_evolucao.gif')...")
ani.save("mapa_termico_evolucao.gif", writer="pillow", fps=2)

# Se tiver o ffmpeg instalado e quiser MP4:
# ani.save("mapa_termico_evolucao.mp4", writer="ffmpeg", fps=2)

print(
    "Processo concluído! GIF salvo na raiz e frames individuais salvos na pasta /frames."
)