import pyNN.nest as sim

sim.setup()

parameters = {}

neuron = sim.Population(1, sim.IF_curr_alpha(**parameters), initial_values={"v": -70})
noise = sim.Population(2, sim.SpikeSourcePoisson(rate=[80000, 15000]))

neuron.record("v")


weight = [[0.0012], [0.001]]  # nA
delay = 1.0

connections = sim.Projection(
    noise, neuron,
    sim.AllToAllConnector(),
    sim.StaticSynapse(weight=weight, delay=delay))

sim.run(1000.0)
