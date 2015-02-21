# P-uppgift 154: Wumpus
# Text-based adventure game
# Iris Hartl 2014-05-04

############################################################################### CHANGE LOG ####
#
# 2014-04-12, v0.2: added showMenu() and move(). User can now interact with the program and move between rooms.

# 2014-04-12, v0.3: added methods showTraps(), senseTraps(), trapCheck().
#                   added functions addTraps(), peek(). Rooms now contain (non-lethal) traps.
#                   changed function chooseStartingpoint() to only choose rooms w/o traps.

# 2014-04-18, v0.4: introduced error-handling for user input.
#                   Replaced the Quiver class with a Player class.
#                   added functions batAbduction() and death().
#                   added method whichTrap() to the Room class.
#                   changed showMenu() and main().
#                   Rooms now contain lethal traps.

# 2014-04-20, v0.5: made minor changes to chooseStartingpoint, showMenu(), move(), main(), Player and batAbduction().
#                   removed functions showMap() and peek() (method showInfo() is taking over their role).
#                   removed testing-method showTraps().
#                   updated and added some descriptions.

# 2014-04-20, v0.6: added function shootArrow(). Made minor changes to showMenu().
#                   rewrote function death() to endGame().
#                   removed some functionality from the Player class.
#                   added a Game class.

# 2014-04-21, v0.7: added an introduction text. Made some minor changes to descriptions and names.
#                   removed method trapCheck(). Renamed whichTrap() to getTrap().
#                   added function getDirection() and made some changes to move() and shootArrow().

# 2014-04-24, v0.8: added difficulty levels. Added function moveWumpus().

# 2014-04-24, v0.9: moved most functions into the game class and changed them to methods accordingly.
#                   renamed showMenu() to runGame().

# 2014-04-29, v1.0: changed Game-method moveWumpus() to actually change a room's Wumpus-attribute
#                   instead of creating a new attribute within the Game class.
#                   improved error-handling in runGame().
#                   renamed all hole(s) to pit(s) for more coherent naming.

# 2014-05-04, v1.1: changed self.__arrowRoom to be a local variable in the Game class.
#                   further improved user input and error handling.
#                   change Game-method moveWumpus().
#                   wrote a new main loop that lets the user start a new game w/o restarting the program.


############################################################################### MODULES #######

import random

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
        """ prints information about the room and its neighbours. """
        print("\nYou are in room number " + str(self.__roomNr) + ".")
        print("From here, you can get to the following rooms:")
        print("East: " + str(self.__neighbours["E"]) + " | West: " + str(self.__neighbours["W"]) +
              " | North: " + str(self.__neighbours["N"]) + " | South: " + str(self.__neighbours["S"]))
        for direction in self.__neighbours:
            self.senseTraps(direction)

    def senseTraps(self, direction):
        """ prints information about traps in the neighbouring rooms. """
        neighbour = self.__neighbours[direction]
        if neighbour.__pit:
            print("You feel a light draft.")
        elif neighbour.__bats:
            print("You hear bats.")
        elif neighbour.__wumpus:
            print("You smell Wumpus' foul breath!")

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
        """ prints information about the player.
    RETURNS arrows as a string. """
        rep = "You have " + str(self.__arrows) + " arrow(s) left."
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

    def __init__(self):
        """ creates a Game-object.
    CHANGES running. """
        self.__running = True
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

        elif self.__difficulty == "H":
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
        return getUserInput("\nChoose difficulty:\nEasy (E) | Normal (N) | Hard (H)\n", ["E", "N", "H"])
        
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
        print("\nWumpus is moving through the tunnels...")

        if self.__wumpusRoom == self.__currentRoom:
            self.endGame("wumpus")

    def inputDirection(self, movementType):
        """ lets the user input a direction and shows fitting text. Handles errors.
    RETURNS E, W, N or S as a string. """
        
        if movementType == "move":
            prompt = "Where do you want to go? (E, W, N, S) "
        elif movementType == "shoot1":
            prompt = "Which direction do you want to shoot in? (E, W, N, S) "
        elif movementType == "shoot2":
            prompt = "Which way should it fly? (E, W, N, S) "

        return getUserInput(prompt, ["E", "W", "N", "S"])
    
    def move(self):
        """ lets the user move around the labyrinth.
    CHANGES currentRoom. """
        direction = self.inputDirection("move")
        self.__currentRoom = self.__currentRoom.getNeighbour(direction)

    def shootArrow(self):
        """ lets the user shoot an arrow. """
        direction = self.inputDirection("shoot1")
        counter = 1
        arrowRoom = self.__currentRoom.getNeighbour(direction)
        while arrowRoom.getTrap() != "wumpus" and counter < 3 and arrowRoom != self.__currentRoom:
            print("\nThe arrow has power for " + str(3 - counter) + " more room(s).")
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
                print("\n" + str(self.__player))

    def batAbduction(self):
        """ moves the user to a random room on the map.
    CHANGES currentRoom. """
        self.__currentRoom = random.choice(self.__listOfRooms)
        print("\nBats live in this room! You feel their wings touching your cheek and suddenly\n"
              "lose ground under your feet.\n"
              "After a short trip through the air, the bats drop you in room nr. "
              + str(self.__currentRoom) + ".")

    def endGame(self, trapType=""):
        """ ends the game and prints a fitting text.
    CHANGES self.__running."""
        self.__running = False
        if trapType == "pit":
            print("\nThere is a bottomless pit in this room!\n"
                  "You are sucked into it in a powerful current of air.\n"
                  "As you fall into the darkness, you come to the realisation that\n"
                  "trespassing on KTH property to hunt monsters\n"
                  "might not have been such a great idea after all...")
            print("\nGAME OVER\n\n")

        elif trapType == "wumpus":
            print("\nWumpus is in this room!\n"
                  "You try to reach behind your back to grasp an arrow and shoot the monster, \n"
                  "but accidentally spill the contents of your quiver as you twist and bend.\n"
                  "The sound of the arrows clattering on the floor alerts Wumpus to your presence.\n"
                  "He looks pretty hungry...")
            print("\nGAME OVER\n\n")

        elif trapType == "suicide":
            print("\nCongratulations, you managed to shoot yourself with bow and arrow.")
            print("\nGAME OVER\n\n")

        elif trapType == "noArrows":
            print("\nYou hear your last arrow hit a wall a couple of rooms away.\n"
                  "How are you going to defeat Wumpus now, with your bare hands?")
            print("\nGAME OVER\n\n")

        else:
            print("\nYour arrow found Wumpus! It doesn't seem to like him, judging from the way\n"
                  "it finds its path right to the monster's heart all on its own. Good riddance!\n"
                  "Now the only thing left to do is to get out of here!\nThat can't be too hard, right?...")
            print("\nYOU WON!!! Go you!\n\n")

    def runGame(self):
        """ lets the user interact with the program. """

        while self.__running:
            self.__currentRoom.showInfo()

            action = getUserInput("\nDo you want to move (M) or shoot an arrow (S)? ", ["M", "S"])
                
            if action == "M":
                self.move()
                while self.__currentRoom.getTrap() == "bats":
                    self.batAbduction()

                trapType = self.__currentRoom.getTrap()        
                if trapType == "pit" or trapType == "wumpus":
                    self.endGame(trapType)
                            
            elif action == "S":
                self.shootArrow()

            if self.__running and self.__difficulty == "H":
                self.moveWumpus()
    
            
