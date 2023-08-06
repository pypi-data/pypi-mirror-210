import sys
sys.path.append('..')
import numpy as np
import networkx as nx
import qwalk.coined as qw
import qwplot

n = 10
A = nx.adjacency_matrix(nx.generators.hypercube_graph(n))

cqw = qw.Graph(A)

a = 1/np.sqrt(n)
print(a)
print(1/np.sqrt(2**n))
print((1/np.sqrt(2**n))**2)

psi0 = cqw.uniform_state()
U = cqw.evolution_operator(marked_vertices=0, oracle_type='phase_flip',
                           hpc=False)
print(U.todense())

states = cqw.simulate(time_range=(20, 1), evolution_operator=U,
                      initial_condition=psi0, hpc=True)

probs = cqw.probability_distribution(states)
print(probs)
qwplot.probability_distribution(probs, plot_type='line', animate=True)
