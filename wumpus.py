# Speech Technology Final Project
# Speech interface to a text-based adventure game
# Iris Hartl (ihartl@kth.se)
# Benjamin Coors (coors@kth.se)
# Fabian Schilling (fabsch@kth.se)

############################################################################### MODULES #######

import random
import os
import subprocess
import signal
import speech_recognition as sr

############################################################################### CLASSES #######

class Room():
    """ represents a room in a labyrinth """

    def __init__(self, roomNr): 
        """ creates a room object.
    CHANGES roomNr, bats, pit, wumpus, neighbours. """
        self.__roomNr = roomNr
        self.__pit = False
        self.__bats = False
        self.__wumpus = False
        self.__neighbours = {}

    def __str__(self):
        """ RETURNS roomNr as a string. """
        rep = str(self.__roomNr)
        return rep

    def addPit(self):
        """ CHANGES pit. """
        self.__pit = True

    def addBats(self):
        """ CHANGES bats. """
        self.__bats = True

    def removeBats(self):
        """ CHANGES bats. """
        self.__bats = False

    def addWumpus(self):
        """ CHANGES wumpus. """
        self.__wumpus = True

    def removeWumpus(self):
        """ CHANGES wumpus """
        self.__wumpus = False

    def addNeighbour(self, direction, room):
        """ 'connects' a room to another room.
    CHANGES neighbours. """
        self.__neighbours[direction] = room

    def getNeighbour(self, direction):
        """ RETURNS the room object in the given direction. """
        return self.__neighbours[direction]

    def getAllNeighbours(self):
        """ RETURNS all neighbouring rooms in a list. """
        return self.__neighbours.values()

    def showInfo(self):
        """ outputs information about the room and its neighbours. """
        output("\nYou are in room number " + str(self.__roomNr) + ". ")
                #"From here, you can get to the following rooms:"
                #"East: " + str(self.__neighbours["E"]) + ". West: " + str(self.__neighbours["W"]) +
                #". North: " + str(self.__neighbours["N"]) + ". South: " + str(self.__neighbours["S"]) + ".")
        for direction in self.__neighbours:
            self.senseTraps(direction)

    def senseTraps(self, direction):
        """ outputs information about traps in the neighbouring rooms. """
        neighbour = self.__neighbours[direction]
        if neighbour.__pit:
            output("You feel a light draft.")
        elif neighbour.__bats:
            output("You hear bats.")
        elif neighbour.__wumpus:
            output("You smell Wumpus' foul breath!")

    def trapCheck(self):
        """ checks if the room contains traps.
    RETURNS True or False. """
        return self.__pit or self.__bats or self.__wumpus

    def getTrap(self):
        """ RETURNS the room's own trap as a string (an empty string if there are no traps). """
        if self.__pit:
            return "pit"
        elif self.__bats:
            return "bats"
        elif self.__wumpus:
            return "wumpus"
        else:
            return ""


class Player():
    """ represents the user and their weapon. """

    def __init__(self):
        """ creates a Player-object.
    CHANGES arrows. """
        self.__arrows = 5

    def __str__(self):
        """ outputs information about the player.
    RETURNS arrows as a string. """
        if self.__arrows == 1:
            rep = "You have " + str(self.__arrows) + " arrow left."
        else:
            rep = "You have " + str(self.__arrows) + " arrows left."
        return rep

    def useArrow(self):
        """ reduces arrows by 1 everytime it is called.
    CHANGES arrows. """
        self.__arrows -= 1

    def getArrows(self):
        """ RETURNS the number of arrows left. """
        return self.__arrows