############################################################################## FUNCTIONS #######

def getUserInput(message, validInputs):
    """ takes input from the user for the main loop.
    RETURNS userInput. """
    try:
        userInput = input(message).upper()
        while not userInput in validInputs:
            print("Please give a valid answer.")
            userInput = input(message).upper()
        return userInput

    except KeyboardInterrupt:
        print("\nYou pressed Ctrl+C.\n")
        exit()
    except EOFError:
        print("\nYou pressed Ctrl+D.\n")
        exit()

def showInstructions():
    """ prints information about the game's story and how to play. """
    print("-----------------------------------------------------\n\n"
          "You are in the tunnels beneath KTH where the greedy monster Wumpus lives.\n"
          "The tunnels are made up of 20 rooms that are connected by narrow passageways.\n"
          "You can move east, west, north or south from one room to the next.\n"
          "However, there are traps lurking around every corner - some rooms contain\n"
          "bottomless pits that will swallow you up. Others are home to bats, which will\n"
          "abduct you and drop you in a random room.\n"
          "Wumpus lives in one of the rooms and will eat you as soon as he notices you.\n"
          "Luckily you can sense from the adjacent rooms, if there is a draft of air from\n"
          "a bottomless pit, the sound of flapping bat wings or the smell of Wumpus' foul\n"
          "breath.\n"
          "\n"
          "To win the game, you have to shoot Wumpus with your bow and arrows.\n"
          "Arrows can fly through at most 3 rooms and you can change their direction after\n"
          "every room. Remember that the tunnels are layed out in unexpected ways.\n"
          "You might accidentally shoot yourself...\n"
          "You have 5 arrows. Good luck!")


################################################################################### MAIN #######

def main():

    while True:
        print("-----------------------------------------------------\n"
              "~ Welcome to 'Wumpus', a text-based adventure game ~\n"
              "  What do you want to do?\n"
              "          Start a new game (a)\n"
              "          Exit the program (b)")
        
        userInput = getUserInput("          ", ["A", "B"])

        if userInput == "A":
            showInstructions()
            newGame = Game()
            newGame.runGame()

        elif userInput == "B":
            input("-----------------------------------------------------\n"
                  "Press enter to exit.")
            break

main()


