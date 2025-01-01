import psychrolib
import logging
import sys
from typing import Tuple


# Set up logging configuration
def setup_logger(debug: bool = False) -> logging.Logger:
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler(sys.stdout)

    if debug:
        logger.setLevel(logging.DEBUG)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        logger.setLevel(logging.INFO)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def calculate_cfm_from_room(volume_ft3: float, ach: float) -> float:
    """Calculate CFM from room volume and air changes per hour"""
    return (volume_ft3 * ach) / 60  # Convert from per hour to per minute


def calculate_cooling_load(
        flow_cfm: float,
        t1: float,
        rh1: float,
        t2: float,
        rh2: float,
        logger: logging.Logger
) -> int:
    """Calculate cooling load with detailed logging"""
    # Initialize psychrolib for SI units
    psychrolib.SetUnitSystem(psychrolib.SI)

    # Convert CFM to m³/s
    flow_m3s = flow_cfm * 0.000471947
    logger.debug(f"Volumetric flow rate: {flow_m3s:.6f} m³/s")

    # Get air density (kg/m³)
    w1 = psychrolib.GetHumRatioFromRelHum(t1, rh1, 101325)
    density = psychrolib.GetMoistAirDensity(t1, w1, 101325)
    logger.debug(f"Air density: {density:.2f} kg/m³")

    # Calculate mass flow rate (kg/s)
    mass_flow = flow_m3s * density
    logger.debug(f"Mass flow rate: {mass_flow:.4f} kg/s")

    # Get initial and final enthalpies
    h1 = psychrolib.GetMoistAirEnthalpy(t1, w1)
    w2 = psychrolib.GetHumRatioFromRelHum(t2, rh2, 101325)
    h2 = psychrolib.GetMoistAirEnthalpy(t2, w2)
    logger.debug(f"Initial enthalpy: {h1:.2f} J/kg")
    logger.debug(f"Final enthalpy: {h2:.2f} J/kg")
    logger.debug(f"Enthalpy difference: {h1 - h2:.2f} J/kg")

    # Calculate total cooling load (kW)
    cooling_load_kw = mass_flow * (h1 - h2) / 1000  # Convert J/s to kW
    logger.debug(f"Cooling load: {cooling_load_kw:.2f} kW")

    # Convert to BTU/hr (1 kW = 3412.142 BTU/hr)
    cooling_load_btu = cooling_load_kw * 3412.142

    water_removal_kg_s = mass_flow * (w1 - w2)  # kg water/s
    water_removal_kg_hr = water_removal_kg_s * 3600  # Convert to kg/hr
    logger.debug(f"Water removal rate: {water_removal_kg_hr:.2f} kg/hr")

    return round(cooling_load_btu)


def get_user_input(logger: logging.Logger) -> Tuple[float, float, float, float, float, float, float]:
    """Get user inputs with default values"""
    logger.info("\nEnter room dimensions and air changes per hour:")
    length = float(input("Room length (feet) [20]: ") or 20)
    width = float(input("Room width (feet) [15]: ") or 15)
    logger.info(f"\nRoom area = {length*width} sqft")
    height = float(input("Room height (feet) [8]: ") or 8)
    ach = float(input("Air changes per hour [4]: ") or 4)

    volume = length * width * height
    cfm = calculate_cfm_from_room(volume, ach)

    logger.info("\nEnter temperature and humidity parameters:")
    t1 = float(input("Initial temperature (°C) [43]: ") or 43)
    rh1 = float(input("Initial relative humidity (0-1) [0.85]: ") or 0.85)
    t2 = float(input("Target temperature (°C) [25]: ") or 25)
    rh2 = float(input("Target relative humidity (0-1) [0.55]: ") or 0.55)

    return cfm, t1, rh1, t2, rh2, volume, ach


def main():
    # Initialize logger
    DEBUG_MODE = True  #Set to False to disable debugging
    logger = setup_logger(DEBUG_MODE)

    try:
        # Get user inputs
        cfm, t1, rh1, t2, rh2, volume, ach = get_user_input(logger)

        # Print room and airflow information
        logger.info(f"\nRoom volume: {volume:,.0f} ft³")
        logger.info(f"Air changes per hour: {ach}")
        logger.info(f"Required CFM: {cfm:.1f}")

        # Calculate cooling load
        load = calculate_cooling_load(
            flow_cfm=cfm,
            t1=t1,
            rh1=rh1,
            t2=t2,
            rh2=rh2,
            logger=logger
        )

        logger.info(f"\nTotal Cooling Load: {load:,} BTU/hr")
        logger.info(f"Cooling Tons: {load / 12000:.1f} tons")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
