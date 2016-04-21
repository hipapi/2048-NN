from Tkinter import *
from logic import *
from random import *
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import RMSprop
import numpy as np
import time


SIZE = 500
GRID_LEN = 4
GRID_PADDING = 10

BACKGROUND_COLOR_GAME = "#92877d"
BACKGROUND_COLOR_CELL_EMPTY = "#9e948a"
BACKGROUND_COLOR_DICT = {   2:"#eee4da", 4:"#ede0c8", 8:"#f2b179", 16:"#f59563", \
                            32:"#f67c5f", 64:"#f65e3b", 128:"#edcf72", 256:"#edcc61", \
                            512:"#edc850", 1024:"#edc53f", 2048:"#edc22e" }
CELL_COLOR_DICT = { 2:"#776e65", 4:"#776e65", 8:"#f9f6f2", 16:"#f9f6f2", \
                    32:"#f9f6f2", 64:"#f9f6f2", 128:"#f9f6f2", 256:"#f9f6f2", \
                    512:"#f9f6f2", 1024:"#f9f6f2", 2048:"#f9f6f2" }
FONT = ("Verdana", 40, "bold")

KEY_UP_ALT = "\'\\uf700\'"
KEY_DOWN_ALT = "\'\\uf701\'"
KEY_LEFT_ALT = "\'\\uf702\'"
KEY_RIGHT_ALT = "\'\\uf703\'"

KEY_UP = "'w'"
KEY_DOWN = "'s'"
KEY_LEFT = "'a'"
KEY_RIGHT = "'d'"

