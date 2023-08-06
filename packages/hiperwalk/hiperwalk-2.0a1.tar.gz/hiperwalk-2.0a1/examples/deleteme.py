import numpy as np
from scipy.linalg import expm
import networkx as nx

num_vert = 201
A = nx.adjacency_matrix(nx.cycle_graph(num_vert)).todense()

def taylor(A, t, n):
    M = np.eye(A.shape[0], dtype=np.complex128)
    curr_term = np.eye(A.shape[0], dtype=np.complex128)
    for i in range(1, n+1):
        curr_term = 1/i * (curr_term @ A)
        M += curr_term
        print('-----------')
        print(i)
        print(curr_term)
        print()
        print(M)

    M2 = np.copy(M)
    for i in range(t - 1):
        M2 = M2 @ M

    return M2

t = 100
A = (-1j*A).astype(np.complex128)
print(A)
A_expm = expm(t*A)
A_taylor = taylor(A, t, 20)
print('---------------------------------------------')
print(A_expm)
print('---------------------------------------------')
print(A_taylor)
print('---------------------------------------------')
print(np.allclose(A_expm, A_taylor))
print(np.max(np.absolute(A_expm - A_taylor)))