class Game():
    """ represents a full game. Calls all the necessary methods in the right order upon instantiation. """

    def __init__(self, firstTime):
        """ creates a Game-object.
    CHANGES running. """
        self.__running = True
        self.__firstTime = firstTime
        self.__firstArrow = True
        self.__directionCounter = 0;
        self.__createRooms()
        self.__difficulty = self.requestDifficulty()
        self.__addTraps()
        self.__createMap()
        self.__chooseStartingpoint()
        self.__player = Player()
    
    def __createRooms(self):
        """ creates a list of Room-objects.
    CHANGES listOfRooms. """
        self.__listOfRooms = []
        for i in range(20):
            self.__listOfRooms.append(Room(i + 1))

    def __addTraps(self):
        """ distributes traps over the rooms.
    If difficulty = hard: CHANGES self.__wumpusRoom. """
        random.shuffle(self.__listOfRooms)
        if self.__difficulty == "E":
            for room in self.__listOfRooms[0:3]:
                room.addPit()
            for room in self.__listOfRooms[3:8]:
                room.addBats()
            random.choice(self.__listOfRooms[8:]).addWumpus()

        elif self.__difficulty == "D":
            for room in self.__listOfRooms[0:5]:
                room.addPit()
            for room in self.__listOfRooms[5:12]:
                room.addBats()
            random.choice(self.__listOfRooms[12:]).addWumpus()
            for room in self.__listOfRooms:
                if room.getTrap() == "wumpus":
                    self.__wumpusRoom = room
                    
        else:
            for room in self.__listOfRooms[0:5]:
                room.addPit()
            for room in self.__listOfRooms[5:12]:
                room.addBats()
            random.choice(self.__listOfRooms[12:]).addWumpus()

    def __createMap(self):
        """ shuffles the list of Room-objects and 'connects' the rooms east to west.
    shuffles the list again and 'connects' the rooms north to south. """
        random.shuffle(self.__listOfRooms)
        self.__listOfRooms[0].addNeighbour("E", self.__listOfRooms[19])
        self.__listOfRooms[0].addNeighbour("W", self.__listOfRooms[1])
        self.__listOfRooms[19].addNeighbour("E", self.__listOfRooms[18])
        self.__listOfRooms[19].addNeighbour("W", self.__listOfRooms[0])
        
        for i in range(1, 19):
            room = self.__listOfRooms[i]
            room.addNeighbour("E", self.__listOfRooms[i - 1])
            room.addNeighbour("W", self.__listOfRooms[i + 1])

        random.shuffle(self.__listOfRooms)
        self.__listOfRooms[0].addNeighbour("N", self.__listOfRooms[19])
        self.__listOfRooms[0].addNeighbour("S", self.__listOfRooms[1])
        self.__listOfRooms[19].addNeighbour("N", self.__listOfRooms[18])
        self.__listOfRooms[19].addNeighbour("S", self.__listOfRooms[0])
            
        for i in range(1, 19):
            room = self.__listOfRooms[i]
            room.addNeighbour("N", self.__listOfRooms[i - 1])
            room.addNeighbour("S", self.__listOfRooms[i + 1])

    def __chooseStartingpoint(self):
        """ randomly chooses a room in listOfRooms that becomes the startingpoint (the room cannot contain traps). """
        self.__currentRoom = random.choice(self.__listOfRooms)
        while self.__currentRoom.trapCheck():
            self.__currentRoom = random.choice(self.__listOfRooms)

    def requestDifficulty(self):
        """ lets the user choose a difficulty.
    CHANGES self.__difficulty. """
        return recognize("\nDo you want to play in easy, normal or hard mode?\n", ["E", "N", "D"])
        
    def moveWumpus(self):
        """ lets Wumpus move around the tunnels if difficulty = hard. Removes bats in Wumpus' room. """
        wumpusHasMoved = False
        self.__wumpusRoom.removeWumpus()
        for neighbour in self.__wumpusRoom.getAllNeighbours():
            if neighbour.getTrap() != "pit":
                self.__wumpusRoom = neighbour
                wumpusHasMoved = True
                break
        if not wumpusHasMoved: # This in case there are pits all around Wumpus
                self.__wumpusRoom = random.choice(self.__listOfRooms)
                while self.__wumpusRoom.getTrap == "pit":
                    self.__wumpusRoom = random.choice(self.__listOfRooms)
            
        self.__wumpusRoom.addWumpus()
        self.__wumpusRoom.removeBats()
        output("\nWumpus is moving through the tunnels...")

        if self.__wumpusRoom == self.__currentRoom:
            self.endGame("wumpus")

    def inputDirection(self, movementType):
        """ lets the user input a direction and shows fitting text. Handles errors.
    RETURNS E, W, N or S as a string. """
        

        if movementType == "move":
            if self.__directionCounter < 3 and self.__firstTime:
                prompt = "Where do you want to go? East, west, north or south?"
            else:
                prompt = "Where do you want to go?"
        elif movementType == "shoot1":
            if self.__directionCounter < 3 and self.__firstTime:
                prompt = "Which direction do you want to shoot in? East, west, north or south?"
            else:
                prompt = "Which direction do you want to shoot in?"
        elif movementType == "shoot2":
            if self.__directionCounter < 3 and self.__firstTime:
                prompt = "Which way should it fly? East, west, north or south?"
            else:
                prompt = "Which way should it fly?"

        self.__directionCounter += 1

        direction = recognize(prompt, ["E", "W", "N", "S", "H"])

        if direction == "H":
            helpNeeded = True

        while helpNeeded:
            if movementType == "move":
                output("You can move around the tunnels. \n"
                        "From where you are standing, you can walk East, West, North or South. \n")
            else:
                output("You can shoot an arrow to kill Wumpus. \n"
                        "From where you are standing, you can shoot East, West, North or South. \n")

            direction = recognize(prompt, ["E", "W", "N", "S", "H"])
            if direction != "H":
                helpNeeded = False

        return direction
    
    def move(self):
        """ lets the user move around the labyrinth.
    CHANGES currentRoom. """
        direction = self.inputDirection("move")
        self.__currentRoom = self.__currentRoom.getNeighbour(direction)

    def shootArrow(self):
        """ lets the user shoot an arrow. """
        if self.__firstArrow and self.__firstTime:
            output("Arrows can fly through at most 3 rooms and you can change their direction after\n"
                    "every room. But be careful not to accidentally shoot yourself,,\n")
            self.__firstArrow = False
        direction = self.inputDirection("shoot1")
        counter = 1
        arrowRoom = self.__currentRoom.getNeighbour(direction)
        while arrowRoom.getTrap() != "wumpus" and counter < 3 and arrowRoom != self.__currentRoom:
            if (3 - counter) == 1:
                output("\nThe arrow has power for " + str(3 - counter) + " more room.")
            else:
                output("\nThe arrow has power for " + str(3 - counter) + " more rooms.")
            counter += 1
            direction = self.inputDirection("shoot2")
            arrowRoom = arrowRoom.getNeighbour(direction)

        if arrowRoom == self.__currentRoom:
            self.endGame("suicide")
        elif arrowRoom.getTrap() == "wumpus":
            self.endGame()
        else:
            self.__player.useArrow()
            if self.__player.getArrows() == 0:
                self.endGame("noArrows")
            else:
                output("\n" + str(self.__player))

    def batAbduction(self):
        """ moves the user to a random room on the map.
    CHANGES currentRoom. """
        self.__currentRoom = random.choice(self.__listOfRooms)
        output("\nBats live in this room! You feel their wings touching your cheek and suddenly\n"
              "lose ground under your feet.\n"
              "After a short trip through the air, the bats drop you in room number "
              + str(self.__currentRoom) + ".")

    def endGame(self, trapType=""):
        """ ends the game and outputs a fitting text.
    CHANGES self.__running."""
        self.__running = False
        if trapType == "pit":
            output("\nThere is a bottomless pit in this room!\n"
                  "You are sucked into it in a powerful current of air.\n"
                  "As you fall into the darkness, you come to the realisation that\n"
                  "trespassing on KTH property to hunt monsters\n"
                  "might not have been such a great idea after all..."
                  "\nGAME OVER\n\n")

        elif trapType == "wumpus":
            output("\nWumpus is in this room!\n"
                  "You try to reach behind your back to grasp an arrow and shoot the monster, \n"
                  "but accidentally spill the contents of your quiver as you twist and bend.\n"
                  "The sound of the arrows clattering on the floor alerts Wumpus to your presence.\n"
                  "He looks pretty hungry..."
                  "\nGAME OVER\n\n")

        elif trapType == "suicide":
            output("\nCongratulations, you managed to shoot yourself with bow and arrow."
                    "\nGAME OVER\n\n")

        elif trapType == "noArrows":
            output("\nYou hear your last arrow hit a wall a couple of rooms away.\n"
                  "How are you going to defeat Wumpus now, with your bare hands?"
                    "\nGAME OVER\n\n")

        else:
            output("\nYour arrow found Wumpus! It doesn't seem to like him, judging from the way\n"
                  "it finds its path right to the monster's heart all on its own. Good riddance!\n"
                  "Now the only thing left to do is to get out of here!\nThat can't be too hard, right?..."
                    "\nYOU WON!!! Go you!\n\n")

    def runGame(self):
        """ lets the user interact with the program. """

        while self.__running:
            self.__currentRoom.showInfo()

            action = recognize("\nDo you want to move or shoot an arrow? ", ["M", "S", "H"])

            if action == "H":
                helpNeeded = True

            while helpNeeded:
                output("You can move around the tunnels. \n"
                        "From where you are standing, you can walk East, West, North or South. \n"
                        "But beware of traps!\n"
                        "If you hear bat wings flapping, then bats reside in one of the adjacent rooms.\n"
                        "When you step into their room, they will abduct you and drop you in a random room. ,, \n"
                        "A howling wind signals that a bottomless pit is in one of the neighbouring rooms. \n"
                        "Don't fall into it or you will die! \n"
                        "If you hear Wumpus growl, then be especially careful! \n"
                        "You can try to kill Wumpus by shooting an arrow. \n")
                action = recognize("\nDo you want to move or shoot an arrow? ", ["M", "S", "H"])
                if action != "H":
                    helpNeeded = False
                
            if action == "M":
                self.move()
                while self.__currentRoom.getTrap() == "bats":
                    self.batAbduction()

                trapType = self.__currentRoom.getTrap()        
                if trapType == "pit" or trapType == "wumpus":
                    self.endGame(trapType)
                            
            elif action == "S":
                self.shootArrow()

            if self.__running and self.__difficulty == "D":
                self.moveWumpus()
    
