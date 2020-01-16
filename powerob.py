#!/usr/bin/python3

import re
import sys
import argparse
import random
import string

# REGEX expression: function\s([A-Z]{1}[a-z]{2,10})-([A-Z]{1}[a-z]+[A-Z]{1}([^\s||^(]+))
function_pattern = r"(function\s([A-Z]{1}[a-z]{2,10})-([A-Z]{1}[a-z]+[A-Z]{1}([^\s||^(]+)))"

def banner():
    print(r"""
   ___                        ___ _     
  / _ \_____      _____ _ __ /___| |__  
 / /_)/ _ \ \ /\ / / _ | '__//  /| '_ \ 
/ ___| (_) \ V  V |  __| | / \_//| |_) |
\/    \___/ \_/\_/ \___|_| \___/ |_.__/ 

    """)

def get_funcs(input):
    print("[+] Loading the Powershell script")
    if not input.endswith('.ps1'):
        print("Error: The input file must end with .ps1")
        exit()

    try:
        file = open(input,"r")
        print("[+] Locating functions")
        funcs = re.findall(function_pattern, file.read())
        
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

def obfuscate_funcs(input,functions):
    print("[+] Obfuscating functions")
    try:

        #Create new dict for replacements
        substitutions = {}

        for f in functions:

            #Generate a random string to use in place of function name
            rando_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            substitutions[f] = str(rando_name)
        
        # Open the file
        with open(input) as file:
            file_as_str = file.read()

            regex = re.compile("|".join(map(re.escape, substitutions.keys(  ))))
            newtext = regex.sub(lambda match: substitutions[match.group(0)], file_as_str)

        return newtext


    except IOError as e:
        errno, strerror = e.args
        print("[-] I/O error ({}): {}".format(errno, strerror))
    except: #handle other exceptions such as attribute errors
        print("Unexpected error:", sys.exc_info()[0])
    pass

if __name__ == '__main__':
    banner()
  
    parser = argparse.ArgumentParser(description='Powershell Script Obfuscator')
    parser.add_argument('inputfile', type=str, help='Location of the Powershell script to obfuscate')
    parser.add_argument('outputfile', type=str, help='Path and filename of the output script')
    args = parser.parse_args()

    functions = get_funcs(args.inputfile)
    newtext_with_functions = obfuscate_funcs(args.inputfile, functions)

    # Write file
    try: 
        f = open(args.outputfile, "w+")
        f.write(newtext_with_functions)
        f.close()
    except IOError as e:
        errno, strerror = e.args
        print("[-] I/O error ({}): {}\n[-] No file written".format(errno, strerror))
    except: #handle other exceptions such as attribute errors
        print("Unexpected error:", sys.exc_info()[0])
    pass
    print("\n[+] Done. Output file located at " + args.outputfile) 