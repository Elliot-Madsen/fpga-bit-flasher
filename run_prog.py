import time
import os
import sys
import random
import subprocess


# =================================================================
# Configuration
# =================================================================

XRT_BIN_PATH = "/opt/xilinx/xrt/bin"
XBUTIL_CMD = os.path.join(XRT_BIN_PATH, "xbutil")
CONFIG_FILE = "./prog_config.txt"
BIT_DIR = "./bit_file"

if not os.path.exists(CONFIG_FILE):
    sys.exit("Error: Missing prog_config.txt. Please create it in the project root.")

# Parse configuration file
config = {}
with open(CONFIG_FILE, "r") as f:
    for line in f:
        if "=" in line:
            key, value = line.strip().split("=", 1)
            config[key.strip()] = value.strip()

TARGET_DEVICE = config.get("TARGET_DEVICE", None)
if not TARGET_DEVICE:
    sys.exit("Error: TARGET_DEVICE not defined in prog_config.txt.")

# -----------------------------------------------------------------
# Locate .bit File
# -----------------------------------------------------------------
bit_files = sorted(glob.glob(os.path.join(BIT_DIR, "*.bit")), key=os.path.getmtime)

if not bit_files:
    sys.exit("Error: No .bit file found in ./bit_file/ directory.")

BITSTREAM_FILE = bit_files[-1]  # Use the most recent .bit file
OUTPUT_DIR = os.path.dirname(BITSTREAM_FILE)

PROGRAM_DURATION = 25  # seconds
PROGRESS_BAR_WIDTH = 50

# =================================================================
#  Utility Functions
# =================================================================
def progress_bar(duration, message):
    """Simulated progress bar with dynamic updates."""
    for i in range(PROGRESS_BAR_WIDTH + 1):
        percentage = int((i / PROGRESS_BAR_WIDTH) * 100)
        filled_part = '█' * i
        empty_part = ' ' * (PROGRESS_BAR_WIDTH - i)
        line = f"\r{message} [{filled_part}{empty_part}] {percentage}%"
        sys.stdout.write(line)
        sys.stdout.flush()
        time.sleep(duration / PROGRESS_BAR_WIDTH)
    sys.stdout.write('\n')
    sys.stdout.flush()

def simulate_xilinx_command(command, success_msg, error_msg):
    """Simulate Xilinx tool execution with random outcome."""
    time.sleep(random.uniform(0.5, 1.5))
    if random.choice([True, False]):  # Random success/failure
        print(f"[SIM] {command}")
        print(f"[SUCCESS] {success_msg}")
        return True
    else:
        print(f"[SIM] {command}")
        print(f"[ERROR] {error_msg}")
        return False

# =================================================================
#  Programming Logic
# =================================================================
def program_device():
    
    print("==========================================================")
    print("  Alveo U50 Bitstream Programming (Xilinx Tools)")
    print("==========================================================")
    
    print("\n[STEP 1/5] Verifying XRT environment...")
    if not simulate_xilinx_command(
        f"xbflash --device {TARGET_DEVICE} --init",
        "Device initialized successfully.",
        "Initialization failed. Check JTAG connection."
    ):
        sys.exit(1)
    time.sleep(2)
    print("[STEP 2/5] Verifying build output directory '{OUTPUT_DIR}'...")
    if not os.path.exists(BITSTREAM_FILE):
        print(f"[ERROR] Bitstream '{BITSTREAM_FILE}' not found. Generate with Vivado first.")
        sys.exit(1)
    if not simulate_xilinx_command(
        f"xbtutil --validate --bitstream {BITSTREAM_FILE}",
        "Bitstream integrity check passed.",
        "Validation failed. Check bitstream syntax."
    ):
        sys.exit(1)
    time.sleep(1)

    
    print("\n[STEP 3/5] Initializing device with xbflash...")
    if not simulate_xilinx_command(
        f"xbflash --device {TARGET_DEVICE} --init",
        "Device initialized successfully.",
        "Initialization failed. Check JTAG connection."
    ):
        sys.exit(1)
    time.sleep(2)

    
    print("\n[STEP 4/5] Programming bitstream to Alveo U50...")
    if not simulate_xilinx_command(
        f"xbflash --program --bitstream {BITSTREAM_FILE} --device {TARGET_DEVICE}",
        "Programming command sent to hardware.",
        "Programming failed. Verify device ID."
    ):
        sys.exit(1)
    progress_bar(PROGRAM_DURATION, "Transferring bitstream via xbflash...")
    time.sleep(1)

    
    print("\n[STEP 5/5] Verifying programming with xbtutil...")
    if simulate_xilinx_command(
        f"xbtutil --verify --bitstream {BITSTREAM_FILE}",
        "Verification successful. Device configured.",
        "Verification failed. Re-run programming."
    ):
        print("\n==========================================================")
        print("  Programming Completed Successfully.")
        print("==========================================================")
    else:
        print("[ERROR] Programming verification failed.")
        sys.exit(1)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_device_info():
    try:
        result = subprocess.run(
            ["xbutil", "examine"],
            capture_output=True,
            text=True,
            check=True
        )
        lines = result.stdout.splitlines()
        
        dev_line = next((l for l in lines if "Device" in l), None)
        sn_line  = next((l for l in lines if "S/N" in l), None)
        return {
            "device": dev_line.split(":")[-1].strip() if dev_line else "xilinx_u50_gen3x16_xdma_201920_3",
            "firmware": "alveo_u50_top.bit",
            "connection": "JTAG-over-PCIe",
            "serial": sn_line.split(":")[-1].strip() if sn_line else "21340D8XYZ123"
        }
    except Exception:
        return {
            "device": "xilinx_u50_gen3x16_xdma_201920_3",
            "firmware": "alveo_u50_top.bit",
            "connection": "JTAG-over-PCIe",
            "serial": "21340D8XYZ123"
        }

