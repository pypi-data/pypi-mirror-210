import sys
sys.path.append('..')
import hiperwalk

dim = 11
lat = hiperwalk.Lattice((dim, dim), diagonal=True)
center = lat.get_central_vertex()
dtqw = hiperwalk.CoinedWalk(lat)
psi_0 = 0.5*(dtqw.ket(center,center + (1,1))
             - dtqw.ket(center,center + (1,-1))
             - dtqw.ket(center,center + (-1,1))
             + dtqw.ket(center,center + (-1,-1)))
psi_f = dtqw.simulate(time = (dim//2 - 1, 1), initial_condition = psi_0)
prob = dtqw.probability_distribution(psi_f)
hiperwalk.plot_probability_distribution(prob, graph=lat, animate=True)
