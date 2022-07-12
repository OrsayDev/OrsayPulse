from . import orsay_pulse_handler
from . import orsay_pulse_tools

def run():
    pulse_instrument = orsay_pulse_tools.PulseTools()
    orsay_pulse_handler.run(pulse_instrument)