class GameGrid(Frame):
    def __init__(self):
        Frame.__init__(self)
        self.model = Sequential()
        self.model.add(Dense(164, init='lecun_uniform', input_shape=(16,)))
        self.model.add(Activation('relu'))
        #model.add(Dropout(0.2)) I'm not using dropout, but maybe you wanna give it a try?

        self.model.add(Dense(150, init='lecun_uniform'))
        self.model.add(Activation('relu'))
        #model.add(Dropout(0.2))

        self.model.add(Dense(4, init='lecun_uniform'))
        self.model.add(Activation('linear')) #linear output so we can have range of real-valued outputs

        rms = RMSprop()
        self.model.compile(loss='mse', optimizer=rms)
        self.atoi = {'w': 0, 'a': 1, 's': 2, 'd': 3}


        #self.gamelogic = gamelogic
        self.commands = {   KEY_UP: up, KEY_DOWN: down, KEY_LEFT: left, KEY_RIGHT: right,
                            KEY_UP_ALT: up, KEY_DOWN_ALT: down, KEY_LEFT_ALT: left, KEY_RIGHT_ALT: right }
        #keypress = ''
        keypress = 'w'
        #self.grid_cells = []
        #self.init_grid()
        #matrix = self.init_matrix()
        #print matrix
        import random

        epochs = 1000
        gamma = 0.9 #since it may take several moves to goal, making gamma high
        epsilon = 1
        for i in range(epochs):
            for widget in self.winfo_children():
                widget.destroy()
            self.grid()
            self.master.title('2048')
            self.master.bind("<Key>", self.key_down)
            self.status = -1
            self.grid_cells = []
            self.init_grid()
            matrix = self.init_matrix()
            self.update_grid_cells()
            state = self.get_state()
            number = len(state)
            self.reward = self.get_score()
            #while game still in progress

            while(self.status == -1):
                #time.sleep(0.1)
                time.sleep(0.5)
                qval = self.model.predict(state.reshape(1,16), batch_size=1)

                if (random.random() < epsilon): #choose random action
                    action = np.random.randint(0,4)
                else: #choose best action from Q(s,a) values
                    action = (np.argmax(qval))
                newstate = state
                self.makeMove(action)
                state = self.get_state()
                if (newstate == state).all():
                    self.reward -=1

                #self.update_grid_cells()
                new_state = self.get_state()
                #new_state =
                #Observe reward
                self.reward = self.get_score()
                #Get max_Q(S',a)
                newQ = self.model.predict(new_state.reshape(1,16), batch_size=1)
                maxQ = np.max(newQ)
                self.reward = self.get_score()
                y = np.zeros((1,4))
                y[:] = qval[:]
                if self.status == -1: #non-terminal state
                    update = (self.reward + (gamma * maxQ))
                else: #terminal state
                    update = self.reward
                y[0][action] = update #target output
                print(i)
                self.model.fit(state.reshape(1,16), y, batch_size=1, nb_epoch=1, verbose=1)
                state = new_state

            if epsilon > 0.1:
                epsilon -= (1/epochs)
                #self.matrix,done = self.commands[repr('s')](self.matrix)
        epochs = 20
        self.model.save_weights('2048.h5', overwrite=True)
        for widget in self.winfo_children():
                widget.destroy()
        for i in range(epochs):
            #elf.destroy()
            self.status = -1         #self.random_key(keypress)

            self.grid()
            self.master.title('2048')
            self.master.bind("<Key>", self.key_down)
            self.status = -1
            self.grid_cells = []
            self.init_grid()
            matrix = self.init_matrix()
            self.update_grid_cells()
            state = self.get_state()
            number = len(state)
            i = 0
            newqval = -100
            while(self.status == -1):
                time.sleep(0.5)
                qval = self.model.predict(state.reshape(1,16), batch_size=1)
                action = (np.argmax(qval)) #take action with highest Q-value
                #print('Move #: %s; Taking action: %s' % (i, action))
                self.makeMove( action)
                # i +=1
                # if i >20 and action == newqval:
                #     l = np.sort(qval,axis=None)
                #     action = l([3])
                #     i = 0

                self.update_grid_cells()
                #print(dispGrid(state))
                self.reward = self.get_score()
                newqval = action



        #self.mainloop()


    def get_score(self):
        reward = 0
        for i in range(GRID_LEN):
            for j in range(GRID_LEN):
                reward += self.matrix[i][j]
        return reward

    def makeMove(self,action):
        #{'w': 0, 'a': 1, 's': 2, 'd': 3}
        if action==0:
             self.random_key('w')
        elif action==1:
            self.random_key('a')
        #left (column - 1)
        elif action==2:
            self.random_key('s')
        #right (column + 1)
        elif action==3:
            self.random_key('d')

    def init_grid(self):
        background = Frame(self, bg=BACKGROUND_COLOR_GAME, width=SIZE, height=SIZE)
        background.grid()
        for i in range(GRID_LEN):
            grid_row = []
            for j in range(GRID_LEN):
                cell = Frame(background, bg=BACKGROUND_COLOR_CELL_EMPTY, width=SIZE/GRID_LEN, height=SIZE/GRID_LEN)
                cell.grid(row=i, column=j, padx=GRID_PADDING, pady=GRID_PADDING)
                # font = Font(size=FONT_SIZE, family=FONT_FAMILY, weight=FONT_WEIGHT)
                t = Label(master=cell, text="", bg=BACKGROUND_COLOR_CELL_EMPTY, justify=CENTER, font=FONT, width=4, height=2)
                t.grid()
                grid_row.append(t)

            self.grid_cells.append(grid_row)

    def gen(self):
        return randint(0, GRID_LEN - 1)

    def init_matrix(self):
        self.matrix = new_game(4)

        self.matrix=add_two(self.matrix)
        self.matrix=add_two(self.matrix)

    def update_grid_cells(self):
        for i in range(GRID_LEN):
            for j in range(GRID_LEN):
                new_number = self.matrix[i][j]
                if new_number == 0:
                    self.grid_cells[i][j].configure(text="", bg=BACKGROUND_COLOR_CELL_EMPTY)
                else:
                    self.grid_cells[i][j].configure(text=str(new_number), bg=BACKGROUND_COLOR_DICT[new_number], fg=CELL_COLOR_DICT[new_number])
        self.update_idletasks()

    def get_state(self):
        X = np.array([])
        for i in range(GRID_LEN):
            for j in range(GRID_LEN):
               Y = self.matrix[i][j]
               T = self.get_score()
               Q = float(Y)/T
               X =  np.append(X,str(Q))
        return X

    def key_down(self, event):
        key = repr(event.char)
        if key in self.commands:
            self.matrix,done = self.commands[repr(event.char)](self.matrix)
            if done:
                self.matrix = add_two(self.matrix)
                self.update_grid_cells()
                done=False
                if game_state(self.matrix)=='win':
                    self.grid_cells[1][1].configure(text="You",bg=BACKGROUND_COLOR_CELL_EMPTY)
                    self.grid_cells[1][2].configure(text="Win!",bg=BACKGROUND_COLOR_CELL_EMPTY)
                    self.status = 1
                elif game_state(self.matrix)=='lose':
                    self.grid_cells[1][1].configure(text="You",bg=BACKGROUND_COLOR_CELL_EMPTY)
                    self.grid_cells[1][2].configure(text="Lose!",bg=BACKGROUND_COLOR_CELL_EMPTY)
                    self.status = -10
                    self.reward -= 1000
                else:
                    self.status = -1

    def random_key(self, random_key):
        key = random_key
        #if key in self.commands:
            #print 'legal'
        self.matrix,done = self.commands[repr(key)](self.matrix)
        if game_state(self.matrix)=='win':
            done = True
        if done:
             self.matrix = add_two(self.matrix)
             self.update_grid_cells()
             done=False
             if game_state(self.matrix)=='win':
                 self.grid_cells[1][1].configure(text="You",bg=BACKGROUND_COLOR_CELL_EMPTY)
                 self.grid_cells[1][2].configure(text="Win!",bg=BACKGROUND_COLOR_CELL_EMPTY)
                 self.status = 1
                 self.reward += 500
             elif game_state(self.matrix)=='lose':
                 self.grid_cells[1][1].configure(text="You",bg=BACKGROUND_COLOR_CELL_EMPTY)
                 self.grid_cells[1][2].configure(text="Lose!",bg=BACKGROUND_COLOR_CELL_EMPTY)
                 #self.destroy()
                 self.status = -10
                 self.reward -= 1000
             else:
                 self.status = -1
                 self.reward -= 1

        # else:
        #    if game_state(self.matrix)=='lose':
        #             #self.grid_cells[1][1].configure(text="You",bg=BACKGROUND_COLOR_CELL_EMPTY)
        #             #self.grid_cells[1][2].configure(text="Lose!",bg=BACKGROUND_COLOR_CELL_EMPTY)
        #             #self.destroy()
        #             self._displayof()
        #             self.status = -10
        #             self.reward -= 1000

    def generate_next(self):
        index = (self.gen(), self.gen())
        while self.matrix[index[0]][index[1]] != 0:
            index = (self.gen(), self.gen())
        self.matrix[index[0]][index[1]] = 2

gamegrid = GameGrid()