class TestGame():
    """ represents a test game without random elements. Calls all the necessary methods in the right order upon instantiation. """

    def __init__(self, firstTime):
        """ creates a TestGame-object.
    CHANGES running. """
        self.__running = True
        self.__firstTime = firstTime
        self.__firstArrow = True
        self.__directionCounter = 0;
        self.__createRooms()
        self.__difficulty = "E"
        self.__addTraps()
        self.__createMap()
        self.__chooseStartingpoint()
        self.__player = Player()
    
    def __createRooms(self):
        """ creates a list of Room-objects.
    CHANGES listOfRooms. """
        self.__listOfRooms = []
        for i in range(20):
            self.__listOfRooms.append(Room(i + 1))

    def __addTraps(self):
        """ distributes traps over the rooms. """
       
        for room in self.__listOfRooms[0:3]:
            room.addPit()
        for room in self.__listOfRooms[3:8]:
            room.addBats()
        self.__listOfRooms[8].addWumpus()

    def __createMap(self):
        """ 'connects' the rooms east to west.
    'connects' the rooms north to south. """
        self.__listOfRooms[0].addNeighbour("E", self.__listOfRooms[19])
        self.__listOfRooms[0].addNeighbour("W", self.__listOfRooms[1])
        self.__listOfRooms[19].addNeighbour("E", self.__listOfRooms[18])
        self.__listOfRooms[19].addNeighbour("W", self.__listOfRooms[0])
        
        for i in range(1, 19):
            room = self.__listOfRooms[i]
            room.addNeighbour("E", self.__listOfRooms[i - 1])
            room.addNeighbour("W", self.__listOfRooms[i + 1])

        self.__listOfRooms[0].addNeighbour("N", self.__listOfRooms[18])
        self.__listOfRooms[0].addNeighbour("S", self.__listOfRooms[2])
        self.__listOfRooms[19].addNeighbour("N", self.__listOfRooms[17])
        self.__listOfRooms[19].addNeighbour("S", self.__listOfRooms[1])
            
        for i in range(1, 18):
            room = self.__listOfRooms[i]
            room.addNeighbour("N", self.__listOfRooms[i - 2])
            room.addNeighbour("S", self.__listOfRooms[i + 2])

    def __chooseStartingpoint(self):
        """ sets the starting point to room 10 """
        self.__currentRoom = self.__listOfRooms[9]


    def inputDirection(self, movementType):
        """ lets the user input a direction and shows fitting text. Handles errors.
    RETURNS E, W, N or S as a string. """
        
        if movementType == "move":
            if self.__directionCounter < 3 and self.__firstTime:
                prompt = "Where do you want to go? East, west, north or south?"
            else:
                prompt = "Where do you want to go?"
            sound = "steps"
        elif movementType == "shoot1":
            if self.__directionCounter < 3 and self.__firstTime:
                prompt = "Which direction do you want to shoot in? East, west, north or south?"
            else:
                prompt = "Which direction do you want to shoot in?"
            sound = "arrow"
        elif movementType == "shoot2":
            if self.__directionCounter < 3 and self.__firstTime:
                prompt = "Which way should it fly? East, west, north or south?"
            else:
                prompt = "Which way should it fly?"
            sound = "arrow"

        self.__directionCounter += 1

        direction = recognize(prompt, ["E", "W", "N", "S", "H"])

        if direction == "H":
            helpNeeded = True

        while helpNeeded:
            if movementType == "move":
                output("You can move around the tunnels. \n"
                        "From where you are standing, you can walk East, West, North or South. \n")
            else:
                output("You can shoot an arrow to kill Wumpus. \n"
                        "From where you are standing, you can shoot East, West, North or South. \n")

            direction = recognize(prompt, ["E", "W", "N", "S", "H"])
            if direction != "H":
                helpNeeded = False

        play(sound)
        return direction
    
    def move(self):
        """ lets the user move around the labyrinth.
    CHANGES currentRoom. """
        direction = self.inputDirection("move")
        self.__currentRoom = self.__currentRoom.getNeighbour(direction)

    def shootArrow(self):
        """ lets the user shoot an arrow. """
        if self.__firstArrow and self.__firstTime:
            output("Arrows can fly through at most 3 rooms and you can change their direction after\n"
                    "every room. But be careful not to accidentally shoot yourself,,\n")
            self.__firstArrow = False
        direction = self.inputDirection("shoot1")
        counter = 1
        arrowRoom = self.__currentRoom.getNeighbour(direction)
        while arrowRoom.getTrap() != "wumpus" and counter < 3 and arrowRoom != self.__currentRoom:
            if (3 - counter) == 1:
                output("\nThe arrow has power for " + str(3 - counter) + " more room.")
            else:
                output("\nThe arrow has power for " + str(3 - counter) + " more rooms.")
            counter += 1
            direction = self.inputDirection("shoot2")
            arrowRoom = arrowRoom.getNeighbour(direction)

        if arrowRoom == self.__currentRoom:
            self.endGame("suicide")
        elif arrowRoom.getTrap() == "wumpus":
            self.endGame()
        else:
            self.__player.useArrow()
            if self.__player.getArrows() == 0:
                self.endGame("noArrows")
            else:
                output("\n" + str(self.__player))

    def batAbduction(self):
        """ moves the user to room 11.
    CHANGES currentRoom. """
        self.__currentRoom = self.__listOfRooms[10]
        output("\nBats live in this room! You feel their wings touching your cheek and suddenly\n"
              "lose ground under your feet.\n"
              "After a short trip through the air, the bats drop you in room nr. "
              + str(self.__currentRoom) + ".")

    def endGame(self, trapType=""):
        """ ends the game and outputs a fitting text.
    CHANGES self.__running."""
        self.__running = False
        if trapType == "pit":
            output("\nThere is a bottomless pit in this room!\n"
                  "You are sucked into it in a powerful current of air.\n"
                  "As you fall into the darkness, you come to the realisation that\n"
                  "trespassing on KTH property to hunt monsters\n"
                  "might not have been such a great idea after all..."
                    "\nGAME OVER\n\n")

        elif trapType == "wumpus":
            output("\nWumpus is in this room!\n"
                  "You try to reach behind your back to grasp an arrow and shoot the monster, \n"
                  "but accidentally spill the contents of your quiver as you twist and bend.\n"
                  "The sound of the arrows clattering on the floor alerts Wumpus to your presence.\n"
                  "He looks pretty hungry..."
                    "\nGAME OVER\n\n")

        elif trapType == "suicide":
            output("\nCongratulations, you managed to shoot yourself with bow and arrow."
                    "\nGAME OVER\n\n")

        elif trapType == "noArrows":
            output("\nYou hear your last arrow hit a wall a couple of rooms away.\n"
                  "How are you going to defeat Wumpus now, with your bare hands?"
                    "\nGAME OVER\n\n")

        else:
            output("\nYour arrow found Wumpus! It doesn't seem to like him, judging from the way\n"
                  "it finds its path right to the monster's heart all on its own. Good riddance!\n"
                  "Now the only thing left to do is to get out of here!\nThat can't be too hard, right?..."
                    "\nYOU WON!!! Go you!\n\n")

    def runGame(self):
        """ lets the user interact with the program. """

        while self.__running:
            self.__currentRoom.showInfo()

            action = recognize("\nDo you want to move or shoot an arrow? ", ["M", "S", "H"])

            if action == "H":
                helpNeeded = True

            while helpNeeded:
                output("You can move around the tunnels. \n"
                        "From where you are standing, you can walk East, West, North or South. \n"
                        "But beware of traps!\n"
                        "If you hear bat wings flapping, then bats reside in one of the adjacent rooms.\n"
                        "When you step into their room, they will abduct you and drop you in a random room. ,, \n"
                        "A howling wind signals that a bottomless pit is in one of the neighbouring rooms. \n"
                        "Don't fall into it or you will die! \n"
                        "If you hear Wumpus growl, then be especially careful! \n"
                        "You can try to kill Wumpus by shooting an arrow. \n")
                action = recognize("\nDo you want to move or shoot an arrow? ", ["M", "S", "H"])
                if action != "H":
                    helpNeeded = False
                
            if action == "M":
                self.move()
                while self.__currentRoom.getTrap() == "bats":
                    self.batAbduction()

                trapType = self.__currentRoom.getTrap()        
                if trapType == "pit" or trapType == "wumpus":
                    self.endGame(trapType)
                            
            elif action == "S":
                self.shootArrow()

            if self.__running and self.__difficulty == "D":
                self.moveWumpus()


