import sys
sys.path.append('..')
import qwalk.coined as qw
import qwplot
import numpy as np
import networkx as nx
from time import time

n = 19
print(2**(n/2))
print('generating adjacency_matrix')
start = time()
A = nx.adjacency_matrix(nx.generators.hypercube_graph(n))
print(time() - start)

print('generating hypercube')
start = time()
cqw = qw.Graph(A)
print(time() - start)

a = 1/np.sqrt(n)
#psi0 = cqw.state([[a,(0,i)] for i in range(n)])
#psi0 = cqw.state([[a,i,0] for i in range(n)])
print('generating initial condition')
start = time()
psi0 = cqw.uniform_state()
print(time() - start)

print('generating evolution operator')
start = time()
U = cqw.evolution_operator(marked_vertices=[0], oracle_type='phase_flip', hpc=False)
print(time() - start)

print('simulating')
start = time()
state = cqw.simulate(time_range=2**(n//2), evolution_operator=U, initial_condition=psi0,  hpc=False)
print(time() - start)

print('calculating probabilities')
start = time()
prob = cqw.probability_distribution(state)
print(time() - start)

print('plotting probabilities')
start = time()
qwplot.probability_distribution(prob, plot_type='line', marker=None)
print(time() - start)
