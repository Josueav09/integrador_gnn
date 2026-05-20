import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import MinMaxScaler

class CrimeSpatiotemporalDataset(Dataset):
    """
    Clase de PyTorch para Carga Perezosa (Lazy Loading).
    Solo mantiene la matriz matriz original en RAM y extrae ventanas bajo demanda.
    """
    def __init__(self, data_3d_tensor, ventana_dias=14):
        self.data_3d = data_3d_tensor
        self.ventana_dias = ventana_dias

    def __len__(self):
        # La cantidad total de "exámenes" que podemos generar
        return len(self.data_3d) - self.ventana_dias

    def __getitem__(self, idx):
        # LAZY LOADING: Solo leemos el fragmento exacto para este lote
        
        # X: Historial de 14 días -> [14, 400, 5]
        x_window = self.data_3d[idx : idx + self.ventana_dias]
        
        # Y: El conteo de delitos del día 15. Índice 0 es 'conteo_delitos' -> [400]
        y_target = self.data_3d[idx + self.ventana_dias, :, 0]
        
        return x_window, y_target


def preparar_dataloaders(ruta_parquet, ventana_dias=14, batch_size=32):
    """
    Función maestra que orquesta la lectura, el split cronológico, 
    el escalamiento MinMax y devuelve los DataLoaders listos para entrenar.
    """
    print("Cargando y estructurando datos (Lazy Loading Mode)...")
    
    # 1. Carga inicial y orden estricto
    df = pd.read_parquet(ruta_parquet)
    df = df.sort_values(by=['fecha_delito', 'id_nodo'])
    
    num_dias = len(df['fecha_delito'].unique())
    num_nodos = 400
    columnas_features = ['conteo_delitos', 'dia_semana', 'es_fin_semana', 'mes_sin', 'mes_cos']
    
    # 2. Única matriz 3D en RAM (Pesa menos de 15 MB)
    matriz_3d = df[columnas_features].values.reshape(num_dias, num_nodos, len(columnas_features))
    
    # 3. Corte Cronológico (80% Train, 20% Test)
    limite_train = int(num_dias * 0.8)
    
    # Dividimos la matriz base
    train_data = matriz_3d[:limite_train]
    test_data = matriz_3d[limite_train:]
    
    # 4. Prevención de Data Leakage (Escalamiento)
    scaler_y = MinMaxScaler() # Necesitamos devolverlo para evaluar después
    scaler_x = MinMaxScaler()
    
    # Ajustamos el escalador estrictamente con el pasado (Train)
    train_delitos_crudos = train_data[:, :, 0].reshape(-1, 1)
    scaler_x.fit(train_delitos_crudos)
    scaler_y.fit(train_delitos_crudos)
    
    # Aplicamos la transformación a Train y Test en su característica 0
    train_data[:, :, 0] = scaler_x.transform(train_data[:, :, 0].reshape(-1, 1)).reshape(train_data[:, :, 0].shape)
    test_data[:, :, 0] = scaler_x.transform(test_data[:, :, 0].reshape(-1, 1)).reshape(test_data[:, :, 0].shape)
    
    # 5. Conversión a Tensores PyTorch
    train_tensor = torch.tensor(train_data, dtype=torch.float32)
    test_tensor = torch.tensor(test_data, dtype=torch.float32)
    
    # 6. Instanciamos los Datasets (Memoria protegida)
    train_dataset = CrimeSpatiotemporalDataset(train_tensor, ventana_dias)
    test_dataset = CrimeSpatiotemporalDataset(test_tensor, ventana_dias)
    
    # 7. Creamos los DataLoaders (Generadores de Mini-Lotes automáticos)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    print(f"DataLoaders listos. Lotes de entrenamiento: {len(train_loader)}")
    
    return train_loader, test_loader, scaler_y