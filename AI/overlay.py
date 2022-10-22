from pynq import Overlay

# Handle the preprocessing and passing of data into the FPGA
def main():
    
    # Program the FPGA with the bitstream
    ol = Overlay('design_1_wrapper.bit')

if __name__ == "__main__":
    main()