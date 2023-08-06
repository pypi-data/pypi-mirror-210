import sys
sys.path.append('..')
import hiperwalk

N = 101
cycle = hiperwalk.Cycle(N)
ctqw = hiperwalk.ContinuousWalk(graph=cycle, gamma=0.35)
psi_0 = ctqw.ket(50)
psi_f = ctqw.simulate(time = 50, initial_condition = psi_0)
prob = ctqw.probability_distribution(psi_f)
hiperwalk.plot_probability_distribution(prob)
