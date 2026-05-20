import torch
import torch_geometric
import psutil

# 1. Auditoría del Motor Tensorial y Hardware
print("=== AUDITORÍA DE INFRAESTRUCTURA LOCAL ===")
print(f"Versión de PyTorch: {torch.__version__}")
print(f"Versión de PyG: {torch_geometric.__version__}")

# 2. Validación de CUDA (Crítico)
if torch.cuda.is_available():
    device = torch.cuda.get_device_name(0)
    vram_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    print(f"\n[ÉXITO] Motor CUDA detectado.")
    print(f"GPU Asignada: {device}")
    print(f"VRAM Total Disponible: {vram_total:.2f} GB")
else:
    print("\n[ERROR FATAL] PyTorch no detecta tu tarjeta NVIDIA. El entrenamiento caerá a la CPU.")

# 3. Auditoría de Memoria RAM del Sistema
ram = psutil.virtual_memory()
print(f"\nRAM del Sistema Disponible: {ram.available / (1024**3):.2f} GB")