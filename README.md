![fenrir-desktop-bg](https://user-images.githubusercontent.com/8293038/133816238-7152221b-c37d-46ca-831d-ff636178f44f.png)

# Powerob
An on-the-fly Powershell script obfuscator meant for red team engagements. Built out of necessity.

This only obfuscates functions and removes found in PowerShell scripts. Roadmap includes bfuscating variables. Pull requests and collaborative welcomed.

### About
This was built out of the need to bypass endpoint security on a recent engagement. During priv esc attempts I could not download [PowerUp.ps1](https://github.com/PowerShellMafia/PowerSploit/blob/master/Privesc/PowerUp.ps1) until it was obfuscated.

This is technically v2 and has been updated to remove comments.

### Installation
`git clone https://github.com/cwolff411/powerob`

### Usage
`python3 powerob.py obfuscate originalfile.ps1 obfuscatedfile.ps1`

Takes an INPUTFILE obfuscates it and dumps the obfuscated version into OUTPUTFILE.

![PowerOb](https://user-images.githubusercontent.com/8293038/81839384-7059b300-9515-11ea-912a-c9432a5e0287.png)


* * *
`python3 powerob.py list`

Lists all of the currently obfuscated files along with their commands and associated obfuscated commands.

![PowerOb](https://user-images.githubusercontent.com/8293038/81839399-751e6700-9515-11ea-86c7-d9374221f483.png)

* * *
`python3 powerob.py getcommand COMMAND_NAME`

For reference on the fly for when you forget. Takes the original command name and displays the obfuscated command name to be used in Powershell.

![PowerOb](https://user-images.githubusercontent.com/8293038/81839407-78195780-9515-11ea-8b0e-58d7bd44b783.png)

* * *
`python3 powerob.py cleardb`

Maintenance function to clear the db of past obfuscated files and functions.


### License
[MIT License](https://opensource.org/licenses/MIT)