# Automating_All_Users Program Overview
The program starts out by declaring numerous variables related to BSD’s API call, and VAN’s API calls. These include API usernames, secrets, and various element that allow the URL to be built. In the case of BSD’s URL, It dynamically adds in a parameter, the signup form ID, which is why the program requires input. Two VAN API will be called, with both using POST requests. The second API requires a URL that has a VAN ID in it, thus there is a function that is called to dynamically add this, and this does not require user input. BSD’s API’s use HMAC authentication and VAN’s use general authentication, though it is sent via a URL that uses HTTPS encryption.

A PANDAS DataFrame is also created so that the program can output a log of everyone affected to a CSV file

The main part of the program begins when the BSD API is called, and XML data is then returned and read, and parsed into JSON using the yahoo standard. 

The resulting JSON is nested, so to get at a usable dictionary, a series of ‘for’ statements is implemented. This will result in a series of dictionaries that are in a list. The program will deal with each one by iterating through the list.

At this point, a previously declared queue of maxsize 2000 is referenced, and is variable that defines the number of threads (this was set to 4, though VAN has cleared the program to go up to 10 - ONLY do this if the computer being used is sufficiently powerful, such that it is 64 bit, quad-core, and each core is running at least above 2 ghz). As the list of dictionaries is iterated through, it puts each each dictionary in a queue. 

### Everything beyond this point, uses threading to run concurrently:

A function is then called that checks to see how many fields have been filled out for each person whose key corresponds to certain text and whose value is not blank, and this number is assigned to a variable. The program then proceeds to look for certain keys for each person (first name, last name, zip code, phone number, and email) whose value is not blank, and it adds these pairs to a temporary dictionary. Sometimes the name of the keys are changed to match the style that VAN uses (firstname becomes firstName), though the values can also change (2102966021 becomes 1-210-296-6021). This process ends when the amount of values in the temporary dictionary equal the variable returned by the previously mentioned function. This allows each user to have a different amount of fields filled out and the program can know when to iterate to the next user.

The program then continues and calls a function that passes in the temporary dictionary, to both call the first API, to find or create the person in VAN’s My Campaign, and then calls the second API, to update their activist code and survey response status. After calling the first API, it reads the response (which includes a VAN ID) and dynamically assigns this ID to correctly make the URL for the second API. It then uses a POST request to update the activist code and survey response status of the individual. Included in the POST request is JSON data that is formatted to include the necessary activist code and survey response information. The temporary dictionary is then passed to another function that appends to the DataFrame.

Once the queue is empty, ‘q.join()’ is satisfied and the program can read the subsequent lines, which is to print the DataFrame. This is the end of the program. 
