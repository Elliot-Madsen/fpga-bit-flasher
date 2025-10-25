# fpga-bit-flasher

This Python utility allows you to program `.bit` files onto FPGA boards through a simple command-line interface.  
It is compatible with both **Vivado Lab** and **openFPGALoader**, making it suitable for quick flashing, testing, or automated workflows.

To use this tool:

1. Create a folder named `bit_file` in the project root, and place your `.bit` file inside it.  
2. Create a file named `prog_config.txt` in the same directory and specify your FPGA device, for example:

Make sure the device name exactly matches your FPGA part number, otherwise programming may fail.  
3. Run the following command in your terminal:

The script will automatically:
- Read your `prog_config.txt` configuration  
- Find the `.bit` file inside `./bit_file/`  
- Flash it to the connected FPGA device `python run_prog.py`  
