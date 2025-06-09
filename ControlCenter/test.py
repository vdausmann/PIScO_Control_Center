import yaml

with open("modules.yaml", "r") as f:
    data = yaml.safe_load(f)

print(data)
