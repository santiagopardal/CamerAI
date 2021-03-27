"""from System import System


sys = System()
sys.run_with_gui()
"""
from Detectors.CNNs import create_lite_model
create_lite_model().summary()