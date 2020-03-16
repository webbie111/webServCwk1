from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics
from .models import Module, Professor, ModuleInstance, Rating
import json
from decimal import *
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, authenticate, logout
from rest_framework.response import Response
from rest_framework.decorators import api_view

# File for the API views for the client to interact with

################################################################################
# View for registering a user.
@csrf_exempt
@api_view(['POST'])
def register(request):
    regData = json.loads(request.body)
    if regData['username'] is "" or regData['email'] is "" or regData['password'] is "":
        return Response(status = 400, data = "Entered details are not valid.")
    else:
        regUsername = regData['username']
        regEmail = regData['email']
        regPwd = regData['password']
        user = User.objects.create_user(regUsername, regEmail, regPwd)
        return Response(status = 200)

################################################################################
# View for logging a user in.
@csrf_exempt
@api_view(['POST'])
def loginUser(request):
    loginData = json.loads(request.body)
    loginUsername = loginData['username']
    loginPwd = loginData['password']
    user = authenticate(username = loginUsername, password = loginPwd)
    if user is not None:
        if user.is_active:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            print (token)
            print (user)
            return Response({'token': token.key}, status = 200)
        else:
            return Response("User is disabled.")
    else:
        return Response("User doesn't exist.")

################################################################################
# View for listing all the modules and the professors who teach them.
@api_view(['GET'])
def listModInstances(request):
    iteration = 1
    bigDict = {}
    # Get all the module instance objects, ordered appropriately
    lOrdered = ModuleInstance.objects.all().order_by('module_id__module_code', 'year', 'semester')

    # Loop through the objects so that they can be added to the output.
    for x in lOrdered:
        # myDict stores each module instance's information.
        myDict = {"module_code": x.module_id.module_code, "module_name": x.module_id.module_name, "year": x.year,
        "semester": x.semester}

        teachers = x.taught_by.all()
        teacherList = []
        numTeachers = x.taught_by.all().count()

        for teacher in teachers:
            teacherList.append(teacher.prof_code + ' ' + teacher.prof_name)

        myDict['taught_by'] = teacherList
        # add myDict to bigDict
        bigDict[str(iteration)] = myDict
        iteration += 1

    json_data = json.dumps(bigDict)
    return HttpResponse(json_data)

################################################################################
# View for getting every professor's average rating.
@api_view(['GET'])
def viewAllRatings(request):
    myDict = {}
    numOccurrences = {}
    # get all the Rating objects, then loop through them
    vOrdered = Rating.objects.all().order_by('professor__prof_name')
    for y in vOrdered:

        profName = y.professor.prof_name
        rating = y.rating

        # If we haven't seen the professor yet give them their initial rating.
        if profName not in myDict.keys():
            myDict[profName] = rating
            numOccurrences[profName] = 1
        # If we have seen the prof before then simply update their exisitng rating
        else:
            myDict[profName] = rating + myDict[profName]
            numOccurrences[profName] = numOccurrences[profName] + 1

    for professor in myDict:
        # num is the number of times the professor has been rated
        num = numOccurrences[professor]
        aveRating = Decimal(myDict[professor] / num).quantize(Decimal('1.'), rounding = ROUND_HALF_UP)
        myDict[professor] = int(aveRating)

    json_data = json.dumps(myDict)
    return HttpResponse(json_data)

################################################################################
# View for getting a professor's average rating in a specific module
@api_view(['GET'])
def averageRating(request):
    # get the professor and module code from the client
    profCode =  request.GET.get('p' '')
    moduleCode = request.GET.get('m' '')

    # get the relevant objects
    prof = get_object_or_404(Professor, prof_code = profCode)
    module = get_object_or_404(Module, module_code = moduleCode)
    ratings = Rating.objects.filter(professor__prof_code = profCode,
                            module_instance__module_id__module_code = moduleCode)

    # loop through the ratings to sum and then average them
    total = 0
    for rating in ratings:
        total = total + rating.rating
    average = total / len(ratings)
    aveRating = int(Decimal(total/len(ratings)).quantize(Decimal('1.'), rounding = ROUND_HALF_UP))

    data = {'prof_name' : prof.prof_name, "module_name": module.module_name, "rating": aveRating}

    json_data = json.dumps(data)
    return HttpResponse(json_data)

################################################################################
# View for rating a professor specified by the client
@csrf_exempt
@api_view(['POST'])
def rateProfessor(request):
    reqData = json.loads(request.body)
    if reqData['rating'] not in ['1', '2', '3', '4', '5']:
        return Response('Your rating needs to be a whole integer between 1 and 5', status=400)

    # Try and retrieve the relevant objects from the client's input, throw 404 resposne otherwise
    module = get_object_or_404(Module, module_code = reqData['module_code'])
    professor = get_object_or_404(Professor, prof_code = reqData['prof_code'])
    module_instance = get_object_or_404(ModuleInstance, module_id = module,
                                    year = reqData['year'], semester = reqData['semester'],
                                    taught_by = professor)

    # Create and saves the Rating object to the database
    Rating.objects.create(rating = reqData['rating'], professor = professor,
                            module_instance = module_instance)

    return Response(status = 200)

################################################################################
