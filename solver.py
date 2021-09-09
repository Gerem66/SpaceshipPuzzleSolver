#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
    Author : Gérémy Lecaplain
    Time spent : 8h
'''

from os import system
from time import time, sleep
from enum import Enum

class Player:
    def __init__(self, x, y, orientation):
        self.x = x
        self.y = y
        # 0:Top | 1:Right | 2:Bottom | 3:Left
        self.orientation = orientation
        self.history = []
        self.historyMaxLength = 30

    def Turn(self, move, condition):
        if condition:
            if move not in [ 1, -1 ]: return
            self.orientation += move
            if self.orientation < 0: self.orientation = 3
            if self.orientation > 3: self.orientation = 0
        self.addPosInHistory()

    def Forward(self, condition):
        if condition:
            orientation = self.orientation
            if orientation == 0:
                self.y = max(0, self.y - 1)
            elif orientation == 1:
                self.x = self.x + 1
            elif orientation == 2:
                self.y = self.y + 1
            elif orientation == 3:
                self.x = max(0, self.x - 1)
        self.addPosInHistory()

    def Show(self):
        orientations = [ '↑', '→', '↓', '←' ]
        return orientations[self.orientation]

    def addPosInHistory(self):
        self.history.append([ self.x, self.y ])
        while len(self.history) > self.historyMaxLength:
            del self.history[0]

    def isInInfiniteLoop(self):
        infinite = False
        if len(self.history) == self.historyMaxLength:
            maxPositionsNumber = 0
            for h in self.history:
                positionSame = self.history.count(h)
                if positionSame > maxPositionsNumber:
                    maxPositionsNumber = positionSame
            if maxPositionsNumber >= self.historyMaxLength/3: infinite = True
        return infinite

class Floor:
    def __init__(self, player, lines):
        self.floor = [ l.split() for l in lines ]
        self.player = player

    def getBloc(self, x, y):
        return self.floor[y][x]

    def getblocColored(self, x, y):
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        RED = '\033[91m'
        ENDC = '\033[0m'
        colors = { 'B': BLUE, 'G': GREEN, 'R': RED }

        block = self.getBloc(x, y)
        if (block == '0'):
            return ' '
        else:
            block_text = '█'
            block_color = colors[block]
            return block_color + block_text + ENDC

    def CheckCondition(self, condition):
        isOk = condition == Conditions.No
        playerX = self.player.x
        playerY = self.player.y
        block = self.getBloc(playerX, playerY)
        if block == condition.value: isOk = True
        return isOk

    def printFloor(self):
        playerX = self.player.x
        playerY = self.player.y
        playerO = self.player.Show()
        for y in range(len(self.floor)):
            for x in range(len(self.floor[0])):
                if playerX == x and playerY == y:
                    print(playerO, end='')
                else:
                    print(self.getblocColored(x, y), end='')
            print()

class Game:
    def __init__(self, fileName, instructions):
        self.fps = 8

        file = open(fileName, 'r')
        lines = file.readlines()
        file.close()

        startPos, endPos = [ pos.split(' ') for pos in lines[0].split(',') ]
        self.player = Player(int(startPos[0]), int(startPos[1]), int(startPos[2]))
        self.floor = Floor(self.player, lines[1:])
        self.step = 0
        self.instructions = instructions
        self.endPos = [ int(endPos[0]), int(endPos[1]) ]

        self.executionList = [ 0 ]
        self.executionMaxDeepth = 100

        self.attempt = -1
        self.showFloor = True
        self.speedMode = False

    def setSettings(self, attempt, totalAttempt, startTime, showFloor = False, speedMode = False):
        self.attempt = attempt
        self.totalAttempt = totalAttempt
        self.startTime = startTime
        self.showFloor = showFloor
        self.speedMode = speedMode

    def Start(self):
        self.alive = True
        while self.alive:
            t_start = time()
            self.__loop()
            t_end = time()
            delta = max(0, (1/self.fps) - (t_end - t_start))
            if not self.speedMode: sleep(delta)
        return [ self.player.x, self.player.y ] == self.endPos

    def __loop(self):
        self.__nextStep()
        if not self.speedMode or self.showFloor:
            system('clear || cls')
            self.floor.printFloor()
            self.__printInstructions()
        if self.speedMode and self.attempt % 10000 == 0:
            system('clear || cls')
            self.__printInstructions()
        self.alive = self.__isAlive()

    def __nextStep(self):
        index = 0
        step = self.executionList[-1]
        for function in range(len(self.instructions)):
            for element in self.instructions[function]:
                if index == step:
                    _instruction, _condition = element
                    cond = self.floor.CheckCondition(_condition)
                    lastIndexOfFunction = sum([ len(instr) for instr in self.instructions[:function+1] ]) - 1

                    if type(_instruction) == str and _instruction[0] == 'f':
                        #if _instruction == 'f1':
                        toFunction = int(_instruction[1:])
                        firstIndexOfFunction = sum([ len(instr) for instr in self.instructions[:toFunction] ])
                        if index == lastIndexOfFunction: del self.executionList[-1]
                        else: self.executionList[-1] += 1
                        if cond:
                            self.executionList.append(firstIndexOfFunction)
                            self.player.addPosInHistory()

                    elif type(_instruction) == Instructions:
                        if _instruction == Instructions.Forward: self.player.Forward(cond)
                        elif _instruction == Instructions.Right: self.player.Turn(1, cond)
                        elif _instruction == Instructions.Left: self.player.Turn(-1, cond)

                        if index == lastIndexOfFunction: del self.executionList[-1]
                        else: self.executionList[-1] += 1
                index += 1

    def __printInstructions(self):
        print()
        index = 0
        for f in range(len(self.instructions)):
            print("f{} :".format(f), end=' ')
            for component in self.instructions[f]:
                print_text = ''
                _inst, _cond = component

                # Print instruction
                arrows = [ '↑', '←', '→' ]
                if type(_inst) == str: print_text = _inst
                else: print_text = arrows[_inst.value]

                # Print condition
                BLUE = '\033[94m'
                GREEN = '\033[92m'
                RED = '\033[91m'
                ENDC = '\033[0m'
                UNDERLINE = '\033[4m'
                colors = { '0': ENDC, 'B': BLUE, 'G': GREEN, 'R': RED }
                color = colors[_cond.value]
                selected = UNDERLINE if len(self.executionList) and index == self.executionList[-1] else ''
                print(color + selected + print_text + ENDC, end=' ')
                index += 1
            print()
        if self.attempt > -1:
            pc = (self.attempt / self.totalAttempt) * 100

            # Current time
            durationTime = time() - self.startTime
            print("\n{} / {} ({} %)".format(self.attempt, self.totalAttempt, round(pc, 2)))
            print("Current time : " + self.__printTimeWithSeconds(durationTime))

            # Time left
            attemptPerSecond = durationTime / self.attempt
            leftTime = (attemptPerSecond * self.totalAttempt) - durationTime
            print("Time left : {} ({} attempt / second)".format(self.__printTimeWithSeconds(leftTime), int(1/attemptPerSecond)))

    def __printTimeWithSeconds(self, seconds):
        H = int(seconds // 3600)
        M = int((seconds - H * 3600) // 60)
        S = int((seconds - H * 3600 - M * 60))
        textTime = ''
        if H > 0: textTime += str(H) + 'h '
        if M > 0: textTime += str(M) + 'm '
        if S > 0: textTime += str(S) + 's'
        return textTime

    def __isAlive(self):
        alive = True
        playerX = self.player.x
        playerY = self.player.y
        if self.floor.getBloc(playerX, playerY) == '0': alive = False
        if self.player.isInInfiniteLoop(): alive = False
        if playerX == self.endPos[0] and playerY == self.endPos[1]: alive = False
        if len(self.executionList) == 0 or len(self.executionList) > self.executionMaxDeepth: alive = False
        return alive

class Instructions(Enum):
    Forward = 0
    Left = 1
    Right = 2
class Conditions(Enum):
    No = '0'
    Red = 'R'
    Green = 'G'
    Blue = 'B'

def GenerateAllInstructions(func, totalArray, deepth, currArray = [], i = 0):
    if i == deepth: func(currArray)
    else:
        newArr = currArray.copy()
        for element in totalArray:
            if len(newArr) <= i: newArr.append(None)
            newArr[i] = element
            if i < deepth: GenerateAllInstructions(func, totalArray, deepth, newArr, i + 1)

def BruteforceExec(instructions, fileName, attempt, startTime, totalAttempt):
    _instructions = [ [ instructions[0], instructions[1] ], [ instructions[2], instructions[3], instructions[4] ] ]
    #_instructions = [ instructions ]
    if attempt < startAttempt: return
    game = Game(fileName, _instructions)
    game.setSettings(attempt, totalAttempt, startTime, False, True)
    return game.Start()

# 0 : Single test
# 1 : BruteForce mode
mode = 1

if mode == 0:
    fileName = 'Maps/map2'
    instructions = [
        [
            [ Instructions.Forward, Conditions.No ],
            [ 'f1', Conditions.No ]
        ],
        [
            [ Instructions.Left, Conditions.Blue ],
            [ Instructions.Right, Conditions.Red ],
            [ 'f0', Conditions.No ]
        ]
    ]
    '''instructions = [
        [
            [ Instructions.Forward, Conditions.No ],
            [ 'f0', Conditions.Green ],
            [ Instructions.Forward, Conditions.No ],
            [ Instructions.Left, Conditions.No ],
            [ Instructions.Forward, Conditions.No ],
            [ Instructions.Right, Conditions.No ]
        ]
    ]'''
    game = Game(fileName, instructions)
    success = game.Start()
    if success: print("Success")
elif mode == 1:
    # Bruteforce instructions settings
    deepth = 5
    functionsNumber = 2
    startAttempt = 0
    fileName = 'Maps/map1'

    # Get all possibilities
    totalInstructions = []
    totalPossibilities = []
    for i in range(functionsNumber): totalInstructions.append('f' + str(i))
    for instruction in Instructions: totalInstructions.append(instruction)
    for instr in totalInstructions:
        for cond in Conditions:
            totalPossibilities.append([ instr, cond ])

    # Bruteforce
    founded = False
    attempt = 0
    startTime = time()
    totalAttempt = len(totalPossibilities) ** deepth

    def PreExec(instructions):
        global attempt, founded
        if founded: return
        attempt += 1
        success = BruteforceExec(instructions, fileName, attempt, startTime, totalAttempt)
        if success:
            founded = True
            print("Solution founded ! (index : {})".format(attempt))
            input("Press enter to replay")
            _instructions = [ [ instructions[0], instructions[1] ], [ instructions[2], instructions[3], instructions[4] ] ]
            #_instructions = [ instructions ]
            game = Game(fileName, _instructions)
            game.Start()

    GenerateAllInstructions(PreExec, totalPossibilities, deepth)