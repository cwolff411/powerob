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

            coded by Cory Wolff <visnet>
            company: Layer 8 <layer8security.com>
    """)
    print(dashline + "\n")

def python_check():
    if sys.version_info.major != 3:
        print("[*] Please run with Python 3. Python 2 is ded.")
        exit()

def db_check():
    if not path.exists('db.txt'):
        print("[*] No db file.")
        return False

def get_funcs(input):
    print("[+] Loading the Powershell script")
    if not input.endswith('.ps1'):
        print("Error: The input file must end with .ps1")
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
      print("%sI/O error({0}): {1}".format(errno,strerror))
    except: #handle other exceptions such as attribute errors
      print("Unexpected error:", sys.exc_info()[0])
    pass

def obfuscate_funcs(functions):
    print("[+] Obfuscating functions")
    i = 1

    for f in functions:

        # Generate a random string to use in place of each function name
        rando_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))

        substitutions[i] = {}
        substitutions[i]['og_name'] = f
        substitutions[i]['ob_name'] = str(rando_name)
        i = i + 1

    try:
        # Open the file
        with open(args.inputfile) as file:
            file_as_str = file.read()
            regex = re.compile("|".join(map(re.escape, substitutions[1].keys(  ))))
            newtext = regex.sub(lambda match: substitutions[1][match.group(0)], file_as_str)

        return newtext

    except IOError as e:
        errno, strerror = e.args
        print("[-] I/O error ({}): {}".format(errno, strerror))
        exit()
    except: #handle other exceptions such as attribute errors
        print("Unexpected error yo:", sys.exc_info())
        exit()
    pass

def save_functions(functions):
    to_write = {}
    to_write[args.inputfile] = functions
    try:
        with open('db.json', "w+") as file:
            file.write(json.dumps(to_write))
            file.close()
    except IOError as e:
        errno, strerror = e.args
        print("[-] I/O error ({}): {}\n[-] No file written".format(errno, strerror))
    except: #handle other exceptions such as attribute errors
        print("Unexpected error: yo", sys.exc_info()[0])
    pass

if __name__ == '__main__':

    banner()
    python_check()
    db_check()

    parser = argparse.ArgumentParser(description='Powershell Script Obfuscator')
    parser.add_argument('inputfile', type=str, help='Location of the Powershell script to obfuscate')
    parser.add_argument('outputfile', type=str, help='Path and filename of the output script')
    args = parser.parse_args()

    function_pattern = r'(function\s([A-Z]{1}[a-z]{2,10})-([A-Z]{1}[a-z]+[A-Z]{1}([^\s||^(]+)))'
    completed_obfuscation = False

    #Create new dict for replacements
    substitutions = {}

    # Find the functions.
    functions = get_funcs(args.inputfile)

    # Open file and generate random strings. This is where substitutions{} is populated
    newtext_with_functions = obfuscate_funcs(functions)

    # Write file
    try: 
        f = open(args.outputfile, "w+")
        f.write(newtext_with_functions)
        f.close()
    except IOError as e:
        errno, strerror = e.args
        print("[-] I/O error ({}): {}\n[-] No file written".format(errno, strerror))
    except: #handle other exceptions such as attribute errors
        print("Unexpected error: yo", sys.exc_info()[0])
    pass

    print("\n" + dashline)
    print('{:<10}{:<30s}{:>30s}'.format("ID", "Original Function","Obfuscated Function"))
    print(dashline)
    
    for cnt, functions in substitutions.items():
        print('{:<10}{:<30s}{:>25}'.format(cnt, functions['og_name'],functions['ob_name']))

    save_db = save_functions(substitutions)
    if save_db:
        print("[+] Saving to db file")
    print("\n[+] Done. Output file located at " + args.outputfile)