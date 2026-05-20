import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv

class RedEspacioTemporal(nn.Module):
    def __init__(self, num_features, unidades_ocultas):
        super(RedEspacioTemporal, self).__init__()
        self.capa_espacial = GCNConv(num_features, unidades_ocultas)
        self.capa_temporal = nn.GRU(input_size=unidades_ocultas, hidden_size=unidades_ocultas, batch_first=True)
        self.capa_salida = nn.Linear(unidades_ocultas, 1)

    def forward(self, x_ventana, edge_index, edge_weights):
        batch_size, num_dias, num_nodos, num_features = x_ventana.shape
        salidas_espaciales = []

        # Procesamos día por día (Lóbulo Espacial)
        for t in range(num_dias):
            x_dia = x_ventana[:, t, :, :] # [Batch, Nodos, Features]
            mapas_batch = []

            # Procesamos muestra por muestra en el lote para proteger la VRAM
            for b in range(batch_size):
                out = self.capa_espacial(x_dia[b], edge_index, edge_weights)
                out = F.relu(out)
                mapas_batch.append(out)

            mapa_procesado = torch.stack(mapas_batch)
            salidas_espaciales.append(mapa_procesado)

        # Lóbulo Temporal (GRU)
        x_secuencia = torch.stack(salidas_espaciales, dim=2)
        x_secuencia = x_secuencia.reshape(batch_size * num_nodos, num_dias, -1)

        _, memoria_final = self.capa_temporal(x_secuencia)
        memoria_final = memoria_final.squeeze(0)

        # Predicción Final
        prediccion = self.capa_salida(memoria_final)
        return prediccion.reshape(batch_size, num_nodos)