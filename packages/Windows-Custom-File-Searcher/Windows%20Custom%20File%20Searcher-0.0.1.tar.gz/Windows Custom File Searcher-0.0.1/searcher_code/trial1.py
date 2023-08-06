#! python3
import os
import re
import time


def output_handler():
    file = open('output_limit.txt', 'r')
    try:
        count = int(file.read())
    except ValueError:
        with open('output_limit.txt', 'w') as file:
            file.write('0')
        file = open('output_limit.txt', 'r')
        count = int(file.read())

    file_w = open('output_limit.txt', 'w')
    if count < 3:
        output = open('output.txt', 'a', encoding='utf-8')
        file_w.write(str(count + 1))
    else:
        output = open('output.txt', 'w',encoding='utf-8')
        file_w.write('0')

    file_w.close()

    return output


def main(home_folder, word, type, total, iterations, start_file, drive_given):
       
    start_file_switch = True

    output = output_handler()

    print(f'[ {time.ctime()} ]\n', file=output)

    if drive_given:
        if os.path.exists(home_folder):
            print(f'Base Folder: {home_folder}', file=output)
            print(f'Base Folder: {home_folder}')
        else:
            print('Folder path DOES NOT exist.\n', file=output)
            print('Folder path DOES NOT exist.')
            return


    for root, dirs, files in os.walk(home_folder):
        for file in files:
            file_path = os.path.join(root, file)
         
            if re.search(r'{}'.format(word.lower()), str(file.lower().split('.')[:-1]).replace('-', ' ').replace('_', ' ')):
                if type:
                  
                    if file.split('.')[-1].lower() == type.lower():
                        print(f'"{word}" Found in: {file}', file=output)
                        print(f'Folder: {root}\n', file=output)	
                        print(f'"{word}" Found in: {file}')
                        print(f'Folder: {root}')
                        print(f'File Path: {root}\{file}\n\n')
                        total.value += 1
                        
                        if start_file_switch:
                            start_file.append(file_path)
                            start_file_switch = False
                else:
                    print(f'"{word}" Found in: {file}', file=output)
                    print(f'Folder: {root}\n', file=output)
                    print(f'"{word}" Found in: {file}')
                    print(f'Folder: {root}')
                    print(f'File Path: {root}\{file}\n\n')
                    total.value += 1

                    if start_file_switch:
                        start_file.append(file_path)
                        start_file_switch = False
               
            iterations.value += 1


    output.close()
        