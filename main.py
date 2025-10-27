import pyvisa
import time
import numpy as np
import csv

# Replace with the actual VISA resource string for your SPD3303X
# This could be a LAN address (e.g., "TCPIP::192.168.1.100::INSTR"),
# or a USB address (e.g., "USB0::0x10AB::0x09C4::DP8C00000::INSTR")
VISA_ADDRESS = "USB0::0xF4EC::0x1430::SPD3XJFC8R0464::INSTR"
ID_CURRENT_MAX = 2


def setCH1(voltage, current):
    inst.write(f"CH1:VOLT {float(voltage):.3f}")
    inst.write(f"CH1:CURR {float(current):.3f}")


def setCH2(voltage, current):
    inst.write(f"CH2:VOLT {float(voltage):.3f}")
    inst.write(f"CH2:CURR {float(current):.3f}")


def readCH1():
    measured_voltage = inst.query("MEAS:VOLT? CH1")
    measured_current = inst.query("MEAS:CURR? CH1")
    return (float(measured_voltage), float(measured_current))


def readCH2():
    measured_voltage = inst.query("MEAS:VOLT? CH2")
    measured_current = inst.query("MEAS:CURR? CH2")
    return (float(measured_voltage), float(measured_current))


def CH1Off():
    inst.write("OUTP CH1,OFF")


def CH2Off():
    inst.write("OUTP CH2,OFF")


def CH1On():
    inst.write("OUTP CH1,ON")


def CH2On():
    inst.write("OUTP CH2,ON")


def wait():
    time.sleep(1.2)


def readAll():
    CH1_volts, CH1_amps = readCH1()
    CH2_volts, CH2_amps = readCH2()
    return (CH1_volts, CH1_amps, CH2_volts, CH2_amps)


def IdvsVgs(Vds: float, Vgs_start: float, Vgs_step_size: float, Vgs_stop: float):
    CH1Off()
    CH2Off()
    setCH2(Vds, ID_CURRENT_MAX)  # Vds on channel 2
    setCH1(Vgs_start, 0.1)  # Vgs channel 1
    data = [("Vgs", "Igs", "Vds", "Ids")]
    CH1On()
    CH2On()
    wait()
    wait()
    wait()
    for Vgs_voltage in np.arange(Vgs_start, Vgs_stop, Vgs_step_size):
        setCH1(Vgs_voltage, 0.1)
        wait()
        data.append(readAll())

    print(data)
    CH1Off()
    CH2Off()
    setCH1(0, 0)
    setCH2(0, 0)
    return data


def IdvsVds(
    Vgs_list: list[float], Vds_start: float, Vds_step_size: float, Vds_stop: float
):
    CH1Off()
    CH2Off()
    setCH2(Vds_start, ID_CURRENT_MAX)  # Vds on channel 2
    setCH1(Vgs_list[0], 0.1)  # Vgs channel 1
    data = [("Vgs", "Igs", "Vds", "Ids")]
    CH1On()
    CH2On()
    wait()
    wait()
    wait()
    for Vgs_voltage in Vgs_list:
        setCH1(Vgs_voltage, 0.1)
        for Vds_voltage in np.arange(Vds_start, Vds_stop, Vds_step_size):
            setCH2(Vds_voltage, ID_CURRENT_MAX)
            wait()
            data.append(readAll())

    print(data)
    CH1Off()
    CH2Off()
    setCH1(0, 0)
    setCH2(0, 0)
    return data


def writeData(data, name):
    timestamp = f"{time.time():.0f}"
    with open(f"results/{name}_{timestamp}.csv", "w", newline="") as fp:
        writer = csv.writer(fp, delimiter=",")
        writer.writerows(data)


try:
    # Open the resource manager
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    # Open a connection to the instrument
    # Ensure write_termination and read_termination are set correctly for your device
    # Siglent devices often use '\n' for termination.
    inst = rm.open_resource(VISA_ADDRESS, write_termination="\n", read_termination="\n")

    # Query the instrument identification
    idn = inst.query("*IDN?")
    print(f"Connected to: {idn.strip()}")

    data = IdvsVgs(5, 0, 0.1, 3)
    writeData(data, "test_IdvsVgs")

    data = IdvsVds([1.0, 1.5, 2.0, 2.5, 3.0, 3.5], 0, 0.1, 4)

    writeData(data, "test_IdvsVds")


except pyvisa.errors.VisaIOError as e:
    print(f"VISA Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    if "inst" in locals() and inst:
        inst.close()
        print("Connection closed.")
    if "rm" in locals() and rm:
        rm.close()
