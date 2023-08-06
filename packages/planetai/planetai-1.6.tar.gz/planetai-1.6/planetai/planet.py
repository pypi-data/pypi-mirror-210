import random
import webbrowser
import pandas as pd
import matplotlib.pyplot as plt

class Jupiter:

    def __init__(self):
        exit = True

    def test():
        print("hi buddy. looks like we got it!")
        
    def start():
        exit = True
        while exit == True:
            task = input("Hi! My name is Jupiter. How can I help you today? ")
            print("Your Command: " + task)
            if task == 'get coordinates':
                Jupiter.getcoordinates()
            elif task == 'help':
                print("Here is a list of valid commands:  \n get coordinates = Generate random target coordinates for a remote viewing session \n generate target = Generates a random target for a remote viewing session \n license = View licensing \n copyright = View copyright \n credits = View credits \n exit = Exits program")
            elif task == 'generate target':
                Jupiter.generatetarget()
            elif task == 'license':
                Jupiter.license()
            elif task == 'copyright':
                Jupiter.copyright()
            elif task == 'credits':
                Jupiter.credits()
            elif task == 'exit':
                exit = False
            else:
                print("Invalid Command. Type 'help' to see a list of commands")  

    def getcoordinates():
        coordinates = ''
        i = 0

        while i < 8:
            coord = random.randint(0,9)
            coordinates += str(coord)
            i += 1

        coordinates = coordinates[:4] + '/' + coordinates[4:]
        print('Your Target Coordinates are: {}'.format(str(coordinates)))

    def generatetarget():
        targetnumber = random.randint(1,238)
        url = "https://farsight.org/sponsors/PoolA/t{}.html".format(targetnumber)
        webbrowser.open(url)

    def copyright():
        print("""Copyright (c) 2023 Aziz Brown

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files 'planetAI', to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.""")

    def license():
        print('MIT License')

    def credits():
        print('Author: Aziz Brown \n https://kuwindacorp.com/ \n github: https://github.com/sageofnamek')