############################################################################## FUNCTIONS #######


def getUserInput(message, validInputs):
    """ takes input from the user for the main loop.
    RETURNS userInput. """
    try:
        userInput = input().upper()
        #userInput = input(message).upper()
        proc.kill()
        while not userInput in validInputs:
            output("Please give a valid answer.")
            say(message, False)
            #userInput = input(message).upper()
            userInput = input().upper()
        return userInput

    except KeyboardInterrupt:
        #output("\nYou pressed Ctrl+C.\n")
        exit()
    except EOFError:
        #output("\nYou pressed Ctrl+D.\n")
        exit()

def showInstructions():
    """ outputs information about the game's story and how to play. """
    output("-----------------------------------------------------\n\n"
          "You are in the tunnels beneath KTH where the greedy monster Wumpus dwells.\n"
          "The tunnels are made up of 20 rooms that are connected by narrow passageways.\n"
          "You can move around in the maze,,\n"
          "However, there are traps lurking around every corner. Some rooms contain\n"
          "bottomless pits, that will swallow you up. Others are home to bats, which will\n"
          "abduct you and drop you in a random room,,\n"
          "Wumpus lives in one of the rooms and will eat you as soon as he notices you,,\n"
          "Luckily you can sense from the adjacent rooms, if there is a draft of air from\n"
          "a bottomless pit, the sound of flapping bat wings or the smell of Wumpus' foul\n"
          "breath,,\n"
          "\n"
          "To win the game, you have to shoot Wumpus with your bow and arrows.\n"
          "You have 5 arrows. Good luck!\n"
          "If you ever are unsure what to do, you can ask for help.")  





