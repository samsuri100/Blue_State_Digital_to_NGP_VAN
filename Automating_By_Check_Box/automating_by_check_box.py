#!/usr/bin/python
"""
Copyright 2017 Sam Suri, all rights reserved. Only use with permission. Contact: samsuri100@gmail.com, (210)296-6021

version 2
"""

import hmac, hashlib, time, json, requests, copy
import threading
import urllib.request
from queue import Queue
from pandas import DataFrame
from json import dumps, loads
from xmljson import yahoo as yh
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import fromstring

# Declaring global constants, these are form dependant and will vary from form to form
# These strings represent the ID of a check box, if checked, this ID is present
SPAN_LIST = ['enter BSD check box ID(s)']
HOUSE_LIST = ['enter BSD check box ID(s)']
VDR_LIST = ['enter BSD check box ID(s)']
NTL_LIST = ['enter BSD check box ID(s)']
VOLUNTEER_LIST = ['enter BSD check box ID(s)']

# Integer is constant that will be referenced for loop inserting into Queue 1
NUM_ACTIVIST_CODES = 5

# Declaring functions that make code respondent to user input on which AC/SV they are applying
# Function asks the user which list they would like to use
def which_list():  # Returns boolean value, name of activist code to ouput to CSV file name, list of ID's
    print("\nWhat List would you like to use? \n\nPlease enter: span_list, house_list, "
          "vdr_list \nntl_list, volunteer_list, or enter 'ALL'): ")
    answer = input()
    if answer == "span_list":
        return 0, "span_list", SPAN_LIST
    elif answer == "house_list":
        return 0, "house_list", HOUSE_LIST
    elif answer == "vdr_list":
        return 0, "vdr_list", VDR_LIST
    elif answer == "ntl_list":
        return 0, "ntl_list", NTL_LIST
    elif answer == "volunteer_list":
        return 0, "volunteer_list", VOLUNTEER_LIST
    elif answer == 'ALL':  # if user chooses to have all applied, returns boolean 1 to allow Queue 1 to be populated
        return 1, '', ''

# Function returns JSON data to a variable, used in second VAN API call
def which_list_ac_sv(list_in_use):
    if list_in_use == SPAN_LIST:
        return {"resultCodeId": None, "responses": [{"activistCodeId": ["enter code ID here"], "action": "Apply", "type": "ActivistCode"}]}
    elif list_in_use == HOUSE_LIST:
        return {"resultCodeId": None, "responses": [{"activistCodeId": ["enter code ID here"], "action": "Apply", "type": "ActivistCode"}]}
    elif list_in_use == VDR_LIST:
        return {"resultCodeId": None, "responses": [{"surveyQuestionId": ["enter code ID here"], "surveyResponseId":
                ["enter survey ID here"], "type": "SurveyResponse"}]}
    elif list_in_use == NTL_LIST:
        return {"resultCodeId": None, "responses": [{"surveyQuestionId": ["enter code ID here"], "surveyResponseId":
                ["enter survey ID here"], "type": "SurveyResponse"}]}
    elif list_in_use == VOLUNTEER_LIST:
        return {"resultCodeId": None, "responses": [{"surveyQuestionId": ["enter code ID here"], "surveyResponseId":
                ["enter survey ID here"], "type": "SurveyResponse"}]}

#BSD Call and Declarations:
api_secret = "[enter BSD api_secret here]"  # API secret provided by BSD for user Sam Suri
api_ts = int(time.time())  # API call uses HMAC authentication that incorporates times
api_id = "[enter BSD api id here]"  # API ID provided by BSD for user Sam Suri

api_baseCall = "/page/api/signup/get_signups_by_form_id"  # API Call to get list of signups based on form ID
signup_form_id = str(input("Please enter the signup form ID: "))  # prompts the user for input of form ID
# Creates paramaters for API call incorporates user ID, time created, and form ID
api_param = "api_ver=2&api_id=" + api_id + "&api_ts=" + (str(api_ts)) + "&signup_form_id=" + str(signup_form_id)
all_bool, name_of_list_in_use, list_in_use = which_list()  # Calls function which_list(), assigns to three variables