class Mercury:

    def start():
        target = input("What asset we creating a forecast for? ")
        startdate = input("Enter the start date of the forecast (format: MM/DD/YYYY): ")
        enddate = input("Enter the end date of the forecast (format: MM/DD/YYYY): ")
        print("We are creating a forecast for {} between {} - {}".format(target, startdate, enddate))
        correctcheck = input("Is the above statement correct? Type 'Y' for yes or 'N' for no: ")
        
        while correctcheck.lower() not in ('y','n'):
            print("Invalid input. Please type 'y' or 'n'")
            correctcheck = input("Is the above statemen correct? Type 'Y' for yes or 'N' for no: ")
        if correctcheck.lower() == 'y':
            print("Great! Please follow the prompts to input your session data.")
            Mercury.viewerinput()
        elif correctcheck.lower() == 'n':
            print("Let's try again....")
            Mercury.start()

    def is_ten(x):
        if x <= 1:
            return False
        for i in range(2, x):
            if x % i == 0:
                return False
        return True

    def targetinput():
        basetargetnumber = 0
        basetargetnumber = input("Please enter the base target number: ")
        ninegroup = [1,2,3,4,7,8,9,16,18,22,23,24,25,26,27,28,34,36,37,40,42,46,47,48,50,51]
        tengroup = [5,6,10,11,12,13,14,15,17,19,20,21,29,30,31,32,33,35,39,41,43,44,45,49]
        elevengroup = [38]
        targetelements = 0
        if int(basetargetnumber) in ninegroup:
            print ("2 elements in this target")
            targetelements = 9
        elif int(basetargetnumber) in tengroup:
            print("1 element in this target")
            targetelements = 10
        elif int(basetargetnumber) in elevengroup:
            print("0 elements in this target")
            targetelements = 11
        print(targetelements)
        return targetelements
    
    def viewerinput():
        viewerdata = {}
        numberofviewers = int(input("How many viewers are in this project? "))
        probedata = []
        viewerlistelements = {}
        viewerlistelements2 = {}
        viewerlistelements3 = {}
        targetlistelements = {}

        #temperature calculator code
        numpostemps = 0
        numnegtemps = 0
        sumpostemps = 0
        sumnegtemps = 0
        maxval = max(range(numberofviewers))

        #index calculator code

        indexelement = 0
        indexlist = []
        indexavg = 0
        indexcof = 0
        indexminus2 = 0
        indexminus3 = 0
        i = 0
        viewerlist = []


        for i in range(numberofviewers):
            viewername = input("Enter viewer name: ")
            viewerlist.append(viewername)
            viewerelements = input("For {}: Please enter the number of elements over and above the base surface:".format(viewername))
            viewerdata[viewername] = viewerelements
            targetelements = Mercury.targetinput()
            probedata = Mercury.tempinput()
            viewerlistelements[viewername] = viewerelements
            viewerlistelements2[viewername] = viewerelements
            viewerlistelements3[viewername] = viewerelements
            targetlistelements[viewername] = targetelements
            for num in probedata:
                if num > 0:
                    sumpostemps += num
                    numpostemps += 1
                elif num < 0:
                    sumnegtemps += num
                    numnegtemps += 1   
            if i == maxval:
                print("ʕっ•ᴥ•ʔっ Aggregate Temperature Probe Analysis (◕ᴥ◕ʋ)")
                print('Number of positive temperatures: +{} // Number of negative temperatures: {}\nSum value of positive temperatures: +{} // Sum value of negative temperatures: {} '.
                format(str(numpostemps),str(numnegtemps),str(sumpostemps), str(sumnegtemps)))

            i += 1  
        print(viewerdata)
        #print(numberofviewers)
        #Mercury.indexcalculator(numberofviewers, viewerlistelements, targetelements, viewerlistelements2, viewerlistelements3)

        #index calculator code

        int_viewerlistelements = {}
        int_viewerlistelements2 = {}
        int_viewerlistelements3 = {}

        for key in viewerlistelements:
            int_viewerlistelements[key] = int(viewerlistelements[key])
        for key in viewerlistelements2:
            int_viewerlistelements2[key] = int(viewerlistelements2[key])
        for key in viewerlistelements3:
            int_viewerlistelements3[key] = int(viewerlistelements3[key])
        
        resultdict = {}
        resultdict2 = {}
        resultdict3 = {}

        for key in viewerlistelements:
            resultdict[key] = round(int_viewerlistelements[key] / targetlistelements[key], 3)
        for key in viewerlistelements2:
            resultdict2[key] = round((int_viewerlistelements2[key] - 2) / targetlistelements[key], 3)
            if resultdict2[key] < 0:
                resultdict2[key] = int(0)
        for key in viewerlistelements:
            resultdict3[key] = round((int_viewerlistelements3[key] - 3) / targetlistelements[key], 3)
            if resultdict3[key] < 0:
                resultdict3[key] = int(0)
        print("Here are your index values for each viewer from least to most conservative:")
        print(resultdict)
        print(resultdict2)
        print(resultdict3)

        #Calculate averages for indexes

        avglist = []

        viewersum = sum(resultdict[key] for key in viewerlist)
        avg = round(viewersum / numberofviewers, 3)
        avglist.append(avg)

        viewersum = sum(resultdict2[key] for key in viewerlist)
        avg = round(viewersum / numberofviewers, 3)
        avglist.append(avg)

        viewersum = sum(resultdict3[key] for key in viewerlist)
        avg = round(viewersum / numberofviewers, 3)
        avglist.append(avg)

        print('Averages:')
        print(avglist)

        return(viewerdata, probedata, numberofviewers, viewerlistelements, viewerlistelements2, viewerlistelements3, targetlistelements)
    
    def tempinput():
        temperatureprobes = {}
        templist = []
        for i in range(1, 9):
            segmentvalue = input("input value for segment {}/8: ".format(i))
            temperatureprobes[i] = segmentvalue
            i += 1
        
        #df = pd.DataFrame.from_dict(data, orient='index', columns=['quantity'])
        temperatureprobes = {key: int(value) for key, value in temperatureprobes.items()}
        df = pd.DataFrame.from_dict(temperatureprobes, orient='index', columns=['quantity'])
        df.plot(kind='bar', legend=None)
        plt.xlabel('8 segments')
        plt.ylabel('hot or cold')
        plt.title('Temperature Probes')
        #plt.show()
        templist = list(temperatureprobes.values())
        return(templist)