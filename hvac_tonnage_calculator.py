import psychrolib


def calculate_cfm_from_room(volume_ft3, ach):
    """Calculate CFM from room volume and air changes per hour"""
    return (volume_ft3 * ach) / 60  # Convert from per hour to per minute


def calculate_cooling_load(flow_cfm, t1, rh1, t2, rh2):
    # Initialize psychrolib for SI units
    psychrolib.SetUnitSystem(psychrolib.SI)

    # Convert CFM to m³/s
    flow_m3s = flow_cfm * 0.000471947
    print(f"Volumetric flow rate: {flow_m3s:.6f} m³/s")

    # Get air density (kg/m³)
    w1 = psychrolib.GetHumRatioFromRelHum(t1, rh1, 101325)
    density = psychrolib.GetMoistAirDensity(t1, w1, 101325)
    print(f"Air density: {density:.2f} kg/m³")

    # Calculate mass flow rate (kg/s)
    mass_flow = flow_m3s * density
    print(f"Mass flow rate: {mass_flow:.4f} kg/s")

    # Get initial and final enthalpies
    h1 = psychrolib.GetMoistAirEnthalpy(t1, w1)
    w2 = psychrolib.GetHumRatioFromRelHum(t2, rh2, 101325)
    h2 = psychrolib.GetMoistAirEnthalpy(t2, w2)
    print(f"Initial enthalpy: {h1:.2f} J/kg")
    print(f"Final enthalpy: {h2:.2f} J/kg")
    print(f"Enthalpy difference: {h1 - h2:.2f} J/kg")

    # Calculate total cooling load (kW)
    cooling_load_kw = mass_flow * (h1 - h2) / 1000  # Convert J/s to kW
    print(f"Cooling load: {cooling_load_kw:.2f} kW")

    # Convert to BTU/hr (1 kW = 3412.142 BTU/hr)
    cooling_load_btu = cooling_load_kw * 3412.142

    return round(cooling_load_btu)


def get_user_input():
    """Get user inputs with default values"""
    print("\nEnter room dimensions and air changes per hour:")
    length = float(input("Room length (feet) [20]: ") or 20)
    width = float(input("Room width (feet) [15]: ") or 15)
    height = float(input("Room height (feet) [8]: ") or 8)
    ach = float(input("Air changes per hour [4]: ") or 4)

    volume = length * width * height
    cfm = calculate_cfm_from_room(volume, ach)

    print("\nEnter temperature and humidity parameters:")
    t1 = float(input("Initial temperature (°C) [43]: ") or 43)
    rh1 = float(input("Initial relative humidity (0-1) [0.85]: ") or 0.85)
    t2 = float(input("Target temperature (°C) [25]: ") or 25)
    rh2 = float(input("Target relative humidity (0-1) [0.55]: ") or 0.55)

    return cfm, t1, rh1, t2, rh2, volume, ach


if __name__ == "__main__":
    # Get user inputs
    cfm, t1, rh1, t2, rh2, volume, ach = get_user_input()

    # Print room and airflow information
    print(f"\nRoom volume: {volume:,.0f} ft³")
    print(f"Air changes per hour: {ach}")
    print(f"Required CFM: {cfm:.1f}")

    # Calculate cooling load
    load = calculate_cooling_load(
        flow_cfm=cfm,
        t1=t1,
        rh1=rh1,
        t2=t2,
        rh2=rh2
    )

    print(f"\nTotal Cooling Load: {load:,} BTU/hr")
    print(f"Cooling Tons: {load / 12000:.1f} tons")