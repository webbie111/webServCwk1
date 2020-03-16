import requests, json
from operator import itemgetter, attrgetter
from prettytable import PrettyTable

# Client File for interacting with the API. Consists of two while loops which use user input
# to then call functions which make the Http requests to the API.

MY_URL = 'http://127.0.0.1:8000/cwk1Application/'

################################################################################
# Function for registering a new user
def register(username, email, password):
    registerData = {"username": username, "email": email, "password": password}
    payload = json.dumps(registerData)

    res = requests.post(url = MY_URL + 'register', data = payload)

    if res.status_code == 200:
        print ('Registration was successful.')

    else:
        print ('There was an error: ' + res.reason)

################################################################################
# This function is for logging the user in
def login(username, password):
    loginData = {"username": username, "password": password}
    payload = json.dumps(loginData)

    res = requests.post(url = MY_URL + 'login', data = payload)

    if (res.status_code == 200):
        loginResData = json.loads(res.text)
        userToken = str(loginResData['token'])
        print ('Login successful.')
        return userToken
    else:
        print ('There was an error: ' + res.reason)
        return ""

################################################################################
# Function for getting and printing all of the Modules and who teaches them.
def listModules():
    res = requests.get(url = MY_URL + 'list')

    if (res.status_code == 200):
        json_data = json.loads(res.text)

        tList = PrettyTable(['Code', 'Name', 'Year', 'Semester', 'Taught by'])
        for item in json_data:
            ele = json_data[str(item)]
            teachers = ele['taught_by']
            teachersJoin = ', '.join(teachers)

            tList.add_row([ele['module_code'], ele['module_name'], ele['year'],
                                ele['semester'], teachersJoin])

        print (tList)

    else:
        print ("There was an error: " + res.reason)

################################################################################
# This function gets and prints the average rating of each professor.
def viewAllRatings():
    res = requests.get(url = MY_URL + 'view')

    if res.status_code == 200:
        json_data = json.loads(res.text)
        tView = PrettyTable(['Professor', 'Average Rating'])
        for k, v in json_data.items():
            tView.add_row([k, v])

        print (tView)

    else:
        print ('There was an error: ' + res.reason)

################################################################################
# Gets and prints the results for a professor's average rating.
def getAverageRating(gProfCode, gModuleCode):
    res = requests.get(url = MY_URL + 'average/?p=' + gProfCode + '&m=' + gModuleCode)

    if res.status_code == 200:
        json_data = json.loads(res.text)

        print("The average rating of " + json_data['prof_name'] + " (" + gProfCode +
                ") in module " + json_data['module_name'] + " (" + gModuleCode + ") is " +
                str(json_data['rating']) + "/5")

    else:
        print ('There was an error: ' + res.reason)

################################################################################
# This function creates a json object of the user's rating and sends it to the server
# for the server to save on the database
def rateProfessor(prof_code, module_code, year, semester, rating, authHeader):
    if len(authHeader['Authorization']) < 7:
        print ('You need to log in before you can rate professors.')

    else:
        theDict = {}
        theDict['prof_code'] = prof_code
        theDict['module_code'] = module_code
        theDict['year'] = year
        theDict['semester'] = semester
        theDict['rating'] = rating

        payload = json.dumps(theDict)

        res = requests.post(url = MY_URL + 'rate', data = payload, headers = authHeader)

        if res.status_code == 200:
            print ('Professor rated successfully.')

        else:
            print ('There was an error: ' + res.text)

################################################################################
# This is the second control loop where the user can interact with the query functions in
# the API
def secondLoop(firstChoices, authToken):
    # Create the Authorization header for the rate professor function
    authHeader = {'Authorization': 'Token ' + authToken}

    tFChoices = PrettyTable(['Command', 'Arguments', 'Function'])
    tFChoices.add_row(['list', 'None', 'View a list of all module instances and the professor(s) teaching them'])
    tFChoices.add_row(['view', 'None', 'View the ratings of all professors.'])
    tFChoices.add_row(['average', '<professor_id> <module_code>', 'View the average rating of a certain professor in a certain module'])
    tFChoices.add_row(['rate', '<professor_id> <module_code> <year> <semester> <rating>', 'Rate a certain professor in a certain module instance'])
    tFChoices.add_row(['help', 'None', 'Displays the choices again'])
    tFChoices.add_row(['logout', 'None', 'Attempts to log you out'])
    tFChoices.add_row(['back', 'None', 'Go back to the previous menu'])
    print (tFChoices)

    secondChoice = ''
    while secondChoice != 'quit' or 'back' or 'logout':

        secondChoice = input("\nEnter a command and press enter.\n")
        inputList = list(secondChoice.split(" "))

        if secondChoice == 'list':
            listModules()
        elif secondChoice == 'view':
            viewAllRatings()
        elif inputList[0] == 'average':
            if len(inputList) == 3:
                print (inputList[1], inputList[2])
                getAverageRating(inputList[1], inputList[2])
            else:
                print ('Correct syntax is: average <professor_id> <module_code>')
        elif inputList[0] == 'rate':
            if len(inputList) == 6:
                print (authHeader['Authorization'])
                rateProfessor(inputList[1], inputList[2], inputList[3], inputList[4], inputList[5], authHeader)
            else:
                print ('Correct syntax is: rate <professor_id> <module_code> <year> <semester> <rating>')
        elif secondChoice == 'help':
            print (tFChoices)
        elif secondChoice == 'logout':
            print ('Logging out...')
            authToken = ""
            print (firstChoices)
            break
        elif secondChoice == 'back':
            print (firstChoices)
            break
        else:
            print ('Invalid Command. Your choices are:')
            print (tFChoices)

################################################################################
# The first control loop where the user can do things like register or login.
def firstLoop():
    tSChoices = PrettyTable(['Command', 'Arguments', 'Function'])
    tSChoices.add_row(['register', '<username> <email> <password>', 'Create an account with the specified details'])
    tSChoices.add_row(['login', '<username> <password>', 'Attempts to log in with the supplied credentials'])
    tSChoices.add_row(['guest', 'None', 'Continue as a guest, but you won\'t be able to rate professors'])
    tSChoices.add_row(['help', 'None', 'Displays the choices again'])
    tSChoices.add_row(['quit', 'None', 'Quits this program'])
    print (tSChoices)

    firstChoice = ''
    while firstChoice != 'quit':

        firstChoice = input("\nEnter a command and press enter.\n")
        inputList = list(firstChoice.split(" "))

        if inputList[0] == 'register':
            if len(inputList) == 4:
                register(inputList[1], inputList[2], inputList[3])
            else:
                print ('Correct syntax is: register <username> <email> <password>')

        elif inputList[0] == 'login':
            if len(inputList) == 3:
                authToken = (login(inputList[1], inputList[2]))
                if authToken is not "":
                    secondLoop(tSChoices, authToken)
                else:
                    print ('Login Unsuccesful: Token not accquired porperly')
            else:
                print ('Correct syntax is: login <username> <password>')
        elif firstChoice == 'guest':
            secondLoop(tSChoices, "")
        elif firstChoice == 'help':
            print (tSChoices)
        elif firstChoice =='quit':
            print ('Quitting...')
            break
        else:
            print ('Invalid Command. Your choices are:')
            print (tSChoices)


# Run the first loop
firstLoop()
