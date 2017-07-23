#! usr/bin/python
""" 
Copyright 2017 Sam Suri, all rights reserved. Only use with permission. Contact: samsuri100@gmail.com, (210)296-6021

version 1.5
"""

import hmac, hashlib, time, json, requests
import threading
import urllib.request
from queue import Queue
from pandas import DataFrame
from json import dumps, loads
from xmljson import yahoo as yh
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import fromstring

#BSD Call and Declarations:
api_secret = "[enter BSD api_secret here]"  # API secret provided by BSD for user Sam Suri
api_ts = int(time.time())  # API call uses HMAC authentication that incorporates time
api_id = "[enter BSD api id here]"  # API ID provided by BSD for user Sam Suri

api_baseCall = "/page/api/signup/get_signups_by_form_id"  # API Call to get list of sign ups based on form ID
signup_form_id = str(input("Please enter the signup form ID: "))  # prompts the user for input of form ID
# Creates parameters for API call, incorporates user ID, time created, and form ID
api_param = "api_ver=2&api_id=" + api_id + "&api_ts=" + (str(api_ts)) + "&signup_form_id=" + str(signup_form_id)

# Creates string to pass into with HMAC authentication
signing_string = api_id + '\n' + str(api_ts) + '\n' + api_baseCall + '\n' + api_param
# Creates HMAC authentication, uses API secret, 'signing_string'
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
van_base_url = 'https://api.securevan.com/v4'  # Base URL for all VAN API calls
van_find_url = '/people/FindOrCreate'  # first VAN API call being called by program, uses POST request
van_total_find_url = van_base_url + van_find_url
name_of_list_in_use = 'cmi_list'  # will be used in title of CSV file
# JSON data that will be included in post request to apply AC/SV to users
van_ac_sv_data = {"resultCodeId": None, "responses": [{"activistCodeId": ["enter code ID here"], "action": "Apply", "type": "ActivistCode"},
                {"surveyQuestionId": ["enter survey ID here"], "surveyResponseId": ["enter response ID here"], "type": "SurveyResponse"}]}

# Function dynamically inserts VAN ID into second VAN API call
def van_total_ac_sv_url(indiv_id):
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

# Function creates initial data frame using PANDAS library and creates columns
def create_data_frame():
    columns = ['First Name', 'Last Name', 'Phone Number', 'Zip Code', 'Email']
    df = DataFrame(columns=columns)
    return df  # returns data frame to a variable

# Function appends to existing dataframe
def append_csv_row(dictionary):  # looks for keys and inserts values into data frame
    df.loc[len(df)] = [dictionary['firstName'],
                        dictionary['lastName'],
                        dictionary['phones'][0]['phoneNumber'],
                        dictionary['addresses'][0]['zipOrPostalCode'],
                        dictionary['emails'][0]['email']
                       ]

# Function prints data frame to csv file whose title dynamically includes current date
def print_data_frame_to_csv():
    csv_name = 'All Contacts Affected on ' + str(time.strftime('%d-%m-%Y') + ' for ' + name_of_list_in_use) + '.csv'
    df.to_csv(csv_name, index = False)  # index is set to false as programs like Excel make this redundant

# Function finds or creates individual in VAN - My Campaign
def update_indiv(temp_dict):
    # checks to see if user exists or not, creates user if they don't exist
    van_post = requests.post(van_total_find_url, json=temp_dict, auth=(van_app_name, """van_secret"""))
    for k, v in loads(van_post.text).items():  # reads response and coverts to tuple
        if k == 'vanId':
            vanid = v  # reads keys to find van ID
            # calls second VAN API call, updates user with appropriate AC/SV
            requests.post(van_total_ac_sv_url(vanid), json=van_ac_sv_data, auth=(van_app_name, """van_secret"""))
            # appends information on user to CSV file
            append_csv_row(temp_dict, df)
            return

#Queue and threading variables and declarations
q = Queue(maxsize = 2000)  # declares Queue of maxsize 2000, max in Queue is realistically around 1000
number_of_threads = 4  # threads are limited to 4 due to processing constraints of current computer, could go up to 10

# Function passes in each object in queue, each object is a dictionary
def execute_queue(q):
    while True:
        i = q.get()  # assigns passed in dictionary to i
        temp_dict = {}
        # finds out how many fields each person has, and assigns them to variable, allows program to know when to move on to new dictionary
        temp_dict_length = indiv_dict_length(i.items())
        if temp_dict_length >= 3:  # ensures that each person at least three fields, any less and VAN can't match user
            for k3, v3 in i.items():  # breaks dictionary into tuple
                if v3 != {}:  # makes sure that only answered fields are included
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
                    # makes sure that all filled out fields have been added to temp_dict
                    if (len(temp_dict) == temp_dict_length):
                            # allows single dictionary to proceed so that API call can be made
                            update_indiv(temp_dict)
                            break
        q.task_done()

# iterates over number of threads declared
for i in range(number_of_threads):
    worker = threading.Thread(target = execute_queue, args=(q,))  # executes function in Queue, passes in dictionary
    worker.daemon = True
    worker.start()

# MAIN BODY:
# Creates data frame
df = create_data_frame()

# Waits for input so that the function does not run completely just by being clicked
input("The program will now run and match all individuals \nin My Campaign, press enter to proceed: ")

for k, v in loaded_doc.items():
    for k1, v1 in v.items():
        for k2, v2 in v1.items():
            for i in v2:  # When lists of dictionaries is reached, outputs each one to Queue
                q.put(i)

# Tests to see if Queue is finished
q.join()
# If Queue is empty, completed data frame is printed to CSV file
print_data_frame_to_csv()