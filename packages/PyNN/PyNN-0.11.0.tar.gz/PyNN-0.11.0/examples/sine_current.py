"""


"""

import pyNN.nest
import pyNN.neuron
import pyNN.brian2
from pyNN.utility.plotting import Figure, Panel

sims = [pyNN.nest, pyNN.neuron, pyNN.brian2]

sim_dt = 0.1

start1 = 10.0
freq1 = 100.0
phase1 = 0.0

start2 = 5.0
freq2 = 50.0
phase2 = 90.0

amplitude = 1.0

results = {}

for sim in sims:
    sim.setup(min_delay=1.0, timestep=sim_dt)

    cells = sim.Population(2, sim.IF_curr_exp(v_thresh=-55.0, tau_refrac=5.0))

    acsource1 = sim.ACSource(start=start1, stop=20.0, amplitude=amplitude, offset=0.0,
                             frequency=freq1, phase=phase1)
    cells[0].inject(acsource1)
    acsource1.record()
    acsource2 = sim.ACSource(start=start2, stop=20.0, amplitude=amplitude, offset=0.0,
                             frequency=freq2, phase=phase2)
    cells[1].inject(acsource2)
    acsource2.record()

    #acsource1.start = 10.0
    #acsource2.frequency = 20.0

    cells.record('v')
    sim.run(25.0)
    vm = cells.get_data().segments[0].filter(name="v")[0]
    sim.end()
    i_ac1 = acsource1.get_data()
    i_ac2 = acsource2.get_data()

    results[sim.__name__] = {
        "vm": vm,
        "i_ac1": i_ac1,
        "i_ac2": i_ac2
    }

Figure(
    Panel(
        results["pyNN.nest"]["vm"],
        results["pyNN.neuron"]["vm"],
        results["pyNN.brian2"]["vm"],
        data_labels=("NEST", "NEURON", "Brian"),
        line_properties=({"lw": 5}, {"lw": 3}, {"lw": 1}),
        ylabel="v (mV)", yticks=True
    ),
    Panel(
        results["pyNN.nest"]["i_ac1"],
        results["pyNN.neuron"]["i_ac1"],
        results["pyNN.brian2"]["i_ac1"],
        data_labels=("NEST", "NEURON", "Brian"),
        line_properties=({"lw": 5}, {"lw": 3}, {"lw": 1}),
        ylabel="i_ac1 (nA)", yticks=True
    ),
    Panel(
        results["pyNN.nest"]["i_ac2"],
        results["pyNN.neuron"]["i_ac2"],
        results["pyNN.brian2"]["i_ac2"],
        data_labels=("NEST", "NEURON", "Brian"),
        line_properties=({"lw": 5}, {"lw": 3}, {"lw": 1}),
        ylabel="i_ac2 (nA)",
        xlabel="Time (ms)",
        xticks=True, yticks=True
    ),
).save("sine_current.png")
