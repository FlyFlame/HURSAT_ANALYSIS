import xarray as xr
import matplotlib.pyplot as plt
import glob
import os
import imageio.v2 as imageio
from PIL import Image


folder = "sem dej cestu borecku"
files = sorted(glob.glob(os.path.join(folder, "*.nc")))

frames = []
times = []
images = []
eye_temps = []
centers_lat = []
centers_lon = []


for file in files:
    ds = xr.open_dataset(file, engine="netcdf4")
    ir = ds['IRWIN'] # tady můše měnit variables, teď tam jsou hodnoty infračerveného záření pro teplotu
    scale = ir.attrs.get("scale_factor", 1)
    offset = ir.attrs.get("add_offset", 0)
    ir_scaled = ir * scale + offset
    frames.append(ir_scaled.squeeze())

    timestamp = str(ds['htime'].values[0])[:16]
    times.append(timestamp)

    # Střed bouře
    centers_lat.append(float(ds['CentLat'].values))
    centers_lon.append(float(ds['CentLon'].values))

    # Teplota v oku bouře
    eye_temp = float(ds['bt_eye'].values) if 'bt_eye' in ds else float('nan')
    eye_temps.append(eye_temp)


global_min = min([float(f.min()) for f in frames])
global_max = max([float(f.max()) for f in frames])


tmp_folder = os.path.join(folder, "frames_tmp")
os.makedirs(tmp_folder, exist_ok=True)

for i, ir in enumerate(frames):
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(ir, cmap='coolwarm', vmin=global_min, vmax=global_max)
    ax.set_title(f"IRWIN @ {times[i]}")
    plt.axis('off')
    plt.colorbar(im, ax=ax, label="Teplota (K)")
    ax.plot(150, 150, 'wo')  # fixní bod na středu gridu (přibližný střed bouře)
    tmpfile = os.path.join(tmp_folder, f"frame_{i:03d}.png")
    plt.savefig(tmpfile, bbox_inches='tight', pad_inches=0.1)
    plt.close()

# GIF
for file in sorted(glob.glob(os.path.join(tmp_folder, "*.png"))):
    img = Image.open(file).convert("RGB")
    images.append(img)

output_gif = os.path.join(folder, "IRWIN_animation.gif")
images[0].save(output_gif, save_all=True, append_images=images[1:], duration=500, loop=0)


plt.figure(figsize=(8, 4))
plt.plot(times, eye_temps, marker='o', linestyle='-', color='red')
plt.title("Vývoj teploty v oku bouře")
plt.xticks(rotation=45, ha='right')
plt.ylabel("Teplota v oku (K)")
plt.grid(True)
plt.tight_layout()
eye_graph_path = os.path.join(folder, "eye_temperature_plot.png")
plt.savefig(eye_graph_path)
plt.close()

# Úklid
for file in glob.glob(os.path.join(tmp_folder, "*.png")):
    os.remove(file)
os.rmdir(tmp_folder)

(output_gif, eye_graph_path)
