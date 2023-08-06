#! python3
import os
import sys
import time

from trial1 import output_handler


def info(total, iterations, start_file):
     
    output = output_handler()

    print(f'\nMatching files: {total.value};  Files Searched: {iterations.value}')
    print('-'*150, file=output)
    print('\n\n', file=output)
    if total.value == 1:
        print(start_file)
        os.startfile(start_file[0])
    elif total.value == 0:
        print('No files found')
        print('Closing...')
        time.sleep(3)
    else:
        while True:
            _ = input("Enter file path to open or ['q' to exit]: ")
            if os.path.exists(os.path.abspath(_)):
                os.startfile(os.path.join(_))
            elif _.lower() == 'q':
                sys.exit()
            elif not os.path.exists(os.path.abspath(_)):
                print('File path DOES NOT EXIST.')
            else:
                break
