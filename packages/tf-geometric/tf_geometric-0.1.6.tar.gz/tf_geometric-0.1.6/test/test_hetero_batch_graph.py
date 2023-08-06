# coding=utf-8

import tf_geometric as tfg
import numpy as np


graph0 = tfg.HeteroGraph(
    x_dict={
        "paper": np.random.randn(2, 5),
        "author": np.random.randn(4, 5)
    },
    edge_index_dict={
        ("paper", "r.write", "author"): np.array([
            [0, 0, 1, 1],
            [0, 2, 1, 3]
        ])
    },
    y_dict={
        "paper": np.array([0, 1])
    }
)



graph1 = tfg.HeteroGraph(
    x_dict={
        "paper": np.random.randn(3, 5),
        "author": np.random.randn(5, 5)
    },
    edge_index_dict={
        ("paper", "r.write", "author"): np.array([
            [0, 1, 1, 1, 2, 2],
            [0, 0, 1, 2, 3, 4]
        ])
    },
    y_dict={
        "paper": np.array([1, 1, 0])
    }
)

print(graph0)
print(graph1)

batch_graph = tfg.HeteroBatchGraph.from_graphs([graph0, graph1])

print(batch_graph)
print(batch_graph.edge_index_dict)
print(batch_graph.node_graph_index_dict)
print(batch_graph.edge_graph_index_dict)

batch_graph = batch_graph.convert_data_to_tensor()
print(batch_graph.edge_index_dict)

print(batch_graph.y_dict)

batch_graph.graphs = None

print(batch_graph.num_graphs)