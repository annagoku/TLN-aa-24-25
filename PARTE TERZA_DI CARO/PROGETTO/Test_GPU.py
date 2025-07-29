import torch

print("CUDA disponibile:", torch.cuda.is_available())
print("Nome GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "Nessuna GPU trovata")
print("Memoria GPU totale (GB):", torch.cuda.get_device_properties(0).total_memory / 1e9 if torch.cuda.is_available() else "N/A")
