#!/usr/bin/python3

import os.path
from os import path
import re
import sys
import argparse
import random
import string
import json
import warnings

# Suppressed because of weird future warning with regex
warnings.simplefilter(action='ignore', category=FutureWarning)
dashline = '-' * 75

def banner():
    print(r"""
       ___                        ___ _     
      / _ \_____      _____ _ __ /___| |__  
     / /_)/ _ \ \ /\ / / _ | '__//  /| '_ \ 
    / ___| (_) \ V  V |  __| | / \_//| |_) |
    \/    \___/ \_/\_/ \___|_| \___/ |_.__/ 

            author: Cory Wolff <visnet>
            company: Layer 8 <layer8security.com>
    """)
    print(dashline + "\n")

def python_check():
    if sys.version_info.major != 3:
        print("[*] Please run with Python 3. Python 2 is ded.")
        exit()

def db_check():
    if not path.exists('db.json'):
        return False
    else:
        print("[*] Db file found")
        return True

# Adds the new functions/obfuscated functions to the db file. e.g. filename => original function: obfuscated function
def save_functions(filename, functions):

    to_write = {}
    to_write[filename] = functions

    try:
        with open('db.json', "w+") as file:
            file.write(json.dumps(to_write))
            file.close()
            return True
    except IOError as e:
        errno, strerror = e.args
        print("[-] I/O error ({}): {}\n[-] No file written".format(errno, strerror))
    except: #handle other exceptions such as attribute errors
        print("Unexpected error saving to db file: ", sys.exc_info()[0])
    pass

def find_functions(input):
    print("[+] Loading the Powershell script")

    function_pattern = r'(function\s([A-Z]{1}[a-z]{2,10})-([A-Z]{1}[a-z]+[A-Z]{1}([^\s||^(]+)))'
    if not input.endswith('.ps1'):
        print("[-] Error: The input file must end with .ps1")
        exit()

    try:
        f = open(input,"r")
        print("[+] Locating functions")
        contents = f.read()
        funcs = re.findall(function_pattern, contents)
        
        if funcs:
            #Create list for function names
            function_names = []
            for i in funcs:
                function_names.append(i[0].split(" ")[1])

            return function_names
        else:
            print("[-] No Functions Found. Exiting...")
            exit()

    except IOError as e:
      errno, strerror = e.args
      print("[-] I/O error({0}): {1}".format(errno,strerror))
    except: #handle other exceptions such as attribute errors
      print("[-] Unexpected error:", sys.exc_info()[0])
    pass

def create_obfuscated_functions(functions):
    print("[+] Obfuscating functions")

    # Create list for old function names with corresponding obfuscated function
    substitutions = {}

    for f in functions:

        # Generate a random string to use in place of each function name
        rando_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        substitutions[f] = str(rando_name)

    return substitutions

def write_obfuscated_file(inputfile, outputfile, functions):

    try:
        # Open the file
        with open(inputfile) as file:
            file_as_str = file.read()
            regex = re.compile("|".join(map(re.escape, functions.keys(  ))))
            newtext = regex.sub(lambda match: functions[match.group(0)], file_as_str)
            # Write file
        with open(outputfile, "w+") as f:
            f.write(newtext)
            f.close()

        return True

    except IOError as e:
        errno, strerror = e.args
        print("[-] I/O error ({}): {}".format(errno, strerror))
        exit()
    except: #handle other exceptions such as attribute errors
        print("Unexpected error yo:", sys.exc_info())
        exit()
    pass

class PowerOb(object):

    def __init__(self):
        parser = argparse.ArgumentParser(description='Pretends to be git',usage='''powerob.py <command> [<args>]
            Possible Commands:
            obfuscate - Obfuscate new powershell script
            list - List obfuscated files and their commands
            getcommand - Get a particular command from an obfuscated file

            Try powerob.py <command> -h for help with a particular command.
            ''')
        parser.add_argument('command', help='Command to run')
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print ('Unrecognized command')
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()


    def obfuscate(self):
        parser = argparse.ArgumentParser(description='Obfuscate a new Powershell script.')
        # prefixing the argument with -- means it's optional
        parser.add_argument('inputfile', type=str)
        parser.add_argument('outputfile', type=str)

        db_check()

        args = parser.parse_args(sys.argv[2:])


        # Find the functions. Returns list of functions in the inputfile
        functions = find_functions(args.inputfile)

        # Generate random strings. This is where substitutions{} is populated. Returns list. eg. [original_function, obfuscated_function]
        obfuscated_functions = create_obfuscated_functions(functions)

        obfuscated_file = write_obfuscated_file(args.inputfile, args.outputfile, obfuscated_functions)

        if obfuscated_file:

            print("\n" + dashline)
            print('{:<30s}{:>30s}'.format("Original Function","Obfuscated Function"))
            print(dashline)
            
            for functions in obfuscated_functions.items():
                print('{:<30}{:>25}'.format(functions[0],functions[1]))

            save_db = save_functions(args.outputfile, obfuscated_functions)
            if save_db:
                print("\n[+] Saving to db file")
            print("[+] Done. Output file located at " + args.outputfile)

    def list(self):
        parser = argparse.ArgumentParser(description='List all obfuscated files and their commands.')

        try:
            with open('db.json') as file:
                g = json.load(file)

                if file == None:
                    print ("[-] No obfuscated files found!")
                
                for filename, funcs in g.items():

                    print("\n" + dashline)
                    print('Obfuscated File: ' + filename)

                    print('{:<30s}{:>30s}'.format("Original Function","Obfuscated Function"))
                    print(dashline)

                    for f in funcs.items():
                        print('{:<30}{:>25}'.format(f[0],f[1]))       
                    print(dashline)
            print("[+] Done")

        except IOError as e:
            errno, strerror = e.args
            if errno == 2:
                print('[-] No obfuscated files found!')
            else:
                print("[-] I/O error ({}): {}".format(errno, strerror))
        except: #handle other exceptions such as attribute errors
            print("Unexpected error opening db file: ", sys.exc_info()[0])
        pass


    def getcommand(self):
        parser = argparse.ArgumentParser(description='Get a particular command from an obfuscated file.')
        parser.add_argument('file', type=str, help='The name of the obfuscated file.')
        parser.add_argument('scriptcommand', type=str, help='The name of the command from the original script that you would like the obfuscated equivalent.')
        args= parser.parse_args(sys.argv[2:])



if __name__ == '__main__':

    banner()
    python_check()

    PowerOb()