# Creates string to pass into with HMAC authentication
signing_string = api_id + '\n' + str(api_ts) + '\n' + api_baseCall + '\n' + api_param
# Creates HMAC authentication, uses API secret 'singning_string'
api_mac = hmac.new(api_secret.encode(), signing_string.encode(), hashlib.sha1).hexdigest()
# Creates full address of API call, inserts API Id, time created, HMAC authentication code, and form ID
api_url = "http://battletx.bsd.net/page/api/signup/get_signups_by_form_id?api_ver=2&api_id=" + api_id + "&api_ts=" + \
          str(api_ts) + "&api_mac=" + api_mac + "&signup_form_id=" + str(signup_form_id)

#Reformating BSD XML:
api_xml_data = urllib.request.urlopen(api_url).read()  # Uses urllib library to read XML data from BSD API URL
doc = dumps(yh.data(fromstring(api_xml_data)))  # Parses XML data using xmljson library, parses using yahoo standard
loaded_doc = json.loads(doc)  # Deserializes data

#VAN Call and Declarations
van_app_name = '[enter VAN id here]'  # Van User ID
# Van Secret, boolean number after vertical line indicates VAN universe, 1 = VAN-My Campaign, 0 = NGP
van_secret = '[enter van secret here]'
van_base_url = 'https://api.securevan.com/v4'  # Base URL for API call
van_find_url = '/people/FindOrCreate'  # first VAN API call to find or create individuals, uses POST request
van_total_find_url = van_base_url + van_find_url  # joins base URL and first API call

# Function dynamically generates custom URL for second VAN API call used by program, /people/{VAN ID}/canvassResponses
def van_total_ac_sv_url(indiv_id):  # Returns string
    return van_base_url + '/people/' + str(indiv_id) + '/canvassResponses'

# Function iterates over dictionary and checks keys, if keys match strings, count is altered
def indiv_dict_length(tuple):
    count = 0  # declares temporary count variable, returns it at end of function
    for k, v in tuple:
        if v != {}:
            if k == 'firstname':
                count += 1
            if k == 'lastname':
                count += 1
            if k == 'email':
                count += 1
            if k == 'zip':
                count += 1
            if k == 'phone':
                count += 1
    return count

# Function checks to see if multiple check boxes have been selected
def mult_check_box_copy(mult_check_box_list, value):
    if isinstance(value, list) == True:  # checks dictionary value to see if it is a list
        for i in value:  # if so, breaks it down into dictionaries
            for k, v in i.items():
                if k == 'signup_form_field_id':  # if key is encountered, different values are appended to mult_check_box
                    # appends to list using deep copy, so that there is no possibility of passing by reference
                    mult_check_box_list.append(copy.deepcopy(v))
        return 1  # returns boolean 1 to indicate that the individual has checked multiple check boxes

# Function creates initial data frame using PANDAS library and creates columns
def create_data_frame():
    columns = ['First Name', 'Last Name', 'Phone Number', 'Zip Code', 'Email']
    df = DataFrame(columns=columns)
    return df  # returns data frame to a variable

# Function appends to existing dataframe, temporary dictionary is passed in
def append_csv_row(dictionary):  # looks for keys and inserts values into data frame
    df.loc[len(df)] = [dictionary['firstName'],
                        dictionary['lastName'],
                        dictionary['phones'][0]['phoneNumber'],
                        dictionary['addresses'][0]['zipOrPostalCode'],
                        dictionary['emails'][0]['email']
                       ]

# Function prints data frame to csv file whose title dynamically includes current date and AC/SV inputted by user
def print_data_frame_to_csv(name_of_list_in_use):
    csv_name = 'Contacts Affected on ' + str(time.strftime('%d-%m-%Y')) + ' for ' + name_of_list_in_use + '.csv'
    df.to_csv(csv_name, index = False)  # index is set to false as programs like Excel make this redundant
    global df  # allows DataFrame to be cleared after each iteration in Queue 1, references pointer storing df
    df = df.drop(df.index[:])

