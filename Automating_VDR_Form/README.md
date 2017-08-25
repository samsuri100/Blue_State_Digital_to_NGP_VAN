# Automating_All_Users Program Overview
## Files:
automating_vdr_form.py = Final Program <br />

##  Non-Technical Overview:
This program was designed to be as simple as possible for the intended users. 

The program will ask the users: <br />
* Please enter the VDR 'Welcome Series' signup form ID: <br />
* Please enter the start date (YYYY-MM-DD) <br />
* Please enter the end date (YYYY-MM-DD) <br />
* The program will now run and match all individuals in My Campaign, press ‘enter’ to proceed: <br />
* The program has completed, press 'enter' to quit: <br />

To correctly run the program and match the program output, the user must enter: <br />
* 295 <br />
* A particular start date (ie: 2016-02-15) <br />
* A particular end date (ie: 2016-02-25) <br />
* “enter key” <br />
* “enter key” <br />

## Technical Overview:
This program retrieves XML data from Blue State Digital, parses it, and breaks it down into a JSON dictionary that is then passed into an API call to NGP VAN. The program uses only one queue and threading and will only affect users that fall within two inputted dates. This program does not take into account check boxes and this function cannot be added in this program (Please see Automating_By_Check_Box Program). This allows the program user to have greater control over the program. There is also a threading lock between each item being appended to the DataFrame to ensure that everyone is added. The program standardizes phone numbers so that the country code is always included.

All sensitive info, such as API ID's and secrets have been redacted, as they are private to Battleground Texas. The program cannot be run without this info, either from Battleground Texas or another similar organization.

## Making Changes to the Program
To change the program, one simply has to change the values that belong to the ID and Type keys that correspond to the van_ac_sv_data variable.
