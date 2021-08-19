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
import sqlite3

# Suppressed because of weird future warning with regex
warnings.simplefilter(action='ignore', category=FutureWarning)
dashline = "-" * 75
db_name = "./powerob.db"

def banner():
    print(r"""
       ___                        ___ _     
      / _ \_____      _____ _ __ /___| |__  
     / /_)/ _ \ \ /\ / / _ | '__//  /| '_ \ 
    / ___| (_) \ V  V |  __| | / \_//| |_) |
    \/    \___/ \_/\_/ \___|_| \___/ |_.__/ 

            author: Cory Wolff <fenrir>
            company: Layer 8 <layer8security.com>
    """)
    print(dashline + "\n")

def python_check():
    if sys.version_info.major != 3:
        print(color("[-] Please run with Python 3. Python 2 is ded."))
        sys.exit()

def db_check():
    if not path.exists('db.json'):
        return False
    else:
        print(color("[*] Db file found"))
        return True

def color(text):

	if text.startswith('[+]'):
		return "\033[%d;3%dm%s\033[0m" % (0, 2, text)
	if text.startswith('[-]'):
		return "\033[%d;3%dm%s\033[0m" % (0, 1, text)
	if text.startswith('[*]'):
		return "\033[%d;3%dm%s\033[0m" % (0, 3, text)
	


# Adds the new functions/obfuscated functions to the db file. 
def save_functions(filename, functions):

    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        sql = '''CREATE TABLE IF NOT EXISTS Files
                (FID INTEGER PRIMARY KEY AUTOINCREMENT,
                FILENAME VARCHAR(42))'''
        cursor.execute(sql)

        sql = '''CREATE TABLE IF NOT EXISTS Functions
                (FID INTEGER PRIMARY KEY AUTOINCREMENT,
                FILE_NAME VARCHAR(42),
                OG_FUNCTION VARCHAR(42),
                OB_FUNCTION VARCHAR(42))'''
        cursor.execute(sql)

        cursor.execute("SELECT * FROM Files WHERE FILENAME = :og_file", {"og_file": filename})
        rows = cursor.fetchall()

        if len(rows) > 0:
            # The file has been obfuscated before. Removed old functions from db and add new ones
            cursor.execute("DELETE FROM Functions WHERE FILE_NAME = :file", {"file": filename})

            for f in functions.items():
                cursor.execute("INSERT INTO Functions(FILE_NAME, OG_FUNCTION, OB_FUNCTION) VALUES (?,?,?)", (filename, f[0],f[1]))
        else:
            # File is not in db so add filename to Files table and add functions to Functions table
            cursor.execute("INSERT INTO Files(FILENAME) VALUES(?)", (filename, ))
            for f in functions.items():
                cursor.execute("INSERT INTO Functions(FILE_NAME, OG_FUNCTION, OB_FUNCTION) VALUES (?,?,?)", (filename, f[0],f[1]))
        conn.commit()
        return True

    except:
        
        print(color("[-] Unexpected error: {}".format(sys.exc_info())))
        return False


def find_functions(input):
    print(color("[+] Loading the Powershell script"))

    #function_pattern = r'([Ff]unction\s([A-Z]{1}[a-z]{2,10})-([A-Z]{1}[a-z]+[A-Z]{1}([^\s||^(]+)))'
    function_pattern = r'([Ff]unction\s(.*)\s\{)'
    if not input.endswith('.ps1'):
        print(color("[-] Error: The input file must end with .ps1"))
        sys.exit()

    try:
        f = open(input,"r")
        print(color("[+] Locating functions"))
        contents = f.read()
        funcs = re.findall(function_pattern, contents)
        
        if funcs:
            #Create list for function names
            function_names = []
            for i in funcs:
                function_names.append(i[0].split(" ")[1])

            return function_names
        else:
            print(color("[-] No Functions Found. Exiting..."))
            return "0"

    except IOError as e:
      errno, strerror = e.args
      print(color("[-] I/O error({0}): {1}".format(errno,strerror)))
    except: #handle other exceptions such as attribute errors
      print(color("[-] Unexpected error:" + str(sys.exc_info()[0])))
    pass

