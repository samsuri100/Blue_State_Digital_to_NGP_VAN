# Automating_By_Check_Box Program Overview
## Files:
automated_by_check_box.py = Final Program <br />
automated_by_check_box_csv.py  = Testing Program, shows data that would be affected if final program were to run

# Non-Technical Overview:
This program was designed to be as simple as possible for the intended users. <br />

The program will ask the users: <br />
* Please enter the signup form ID:  <br />
* What List would you like to use? Please enter: span_list, house_list, vdr_list, ntl_list, volunteer_list, or enter 'ALL'):  <br />
* Please enter the start date (YYYY-MM-DD): <br />
* Please enter the end date (YYYY-MM-DD): <br />
* The program will now run, please make sure all information is correct and press 'enter' to proceed: <br />
* The program has completed, press 'enter' to quit: <br />

To correctly run the program and match the program output, the user must enter: <br />
* 275  <br />
* “span_list, house_list, vdr_list, ntl_list, volunteer_list, or 'ALL'”  <br />
* NOTE: words are case sensitive; only pick one word  <br />
* A particular start date (ie: 2016-02-15)  <br />
* A particular end date (ie: 2016-02-25)  <br />
* “enter key”  <br />
* “enter key”  <br />

# Technical Overview:
This program retrieves XML data from Blue State Digital, parses it, and breaks it down into a JSON dictionary that is then passed into an API call to NGP VAN. The program uses two queues (queue 1 and queue 2) and threading and will only affect users that fall within two inputted dates. This allows the program user to have greater control over the program. This program was designed to take into account check boxes, and specifically parses BSD's XML to find the status of each check box. There is also a threading lock both between each item in queue 1 and each item being appended to the DataFrame to ensure that everyone is added. For every check box, there will be a DataFrame, and each will be outputted to a CSV file. The program standardizes phone numbers so that the country code is always included.

All sensitive info, such as API ID's and secrets have been redacted, as they are private to Battleground Texas. The program cannot be run without this info, either from Battleground Texas or another similar organization.

# Making Changes to the Program:
To change the check box ID's, simply change the integers in the lists in lines 18 to 24. To change the activist codes and survey responses that are being applied, change the IDs and Types found in which_list_ac_sv

