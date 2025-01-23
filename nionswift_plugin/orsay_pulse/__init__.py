from . import orsay_pulse_handler
from . import orsay_pulse_tools
from nion.utils import Registry

def run():
    pulse_instrument = orsay_pulse_tools.PulseTools()
    Registry.register_component(pulse_instrument, {"pulse_controller"})
    orsay_pulse_handler.run(pulse_instrument)