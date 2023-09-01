import importlib


for settings_name in "aaron.base_settings", "aaron.user_settings":
    try:
        mod = importlib.import_module(settings_name)
    except ImportError:
        continue

    for name in dir(mod):
        if not name.startswith("__"):
            locals()[name] = getattr(mod, name)