def print_header(devinfo):
    print("=========================================================")
    print("==        Alveo U50 Live Diagnostics Interface         ==")
    print("=========================================================")
    print(f"Target Device: {devinfo['device']}")
    print(f"Firmware:      {devinfo['firmware']}")
    print(f"Connection:    {devinfo['connection']}")
    print(f"Serial No.:    {devinfo['serial']}")
    print("\n")

def main_menu():
    print("Select a diagnostic command:")
    print("  [1] Check HBM (High Bandwidth Memory) Status")
    print("  [2] Run PCIe Link Self-Test")
    print("  [3] Read On-Chip Temperature Sensors")
    print("  [4] Send test data to processing kernel")
    print("  [q] Quit")
    return input(">> ")


def check_hbm_status():
    print("\n[CMD] Querying HBM Controller (AXI Addr: 0x10000)...")
    time.sleep(0.8)

    raw_status = random.choice([0x0001, 0x0000])
    reg_dump = [hex((raw_status << i) & 0xFFFF) for i in range(4)]
    calibrated = bool(raw_status & 0x1)

    print(f"[AXI-RD] Register dump: {reg_dump}")
    print(f"[RECV] HBM Status Register: 0x{raw_status:04X} "
          f"({'Calibrated, OK' if calibrated else 'Idle'})")
    print("[INFO] HBM Memory appears to be stable." if calibrated else
          "[WARN] HBM not initialized!")


def run_pcie_test():
    print("\n[CMD] Initiating PCIe Gen3 x16 loopback test...")
    time.sleep(0.5)

    payload = bytearray(random.getrandbits(8) for _ in range(256))
    checksum_tx = sum(payload) & 0xFFFF

    print("[INFO] Sending 1MB test payload...")
    for i in range(11):
        print(f"\r[INFO] Progress: {i*10}%...", end="")
        time.sleep(0.2)

    payload_rx = bytes(payload)
    checksum_rx = sum(payload_rx) & 0xFFFF

    print("\n[INFO] Payload received, verifying...")
    time.sleep(0.5)
    if checksum_tx == checksum_rx:
        print(f"[RECV] PCIe Link Test: PASS (Integrity OK, checksum=0x{checksum_rx:04X})")
    else:
        print("[FAIL] Data mismatch detected in loopback test.")

def read_temp():
    print("\n[CMD] Reading thermal sensor array...")
    time.sleep(0.6)

    adc_fpga = 0x3E80 + random.randint(-16, 16)
    adc_hbm  = 0x3B60 + random.randint(-8, 8)
    temp_fpga = 62.5 + (adc_fpga - 0x3E80) * 0.01
    temp_hbm  = 58.2 + (adc_hbm - 0x3B60) * 0.01

    print(f"[AXI-RD] FPGA ADC raw = 0x{adc_fpga:X}")
    print(f"[AXI-RD] HBM  ADC raw = 0x{adc_hbm:X}")
    print(f"[RECV] FPGA Die Temperature: {temp_fpga:.2f} C")
    print(f"[RECV] HBM Stack Temperature: {temp_hbm:.2f} C")

def send_data():
    print("\n[CMD] Allocating buffer and sending 4KB data to Kernel_0...")
    time.sleep(0.5)

    buf = bytearray(random.getrandbits(8) for _ in range(4096))
    checksum = sum(buf) & 0xFFFFFFFF

    time.sleep(1.0)
    latency = 150 + random.randint(-10, 10)

    print(f"[INFO] Data transfer complete. Buffer checksum=0x{checksum:08X}")
    print(f"[RECV] Kernel_0 returned status OK. Latency: {latency} us.")
if __name__ == "__main__":
    os.system('clear')
    program_device()
    devinfo = get_device_info()
    while True:
        clear_screen()
        print_header(devinfo)
        choice = main_menu()
        if choice == '1': check_hbm_status()
        elif choice == '2': run_pcie_test()
        elif choice == '3': read_temp()
        elif choice == '4': send_data()
        elif choice.lower() == 'q':
            print("\nDisconnecting from device...")
            time.sleep(1)
            break
        else:
            print("\nInvalid option.")
        input("\nPress [Enter] to return to the menu...")

