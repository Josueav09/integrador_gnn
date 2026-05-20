import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from pathlib import Path

# Importamos nuestros propios módulos locales
from data.dataset import preparar_dataloaders
from model.st_gnn import RedEspacioTemporal

def main():
    # 1. Definición estricta de Hardware y Rutas
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"=== INICIANDO SISTEMA PREDICTIVO PNP ===")
    print(f"Hardware asignado: {device}")

    # Rutas dinámicas e infalibles (Agnósticas al OS)
    BASE_DIR = Path(__file__).resolve().parent.parent
    RUTA_PARQUET = BASE_DIR / "data" / "processed" / "tensor_panel_diario.parquet"
    RUTA_GRAFO = BASE_DIR / "data" / "processed" / "grafo_edge_index.npz"

    # 2. Cargar Dataloaders (Protección de RAM activa)
    train_loader, test_loader, scaler_y = preparar_dataloaders(
        ruta_parquet=RUTA_PARQUET, 
        ventana_dias=14, 
        batch_size=32  # Digerimos de a pocos
    )

    # 3. Cargar la Topología (Grafo)
    print("Cargando matriz de adyacencia urbana...")
    grafo_data = np.load(RUTA_GRAFO)
    
    # IMPORTANTE: Enviamos el mapa estático directamente a la VRAM de la GPU
    edge_index = torch.tensor(grafo_data['edge_index'], dtype=torch.long).to(device)
    edge_weights = torch.tensor(grafo_data['edge_weights'], dtype=torch.float32).to(device)

    # 4. Instanciar el Modelo, Optimizador y Función de Pérdida
    # Usaremos 64 unidades ocultas para aprovechar tu RTX 3050
    modelo = RedEspacioTemporal(num_features=5, unidades_ocultas=64).to(device)
    criterio = nn.L1Loss() # Error Absoluto Medio (MAE)
    optimizador = optim.Adam(modelo.parameters(), lr=0.001)

    # 5. El Bucle de Entrenamiento (Training Loop)
    EPOCHS = 15
    print("\nComenzando entrenamiento (Training Loop)...")
    
    for epoch in range(EPOCHS):
        modelo.train()
        loss_acumulada = 0.0
        
        for batch_idx, (batch_x, batch_y) in enumerate(train_loader):
            # Movemos los lotes a la GPU de forma dinámica
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)

            # Limpiar memoria residual
            optimizador.zero_grad()

            # Fase Forward (Adivinar)
            predicciones = modelo(batch_x, edge_index, edge_weights)
            
            # Calcular error
            loss = criterio(predicciones, batch_y)
            
            # Fase Backward (Aprender)
            loss.backward()
            optimizador.step()

            loss_acumulada += loss.item()

        loss_promedio = loss_acumulada / len(train_loader)
        print(f"Epoch [{epoch+1:02d}/{EPOCHS}] - MAE Train Loss: {loss_promedio:.4f}")

    print("=== ENTRENAMIENTO FINALIZADO ===")
    
    # 6. Guardar los pesos del modelo para usarlos en producción
    ruta_guardado = BASE_DIR / "src" / "model" / "pesos_stgnn_pnp.pth"
    torch.save(modelo.state_dict(), ruta_guardado)
    print(f"Modelo guardado exitosamente en: {ruta_guardado}")

if __name__ == "__main__":
    main()