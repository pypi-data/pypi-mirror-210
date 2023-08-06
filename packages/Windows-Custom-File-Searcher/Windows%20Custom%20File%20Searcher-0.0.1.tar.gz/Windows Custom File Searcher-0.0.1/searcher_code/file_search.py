#! python3
from audioop import mul
import os
import sys
import time
import argparse
import multiprocessing

from trial1 import main
from trial2 import info




if __name__ == '__main__':

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-f', type=str, default=None, help='Base folder to start search')
        parser.add_argument('-w', type=str, default='', help='Word to search')
        parser.add_argument('-t', type=str, default=None, help='File type to search')

        cmd_args = parser.parse_args()

        with multiprocessing.Manager() as manager:

            total = multiprocessing.Value('i', 0)
            iterations = multiprocessing.Value('i', 0)
            start_file = manager.list([])


            if not cmd_args.f:
                print("Searching Drives E & F\n")

                drive_f = multiprocessing.Process(target=main, args=("F:\\", cmd_args.w, cmd_args.t, total, iterations, start_file, None,))
                drive_e = multiprocessing.Process(target=main, args=("E:\\", cmd_args.w, cmd_args.t, total, iterations, start_file, None,))

                drive_f.start()
                drive_f.join()
                
                drive_e.start()
                drive_e.join()

            else:
                main(cmd_args.f, cmd_args.w, cmd_args.t, total, iterations, start_file, cmd_args.f)
                
            info(total, iterations, start_file)
        
            # os.startfile('output.txt')

    except:
        sys.exit()


# TO DO
# unittesting
# version control
# package it as a universal import module with cmd command
# pypi if possible

# BUGS
# Search for 'Final' with file type as mp3 --> FIXED

