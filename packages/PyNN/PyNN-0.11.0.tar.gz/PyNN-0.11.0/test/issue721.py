import pyNN.nest as sim

sim.setup()

p1 = sim.Population(1000, sim.IF_cond_exp())
p2 = sim.Population(1000, sim.IF_cond_exp())


assembly = sim.Assembly(p1, p2)
conn = sim.FixedProbabilityConnector(0.01)
syn = sim.StaticSynapse(weight=0.01, delay=0.5)
sim.Projection(assembly, assembly, connector=conn, synapse_type=syn, receptor_type="excitatory")