""" TESTDATA
>>> 
-----------------------------------------------------
~ Welcome to 'Wumpus', a text-based adventure game ~
  What do you want to do?
          Start a new game (a)
          Exit the program (b)
          a
-----------------------------------------------------

You are in the tunnels beneath KTH where the greedy monster Wumpus lives.
The tunnels are made up of 20 rooms that are connected by narrow passageways.
You can move east, west, north or south from one room to the next.
However, there are traps lurking around every corner - some rooms contain
bottomless pits that will swallow you up. Others are home to bats, which will
abduct you and drop you in a random room.
Wumpus lives in one of the rooms and will eat you as soon as he notices you.
Luckily you can sense from the adjacent rooms, if there is a draft of air from
a bottomless pit, the sound of flapping bat wings or the smell of Wumpus' foul
breath.

To win the game, you have to shoot Wumpus with your bow and arrows.
Arrows can fly through at most 3 rooms and you can change their direction after
every room. Remember that the tunnels are layed out in unexpected ways.
You might accidentally shoot yourself...
You have 5 arrows. Good luck!

Choose difficulty:
Easy (E) | Normal (N) | Hard (H)
h

You are in room number 15.
From here, you can get to the following rooms:
East: 18 | West: 19 | North: 5 | South: 6
You feel a light draft.
You hear bats.

Do you want to move (M) or shoot an arrow (S)? m
Where do you want to go? (E, W, N, S) e

Wumpus is moving through the tunnels...

Wumpus is in this room!
You try to reach behind your back to grasp an arrow and shoot the monster, 
but accidentally spill the contents of your quiver as you twist and bend.
The sound of the arrows clattering on the floor alerts Wumpus to your presence.
He looks pretty hungry...

GAME OVER


-----------------------------------------------------
~ Welcome to 'Wumpus', a text-based adventure game ~
  What do you want to do?
          Start a new game (a)
          Exit the program (b)
          a
-----------------------------------------------------

You are in the tunnels beneath KTH where the greedy monster Wumpus lives.
The tunnels are made up of 20 rooms that are connected by narrow passageways.
You can move east, west, north or south from one room to the next.
However, there are traps lurking around every corner - some rooms contain
bottomless pits that will swallow you up. Others are home to bats, which will
abduct you and drop you in a random room.
Wumpus lives in one of the rooms and will eat you as soon as he notices you.
Luckily you can sense from the adjacent rooms, if there is a draft of air from
a bottomless pit, the sound of flapping bat wings or the smell of Wumpus' foul
breath.

To win the game, you have to shoot Wumpus with your bow and arrows.
Arrows can fly through at most 3 rooms and you can change their direction after
every room. Remember that the tunnels are layed out in unexpected ways.
You might accidentally shoot yourself...
You have 5 arrows. Good luck!

Choose difficulty:
Easy (E) | Normal (N) | Hard (H)
h

You are in room number 6.
From here, you can get to the following rooms:
East: 13 | West: 1 | North: 12 | South: 4
You hear bats.
You hear bats.

Do you want to move (M) or shoot an arrow (S)? m
Where do you want to go? (E, W, N, S) e

Bats live in this room! You feel their wings touching your cheek and suddenly
lose ground under your feet.
After a short trip through the air, the bats drop you in room nr. 19.

Wumpus is moving through the tunnels...

You are in room number 19.
From here, you can get to the following rooms:
East: 10 | West: 14 | North: 3 | South: 8
You hear bats.
You hear bats.
You feel a light draft.
You hear bats.

Do you want to move (M) or shoot an arrow (S)? m
Where do you want to go? (E, W, N, S) e

Bats live in this room! You feel their wings touching your cheek and suddenly
lose ground under your feet.
After a short trip through the air, the bats drop you in room nr. 6.

Wumpus is moving through the tunnels...

You are in room number 6.
From here, you can get to the following rooms:
East: 13 | West: 1 | North: 12 | South: 4
You hear bats.

Do you want to move (M) or shoot an arrow (S)? s
Which direction do you want to shoot in? (E, W, N, S) w

The arrow has power for 2 more room(s).
Which way should it fly? (E, W, N, S) w

The arrow has power for 1 more room(s).
Which way should it fly? (E, W, N, S) w

You have 4 arrow(s) left.

Wumpus is moving through the tunnels...

You are in room number 6.
From here, you can get to the following rooms:
East: 13 | West: 1 | North: 12 | South: 4
You hear bats.
You smell Wumpus' foul breath!

Do you want to move (M) or shoot an arrow (S)? s
Which direction do you want to shoot in? (E, W, N, S) n

The arrow has power for 2 more room(s).
Which way should it fly? (E, W, N, S) n

The arrow has power for 1 more room(s).
Which way should it fly? (E, W, N, S) n

You have 3 arrow(s) left.

Wumpus is moving through the tunnels...

You are in room number 6.
From here, you can get to the following rooms:
East: 13 | West: 1 | North: 12 | South: 4
You hear bats.

Do you want to move (M) or shoot an arrow (S)? m
Where do you want to go? (E, W, N, S) s

Bats live in this room! You feel their wings touching your cheek and suddenly
lose ground under your feet.
After a short trip through the air, the bats drop you in room nr. 16.

There is a bottomless pit in this room!
You are sucked into it in a powerful current of air.
As you fall into the darkness, you come to the realisation that
trespassing on KTH property to hunt monsters
might not have been such a great idea after all...

GAME OVER


-----------------------------------------------------
~ Welcome to 'Wumpus', a text-based adventure game ~
  What do you want to do?
          Start a new game (a)
          Exit the program (b)
          b
-----------------------------------------------------
Press enter to exit.
>>> 
"""








    