################################################################################### SPEECH #####

def output(text):
    #print(text)
    say(text, True)

def recognize(message, validInputs):
    say(message, True)
    return record(validInputs)
    #return getUserInput(message, validInputs)

def record(validInputs):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    w = []
    try:
        l = r.recognize(audio,True)
        print("Done. Possible utterances:")
        for prediction in l:
            utterance = prediction["text"].split()
            for word in utterance:
                w.append(word)
            print("\"" + prediction["text"] + "\" (" + str(prediction["confidence"] * 100) + "%)")
    except LookupError:
        print("Could not understand audio")

    words = list(set(w))
    for v in validInputs:
        buzzlist = buzzwords[v]
        for b in buzzlist:
            if b in words:
                print("User input: " + v)
                return v

def strip(text):
    # prepare text for speech output
    text = text.replace("-", "")
    text = text.replace("~", "")
    return text

def say(text, blocking=False):
    if blocking:
        os.system("say -v Daniel \"" + strip(text) + "\"")
    else:
        global proc 
        proc = subprocess.Popen(["say","-v","Daniel","\"" + strip(text)], stdout=subprocess.PIPE)    
    
def play(sound):
    os.system("afplay  sfx/" + sound + ".wav")
    #sfx = pyglet.resource.media("sfx/" + sound + ".wav", streaming=False)
    #sfx.play()


