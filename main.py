import pyvisa

# Replace with the actual VISA resource string for your SPD3303X
# This could be a LAN address (e.g., "TCPIP::192.168.1.100::INSTR"),
# or a USB address (e.g., "USB0::0x10AB::0x09C4::DP8C00000::INSTR")
VISA_ADDRESS = "TCPIP::192.168.1.100::INSTR"

try:
    # Open the resource manager
    rm = pyvisa.ResourceManager("@py")  # Use the PyVISA-py backend
    print(rm.list_resources)
    # Open a connection to the instrument
    # Ensure write_termination and read_termination are set correctly for your device
    # Siglent devices often use '\n' for termination.
    inst = rm.open_resource(VISA_ADDRESS, write_termination="\n", read_termination="\n")

    # Query the instrument identification
    idn = inst.query("*IDN?")
    print(f"Connected to: {idn.strip()}")

    # Set Channel 1 voltage to 5V and current limit to 1A
    inst.write("CH1:VOLT 5")
    inst.write("CH1:CURR 1")
    print("Channel 1 set to 5V, 1A limit.")

    # Enable Channel 1 output
    inst.write("OUTP CH1,ON")
    print("Channel 1 output ON.")

    # Measure and print the actual output voltage and current for Channel 1
    measured_voltage = inst.query("MEAS:VOLT? CH1")
    measured_current = inst.query("MEAS:CURR? CH1")
    print(
        f"Measured Channel 1: Voltage = {float(measured_voltage):.2f}V, Current = {float(measured_current):.2f}A"
    )

    # Disable Channel 1 output
    inst.write("OUTP CH1,OFF")
    print("Channel 1 output OFF.")

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