# Function checks to see if multiple check boxes clicked match any check box in AC/SV list and if there is a match,
# updates both contact and AC/SV in My Campaign
def mult_check_box_compare(mult_check_box_list, temp_dict, van_ac_sv_data, list_in_use):
    for y in list_in_use:
        for x in mult_check_box_list:
            if x == y:
                # calls first VAN API call, checking to see if user exists or not
                van_post = requests.post(van_total_find_url, json=temp_dict, auth=(van_app_name, """van_secret"""))
                for k, v in loads(van_post.text).items():  # reads response and coverts to tuple
                    if k == 'vanId':
                        vanid = v  # reads keys to find van ID
                        # calls second VAN API call, updates user with appropriate AC/SV
                        requests.post(van_total_ac_sv_url(vanid), json=van_ac_sv_data, auth=(van_app_name, """van_secret"""))
                        append_csv_row(temp_dict)  # appends information on user to CSV file
                        return

# Function checks to see if the single check box clicked matches any of the code in appropriate AC/SV List
# and if there is a match, updates both contact and AC/SV in My Campaign
def single_check_box_compare(dictionary, temp_dict, van_ac_sv_data, list_in_use):
    for k4, v4 in dictionary.items():
        if k4 == 'signup_form_field_id':
            for y in list_in_use:
                if v4 == y:
                    # calls first VAN API call, checking to see if user exists or not
                    van_post = requests.post(van_total_find_url, json=temp_dict, auth=(van_app_name, """van_secret"""))
                    for k, v in loads(van_post.text).items():  # reads response and coverts to tuple
                        if k == 'vanId':
                            vanid = v   # reads keys to find van ID
                            # calls second VAN API call, updates user with appropriate AC/SV
                            requests.post(van_total_ac_sv_url(vanid), json=van_ac_sv_data, auth=(van_app_name, """van_secret"""))
                            # appends information on user to CSV file
                            append_csv_row(temp_dict)
                            return

#Queue and threading variables and declarations
q1 = Queue(maxsize = NUM_ACTIVIST_CODES)  # declares first Queue of size of all activist codes being tested for
q2 = Queue(maxsize = 2000)  # declares second Queue of maxsize 2000, max in second Queue is realistically around 1000
number_of_threads_q1 = NUM_ACTIVIST_CODES  # threading equals number of AC/SV lists
number_of_threads_q2 = 4  # threads limited to 4 due to processing constraints of current computer, could go up to 10
queue_1_lock = threading.Lock()  # lock between each iteration in Queue 1, otherwise 12 threads will run at once

#function allows Queue 1 to insert the name of a list that corresponds to an activist code
def iter_act_codes(iter_num):  # range of integers is passed in that iterates over global constant NUM_ACTIVIST_CODES
    if iter_num == 0:
        return 'span list', SPAN_LIST
    elif iter_num == 1:
        return 'house list', HOUSE_LIST
    elif iter_num == 2:
        return 'volunteer list', VOLUNTEER_LIST
    elif iter_num == 3:
        return 'ntl list', NTL_LIST
    elif iter_num == 4:
        return 'vdr list', VDR_LIST

# Function starts the first Queue, allows program to run for each Activist Code being used
def execute_queue1(q1):
    with queue_1_lock:  # enforces a lock on each thread due to processing power of computer
        loaded_doc, i = q1.get(q1)

        name_of_list_in_use, list_in_use = iter_act_codes(i)  # calls function that returns name of a list
        # Variables holds JSON data, data is eventually passed to POST request of second API call
        van_ac_sv_data = which_list_ac_sv(list_in_use)

        # Breaks down nested dictionary from XML data into useful information
        for k, v in loaded_doc.items():
            for k1, v1 in v.items():
                for k2, v2 in v1.items():
                    for i in v2:  # When lists of dictionaries is reached, outputs each one to second Queue
                        q2.put((i, van_ac_sv_data, list_in_use))

        # Tests to see if second Queue is finished
        q2.join()

        # If Queue is empty, completed data frame is printed to CSV file
        print_data_frame_to_csv(name_of_list_in_use)

    q1.task_done()