def create_obfuscated_functions(functions):
    print(color("[+] Obfuscating functions"))

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
        print(color("[-] I/O error ({}): {}".format(errno, strerror)))
        sys.exit()
    except: #handle other exceptions such as attribute errors
        print(color("[-] Unexpected error yo:" + str(sys.exc_info())))
        sys.exit()
    pass

#
#
# Start of class
#
#
class PowerOb(object):

    def __init__(self):
        parser = argparse.ArgumentParser(usage='''powerob.py <command> [<args>]
            Possible Commands:
            <obfuscate> // Obfuscate new powershell script
            <list> // List obfuscated files and their commands
            <getcommand> // Get a particular command from an obfuscated file
            <cleardb> // Clears the database of previously obfuscated files and functions

            Try powerob.py <command> -h for help with a particular command.
            ''')
        parser.add_argument('command', help='Command to run')

        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print (color('[-] Unrecognized command'))
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()


    def obfuscate(self):
        parser = argparse.ArgumentParser(description='Obfuscate a new Powershell script.')
        parser.add_argument('inputfile', type=str)
        parser.add_argument('outputfile', type=str)

        db_check()

        args = parser.parse_args(sys.argv[2:])

        # Find the functions. Returns list of functions in the inputfile
        functions = find_functions(args.inputfile)
        
        if functions == "0":
            exit()

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
                print("\n")
                print(color("[+] Saving to db file"))
            print(color("[+] Done. Output file located at " + args.outputfile))

    def list(self):
        parser = argparse.ArgumentParser(description='List all obfuscated files and their commands.')

        if not os.path.exists(db_name):
            print(color("[-] No functions or files have been obfuscated."))
            sys.exit()
        else:
            try:
                conn = sqlite3.connect(db_name)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("SELECT * FROM Files")
                file_rows = cursor.fetchall()

                for filename in file_rows:

                    print(color('[*] Obfuscated File: ' + filename['FILENAME']))

                    print('{:<30s}{:>30s}'.format("Original Function","Obfuscated Function"))
                    print(dashline)

                    cursor.execute("SELECT * FROM Functions WHERE FILE_NAME = :filename", {"filename": filename['FILENAME']})
                    function_rows = cursor.fetchall()

                    for f in function_rows:
                        print('{:<30}{:>25}'.format(f['OG_FUNCTION'],f['OB_FUNCTION']))       
                    
                    print(dashline+"\n")

                print(color("[+] Done listing files. Over and out."))

            except OSError as e:
                errno, strerror = e.args
                print(color("[-] I/O error ({}): {}".format(errno, strerror)))
            except: #handle other exceptions such as attribute errors
                print(color("[-] Unexpected error opening db file: " + str(sys.exc_info())))
            pass


    def getcommand(self):
        parser = argparse.ArgumentParser(description='Get a particular command from an obfuscated file.')
        #parser.add_argument('file', type=str, help='The name of the obfuscated file.')
        parser.add_argument('scriptcommand', type=str, help='The name of the command from the original script that you would like the obfuscated equivalent.')
        args = parser.parse_args(sys.argv[2:])

        conn = sqlite3.connect(db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT FILE_NAME, OG_FUNCTION, OB_FUNCTION FROM Functions WHERE OG_FUNCTION LIKE :function",{"function":args.scriptcommand})

        rows = cursor.fetchall()

        if len(rows) == 0:
            print(color("[-] No commands found. Sorry bub."))
        else:

            print(color("[*] " + str(len(rows)) + " Command(s) Found"))

            print('{:<25s}{:<25s}{:>25s}'.format("Obfuscated File", "Original Function","Obfuscated Function"))
            print(dashline)
            for f in rows:
                    print('{:25s}{:<25s}{:>25s}'.format(f['FILE_NAME'],f['OG_FUNCTION'],f['OB_FUNCTION'])) 

    # Helper command to clear the database
    def cleardb(self):
        try:
            if os.path.exists("powerob.db"):
                os.remove("powerob.db")
                print(color("[+] Db cleared. See yaaaaaa"))
        except OSError as e:
            errno, strerror = e.args
            print(color("[-] Error clearing db: " + strerror))

    # Debug function
    def showdb(self):
            conn = sqlite3.connect(db_name)

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Functions")
            print(cursor.fetchall())



if __name__ == '__main__':

    banner()
    python_check()

    PowerOb()