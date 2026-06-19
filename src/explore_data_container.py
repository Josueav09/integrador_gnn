import pandas as pd
import numpy as np

processed_dir = "/app/data/processed"

print("--- tensor_panel_diario.parquet ---")
try:
    df_panel = pd.read_parquet(processed_dir + "/tensor_panel_diario.parquet")
    print("Shape:", df_panel.shape)
    print("Columns:", df_panel.columns.tolist())
    print("First 3 rows:\n", df_panel.head(3))
except Exception as e:
    print("Error panel:", e)

print("\n--- dataset_features_gnn.parquet ---")
try:
    df_feat = pd.read_parquet(processed_dir + "/dataset_features_gnn.parquet")
    print("Shape:", df_feat.shape)
    print("Columns:", df_feat.columns.tolist())
    print("First 3 rows:\n", df_feat.head(3))
except Exception as e:
    print("Error features:", e)

print("\n--- dataset_gnn_granular_final.parquet ---")
try:
    df_gran = pd.read_parquet(processed_dir + "/dataset_gnn_granular_final.parquet")
    print("Shape:", df_gran.shape)
    print("Columns:", df_gran.columns.tolist())
    print("First 3 rows:\n", df_gran.head(3))
    print("Unique id_nodo:", df_gran['id_nodo'].nunique() if 'id_nodo' in df_gran else 'N/A')
    print("Unique distrito:", df_gran['distrito'].unique().tolist() if 'distrito' in df_gran else 'N/A')
except Exception as e:
    print("Error granular:", e)