################################################################################### MAIN #######

def main():

    firstTime = True

    global buzzwords
    buzzwords = {}
    buzzwords["Y"] = ["yes", "yeah", "yo", "yep"]
    buzzwords["N"] = ["no", "nope"]
    buzzwords["M"] = ["move", "go"]
    buzzwords["N"] = ["north", "up", "normal"]
    buzzwords["E"] = ["east", "right", "easy"]
    buzzwords["S"] = ["south", "down", "shoot", "arrow", "fire"]
    buzzwords["W"] = ["west", "left"]
    buzzwords["A"] = ["new", "game", "play", "start"]
    buzzwords["B"] = ["test"]
    buzzwords["C"] = ["exit", "quit", "stop", "out", "program"]
    buzzwords["H"] = ["help", "support", "hard"]

    output("-----------------------------------------------------\n"
              "~ Welcome to 'Wumpus', a speech-controlled adventure game. ~\n")

    while True:      
        
        if firstTime: 
            userInput = recognize("  What do you want to do?\n"
                  "          Start a new game,\n"
                  "          or exit the program.\n"
                  "          ", ["A", "B", "C"])
        else:
            userInput = recognize("Do you want to play again or exit the program?\n"
                  "          ", ["A", "B", "C"])

        if userInput == "A":
            if firstTime == False:
                intro = recognize("Would you like to hear the introduction again?\n"
                  "          ", ["Y", "N"])
                if intro == "Y":
                    showInstructions()
            else:
                showInstructions()
            newGame = Game(firstTime)
            newGame.runGame()

        elif userInput == "B":
            newGame = TestGame(firstTime)
            newGame.runGame()

        elif userInput == "C":
            break
            output("Thank you for playing.\n")

        firstTime = False

main()