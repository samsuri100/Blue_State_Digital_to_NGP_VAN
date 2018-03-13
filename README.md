# XML_To_JSON_API_Automation
This repository contains three different programs that were developed for Battleground Texas (BGTX), a non-profit organization in Austin, Texas: Automating_All_Users, Automating_By_Check_Box, and Automating_VDR_Form. Each transforms XML data into JSON and both make API calls to two different political data organizations, Blue State Digital (BSD) and NGP VAN (VAN). All sensitive information has been redacted.

## Automating_All_Users Program
The Automating_All_Users program retrieves XML form data from BSD for BGTX's signup form #275, parses it into JSON data, finds or creates users given the information, tags each person with the CMI 2017 activist code and survey response, updates this in Van's 'My Campaign' universe, and creates an CSV file displaying the information of any affected individuals. After the XML Data is initially parsed, all further steps are done simultaneously with the use of threads and multiprocessing.

This program only applies the CMI 2017 activist code and survey response, and does not take into account if a user checked any of the boxes on the signup form. It updates everyone that filled out the required fields on the signup form.

##  Automating_By_Check_Box Program
This program retrieves XML form data from BSD for BGTX's signup form #275, parses it into JSON data, finds or creates users given the information, applies one or all activist codes and or survey question responses depending on user input, updates this in Van's 'My Campaign' universe, and creates a CSV file, per activist code and or survey response being applied, displaying the information of any affected individuals. After the XML Data is initially parsed, all further steps are done simultaneously with the use of threads and multiprocessing.

The program gives the user the option to update information for a specific check box or all the check boxes. This allows the user to choose to separately update the information of every person using every activist code, without running the program multiple times.

## Automating_VDR_Form Program
The Automating_All_Users program retrieves XML form data from BSD for BGTX's signup form #295, parses it into JSON data, finds or creates users given the information, tags each person with both the Volunteer and VDR survey response, updates this in Van's 'My Campaign' universe, and creates an CSV file displaying the information of any affected individuals. After the XML Data is initially parsed, all further steps are done simultaneously with the use of threads and multiprocessing.