# Function runs inside of second Queue, with a tuple from being passed in from either main body or Queue 1
def execute_queue2(tuple):
    while True:
        i, van_ac_sv_data, list_in_use = q2.get(tuple)  # breaks down tuple into different objects

        # initializes numerous lists and boolean values
        mult_check_box_list = []
        temp_dict = {}
        nested_dict = {}
        check_button = 0
        mult_check_box = 0
        # finds out how many fields each person has, assigns them to variables, allows program to know when to move on to next person
        temp_dict_length = indiv_dict_length(i.items())

        if temp_dict_length >= 3:  # makes sure that each person at least three fields, any less and VAN cannot match user
            for k3, v3 in i.items():  # breaks dictionary into tuple
                if v3 != {}:  # makes sure that only answered fields are included
                    if k3 == 'stg_signup_extra':
                        # deep copies values from v3 into mult_check_box_list, returns 1 if multiple boxes were clicked
                        mult_check_box = mult_check_box_copy(mult_check_box_list, v3)
                        check_button = 1  # boolean value is set to 1, means at least one check box has been clicked
                        nested_dict = v3
                    if k3 == 'firstname':
                        k3 = 'firstName'
                        temp_dict[k3] = v3  # if key matches, appends key, value pair to temp_dict
                    if k3 == 'lastname':
                        k3 = 'lastName'
                        temp_dict[k3] = v3  # if key matches, appends key, value pair to temp_dict
                    if k3 == 'email':
                        k3 = 'emails'
                        v3 = [{'email': v3}]  # reassigns key to match VAN JSON
                        temp_dict[k3] = v3  # if key matches, appends key, value pair to temp_dict
                    if k3 == 'zip':
                        k3 = 'addresses'
                        v3 = [{'zipOrPostalCode': v3}]  # reassigns key to match VAN JSON
                        temp_dict[k3] = v3  # if key matches, appends key, value pair to temp_dict
                    if k3 == 'phone':
                        k3 = 'phones'
                        v3 = '1-' + v3[0:3] + '-' + v3[3:6] + '-' + v3[6:]  # reassigns value to match VAN style
                        v3 = [{'phoneNumber': v3}]  # reassigns key to match VAN JSON
                        temp_dict[k3] = v3

                    # makes sure that all filled out fields have been added to temp_dict, and that at least one check box has been clicked
                    if (check_button == 1) & (len(temp_dict) == temp_dict_length):
                        if mult_check_box == 1:  # checks variable to see if multiple check boxes have been clicked
                            # allows list to be broken down into dictionaries so API calls can be made
                            mult_check_box_compare(mult_check_box_list, temp_dict, van_ac_sv_data, list_in_use)
                            break
                        else:
                            # allows single dictionary to proceed so that API calls can be made
                            single_check_box_compare(nested_dict, temp_dict, van_ac_sv_data, list_in_use)
                            break
        q2.task_done()

# iterates over number of threads declared for Queue 1
for i in range(number_of_threads_q1):
    worker = threading.Thread(target=execute_queue1, args=(q1,))  # executes function in Queue, passes parsed XML (JSON)
    worker.daemon = True
    worker.start()

# iterates over number of threads declared for Queue 2
for i in range(number_of_threads_q2):
    worker = threading.Thread(target = execute_queue2, args=(q2, ))  # executes function in Queue, passes in tuple
    worker.daemon = True
    worker.start()

# MAIN BODY:
# Creates data frame
df = create_data_frame()

# Checks to see if user would like to update user information for all  activist codes/survey responses
if all_bool == 1:
    for i in range(NUM_ACTIVIST_CODES):
        q1.put((loaded_doc, i))  # if so, puts original parsed data in first Queue, threading and Queue becomes nested

# if the user does not want to update based on all activist codes, only uses Queue 2 and threading is not nested
else:
    # Variables holds JSON data, data is eventually passed to POST request of second API call
    van_ac_sv_data = which_list_ac_sv(list_in_use)

    # Breaks down nested dictionary from XML data into useful information
    for k, v in loaded_doc.items():
        for k1, v1 in v.items():
            for k2, v2 in v1.items():
                for i in v2:  # When lists of dictionaries is reached, outputs each one to second Queue
                    q2.put((i, van_ac_sv_data, list_in_use))

    # Tests to see if second Queue is finished
    q2.join()
    # If Queue is empty, completed data frame is printed to CSV file
    print_data_frame_to_csv(name_of_list_in_use)

# Tests to see if first Queue is finished, if Queue 1 is not used, test will pass immediately
q1.join()

input("\nThe program has completed, press 'enter' to quit: ")