import nest
import nest.voltage_trace
import matplotlib.pyplot as plt

nest.set_verbosity("M_WARNING")
nest.ResetKernel()

neuron = nest.Create("iaf_psc_alpha")
voltmeter = nest.Create("voltmeter")

neuron.I_e = 376.0

nest.Connect(voltmeter, neuron)

nest.Simulate(200.0)

nest.voltage_trace.from_device(voltmeter)
plt.show()

neuron.I_e = 450.0
nest.Simulate(1000.0)

nest.voltage_trace.from_device(voltmeter)
plt.show()
