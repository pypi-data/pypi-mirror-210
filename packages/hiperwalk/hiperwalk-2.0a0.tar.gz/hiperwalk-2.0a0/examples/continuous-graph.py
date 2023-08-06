import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import sys
sys.path.append('..')
import qwalk.continuous as ctqw
import plot as hplot

# create random graph and obtain its adjacency matrix
num_vert = 20
G = nx.ladder_graph(num_vert)
adj = nx.adjacency_matrix(G)
del G

# Quantum Walk preparation and simulation
random = ctqw.Graph(adj)
random.hamiltonian(0.5)
psi0 = np.zeros(random.hilb_dim)
psi0[0] = 1
states = random.simulate((1, 0.1), psi0, hpc=False)
print(states)
print(states is not None)

# Calculating probabilities and plotting
prob = random.probability_distribution(states)
hplot.plot_probability_distribution(prob)
#hplot.plot_probability_distribution(
#    prob, plot_type='graph', animate=True, adj_matrix=adj, interval=1000,
#    cmap='default', fixed_probabilities=False
#)
