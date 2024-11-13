import os

# get the current file path
base_dir = os.path.dirname(os.path.realpath(__file__))

# Package Executable Paths
ffmpeg_path = os.path.join(base_dir, "..", "packages", "ffmpeg", "ffmpeg.exe")

# File paths
config_path = os.path.join(base_dir, "..", "config.env")

# App Icon Paths
app_logo_png = os.path.join(base_dir, "app_logo.png")
app_logo_ico = os.path.join(base_dir, "app_logo.ico")
app_logo_icns = os.path.join(base_dir, "app_logo.icns")

# Connection Icon Paths
connection_down = os.path.join(base_dir, "icons/connection/connection_down.png")
connection_up = os.path.join(base_dir, "icons/connection/connection_up.png")
connection_idle = os.path.join(base_dir, "icons/connection/connection_idle.png")
connection_loading = os.path.join(base_dir, "icons/connection/connection_loading.png")

# Toolbar Icon Paths
new = os.path.join(base_dir, "icons/toolbar/new.png")
open = os.path.join(base_dir, "icons/toolbar/open.png")
save = os.path.join(base_dir, "icons/toolbar/save.png")
saveas = os.path.join(base_dir, "icons/toolbar/saveas.png")
export = os.path.join(base_dir, "icons/toolbar/export.png")
settings = os.path.join(base_dir, "icons/toolbar/settings.png")
play = os.path.join(base_dir, "icons/toolbar/play.png")
cancel = os.path.join(base_dir, "icons/toolbar/cancel.png")
calculate = os.path.join(base_dir, "icons/toolbar/calculate.png")
collect = os.path.join(base_dir, "icons/toolbar/collect.png")
clear = os.path.join(base_dir, "icons/toolbar/clear.png")

# Data Browser Icon Paths
data_card_delete = os.path.join(base_dir, "icons/data_browser/data_card_delete.png")
db_calculated = os.path.join(base_dir, "icons/data_browser/db_calculated.png")
db_collected = os.path.join(base_dir, "icons/data_browser/db_collected.png")
db_loaded = os.path.join(base_dir, "icons/data_browser/db_loaded.png")
default_preview = os.path.join(base_dir, "icons/data_browser/default_preview.png")
