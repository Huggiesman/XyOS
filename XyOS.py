import glob
import os
import sys
import struct
import serial
import time

# Print iterations progress
def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=80):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('%s |%s| %s%s %s\r' % (prefix, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def send_to_device(file, device_fd):
    # Control characters
    stx = b'S'
    cnt = b'C'
    etx = b'E'

    # Initial variables
    s = serial.Serial(device_fd, 115200)
    bytes_sent = 0
    total_bytes = os.stat(file).st_size
    kernel = open(file, "rb")

    # Initial output
    print(file, "->", device_fd)
    print_progress(bytes_sent,total_bytes)

    # Send STX
    s.write(stx)
    s.flush()

    while (True):
        # Data is sent in 8 byte chunks
        for i in range(8):
            data = kernel.read(1)

            # No more data left to send, send junk
            if not data:
                data = b'0'

            # Send byte of data
            s.write(data)
            s.flush()
            bytes_sent = bytes_sent + 1
            print_progress(bytes_sent,total_bytes)

        # Send ETX and quit
        if bytes_sent >= total_bytes:
            s.write(etx)
            s.flush()
            break

        # Send CNT
        s.write(cnt)
        s.flush()
    return True

def find_device():
    devices = glob.glob("/dev/cu.Repleo-PL2303-*")
    if len(devices) != 1:
        print("Invalid number of eligible devices")
        sys.exit(1)
    return devices[0]

def screen(device_fd):
    return os.system("screen " + device_fd + " 115200") == 0

def make_kernel():
    return os.system("cd ./Kernel && make") == 0

def make_bootloader():
    return os.system("cd ./Bootloader && make") == 0

def clean_bootloader_output():
    return os.system("cd ./Bootloader && make clean") == 0

def clean_kernel_output():
    return os.system("cd ./Kernel && make clean") == 0

def clean_all_output():
    return clean_bootloader_output() and clean_kernel_output()

def deploy(device_fd):
    bootloader_img = "./Bootloader/Bootloader.img"
    kernel_img = "./Kernel/Kernel.img"
    return make_bootloader() and send_to_device(bootloader_img, device_fd) and screen(device_fd) and make_kernel() and send_to_device(kernel_img, device_fd) and screen(device_fd)

def main_menu(device_fd):
    print("MAIN MENU")
    print("1. Deploy to device")
    print("2. Make all")
    print("3. Cleanup build output")
    print("4. Screen device")
    print("5. Exit")
    choice = int(input("Choose an option -> "))
    if choice == 1:
        deploy(device_fd)
    elif choice == 2:
        make_bootloader()
        make_kernel()
    elif choice == 3:
        clean_all_output()
    elif choice == 4:
        screen(device_fd)
    elif choice == 5:
        sys.exit(0)
    else:
        print("Invalid choice!")
    

def main():
    print("Welcome to XyOS toolkit!")
    device_fd = find_device()
    print("Found target device: " + device_fd)
    while True:
        main_menu(device_fd)

main()
