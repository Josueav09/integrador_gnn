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
        self.softplus = nn.Softplus()

    def forward(self, x_ventana, edge_index, edge_weights):
        batch_size, num_dias, num_nodos, num_features = x_ventana.shape
        salidas_espaciales = []

        # Vectorización Espacial: Empaquetar el lote en un único grafo disjunto gigante
        # Precalculamos el edge_index desplazado para el batch completo
        offsets = torch.arange(0, batch_size * num_nodos, num_nodos, device=x_ventana.device).view(-1, 1, 1)
        edge_index_batched = edge_index.unsqueeze(0) + offsets  # [Batch, 2, E]
        edge_index_batched = edge_index_batched.transpose(0, 1).reshape(2, -1) # [2, Batch * E]
        
        edge_weights_batched = edge_weights.repeat(batch_size) if edge_weights is not None else None

        # Procesamos día por día (Lóbulo Espacial) de forma paralela para todo el batch
        for t in range(num_dias):
            x_dia = x_ventana[:, t, :, :] # [Batch, Nodos, Features]
            x_dia_batched = x_dia.reshape(batch_size * num_nodos, num_features) # [Batch * Nodos, Features]
            
            # Inferencia paralela en la GNN (Vectorización sobre la dimensión batch espacial)
            out_batched = self.capa_espacial(x_dia_batched, edge_index_batched, edge_weights_batched)
            out_batched = F.relu(out_batched)
            
            # Volvemos a desagregar el batch
            mapa_procesado = out_batched.reshape(batch_size, num_nodos, -1)
            salidas_espaciales.append(mapa_procesado)

        # Lóbulo Temporal (GRU - Secuencial Iterativo)
        x_secuencia = torch.stack(salidas_espaciales, dim=2)
        x_secuencia = x_secuencia.reshape(batch_size * num_nodos, num_dias, -1)

        _, memoria_final = self.capa_temporal(x_secuencia)
        memoria_final = memoria_final.squeeze(0)

        # Predicción Final con Softplus (Garantía Matemática >= 0 y mitiga ReLU muerta)
        prediccion = self.capa_salida(memoria_final)
        prediccion = self.softplus(prediccion)
        return prediccion.reshape(batch_size, num_nodos)