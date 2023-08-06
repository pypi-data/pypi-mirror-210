import pyNN.nest as sim

sim.setup(timestep=0.2, spike_precision="on_grid")

p_in = sim.Population(1, sim.SpikeSourceArray(spike_times=[3.]))
p_out= sim.Population(1, sim.IF_curr_exp())

con = sim.AllToAllConnector()
syn1 = sim.StaticSynapse(delay=2., weight=7.)
syn2 = sim.StaticSynapse(delay=1., weight=7.)

print("MinDelay before Projection:   ", sim.get_min_delay())
prj = sim.Projection(p_in, p_out, con, syn1)
print("MinDelay after Projection 1:  ", sim.get_min_delay())

p_in2 = sim.Population(1, sim.SpikeSourceArray(spike_times=[3.]))
prj2 = sim.Projection(p_in2, p_out, con, syn2)
print("MinDelay after Projection 2:  ", sim.get_min_delay())

p_in.record('spikes')
p_in2.record('spikes')

# Note: In run() the SourceNeurons of the SpikeSourceArray
# are connected to the ParrotNeurons of the SpikeSourceArray
# using the current min_delay as a synapse delay.
sim.run(20)

data_in = p_in.get_data()
data_in2 = p_in2.get_data()

print("In-Spikes at (should be 3.):  ", data_in.segments[0].spiketrains[0].as_array().tolist())
print("In2-Spikes at (should be 3.): ", data_in2.segments[0].spiketrains[0].as_array().tolist())
print("MinDelay: ", sim.get_min_delay())
print("MaxDelay: ", sim.get_max_delay())