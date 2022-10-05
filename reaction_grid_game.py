from tkinter import *
from tkinter.font import Font
import random
import copy
import math

'''
IT IS ALL DONE!!

open tkinter window, generate a grid of dimensions a x a (a is easy to change in the class)
generate a pop-up, asking if the player wants to play easy/medium/hard mode
after clicking 'play', do a 3, 2, 1 countdown... then it starts
the first coloured tile appears after self.speed ms
thereafter, every self.speed ms, the game checks to see if the previous tile has been pressed
self.speed reduces in time after every press, given by an exponential-type formula
which will also depend on the difficulty selected
if it hasn't the game ends, and the score is totalled/printed on screen
also need to check if the player misclicks the wrong tile at any time
'''

class ReactionGame:

    # list of class variables (eg tile colour etc - things we won't need to change)
    colour_bg = "black"
    colour_active = "#00f7ff"
    colour_end = "#630a1d"
    # initially going to put grid_size and base_speed here, but later might make them customisable
    grid_size = 5

    def __init__(self, root):
        self.root = root

        root.title("Reaction Grid Game")

    def game_window(self):

        self.button_size = 130

        full_width = self.grid_size * self.button_size + 80
        full_height = self.grid_size * self.button_size + 80

        # monitor_centre_x = int(root.winfo_screenwidth() / 2)
        # monitor_centre_y = int(root.winfo_screenheight() / 2)

        monitor_centre_x = int(root.winfo_screenwidth() / 2 - full_width / 2)
        monitor_centre_y = int(root.winfo_screenheight() / 2 - full_height / 2)

        root.geometry(f"{full_width}x{full_height}+{monitor_centre_x}+{monitor_centre_y}")
        # root.geometry(f"{full_width}x{full_height}")
        # root.eval(f'tk::PlaceWindow {root} center')
        root.minsize(full_width, full_height)

        # creates the frame within which the buttons will be added
        self.frame = Frame(root, padx=20, pady=20)
        # self.frame.place(relx=0.5, rely=0.5)
        self.frame.place(relx=0.5, rely=0.5, anchor=CENTER)

    def game_buttons(self):

        # adjust the font size and this will adjust the size of the buttons (ideally not below about 10)
        self.sizeFont = Font(
            size=20
        )

        self.buttons = []
        self.button_locs = []

        for r in range(self.grid_size):
            for c in range(self.grid_size):
                button_number = r * self.grid_size + c
                button_loc = (c, r)

                # storing the button objects and location data data in two lists
                self.buttons.append(Button(self.frame, width=7, height=3, bg=self.colour_bg,\
                                           command=self.fail_click, font=self.sizeFont))
                self.button_locs.append(button_loc)
                # adding buttons onto the screen
                self.buttons[button_number].grid(column=c, row=r)

    def game_prompt(self):

        self.bg_start_prompt = "grey"
        self.fg_start_prompt = "white"

        self.promptFont1 = Font(
            family="Helvetica",
            size=14,
            weight="bold"
        )

        self.difficulty_prompt = Label(self.frame, width=35, height=14, state=DISABLED,
                                  bg=self.bg_start_prompt, disabledforeground=self.fg_start_prompt,
                                    font=self.promptFont1,
                                    text="Welcome to Reaction Grid! \n\nSelect a difficulty.",
                                    anchor=N, pady=20)

        self.difficulty_prompt.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.difficulty_multipler = IntVar()

        # value = 1 for easy, 2 for medium etc - this value later becomes the difficulty_multiplier.
        self.difficulty_easy = Button(self.difficulty_prompt, text="Easy", font=self.promptFont1,
                                           width=20, anchor=CENTER, command=self.assign_difficulty_easy)
        self.difficulty_medium = Button(self.difficulty_prompt, text="Medium", font=self.promptFont1,
                                             width=20, anchor=CENTER, command=self.assign_difficulty_medium)
        self.difficulty_hard = Button(self.difficulty_prompt, text="Hard", font=self.promptFont1,
                                           width=20, anchor=CENTER, command=self.assign_difficulty_hard)

        self.difficulty_easy.place(relx=0.5, rely=0.43, anchor=CENTER)
        self.difficulty_medium.place(relx=0.5, rely=0.63, anchor=CENTER)
        self.difficulty_hard.place(relx=0.5, rely=0.83, anchor=CENTER)

    def assign_difficulty_easy(self):
        self.game_difficulty = "easy"
        self.base_time = 1200
        self.difficulty_multipler = 1
        self.countdown_start()

    def assign_difficulty_medium(self):
        self.game_difficulty = "medium"
        self.base_time = 1000
        self.difficulty_multipler = 2
        self.countdown_start()

    def assign_difficulty_hard(self):
        self.game_difficulty = "hard"
        self.base_time = 800
        self.difficulty_multipler = 3
        self.countdown_start()

    def countdown_start(self):
        self.difficulty_easy.place_forget()
        self.difficulty_medium.place_forget()
        self.difficulty_hard.place_forget()

        self.countdownFont= Font(
            family="Helvetica",
            size=40,
            weight="bold"
        )

        self.difficulty_prompt.config(text="")
        # sets countdown text to "3". this variable will be reduced by 1 each time
        self.countdown_text = 3
        self.countdown_widget = Label(self.difficulty_prompt, text=self.countdown_text, font=self.countdownFont, bg=self.bg_start_prompt, \
                                    fg="White")
        self.countdown_widget.place(relx=0.5, rely=0.5, anchor=CENTER)
        root.after(1000, self.countdown_continue)

    def countdown_continue(self):
        self.countdown_text -= 1
        if self.countdown_text > 0:
            self.countdown_widget.config(text=self.countdown_text)
            root.after(1000, self.countdown_continue)
        else:
            self.game_start()

    def game_start(self):
        # clears the board
        self.difficulty_prompt.place_forget()

        # sets score and starting info etc
        self.fail_check = False
        # buttons_pressed represents the score
        self.buttons_pressed = 0

        # sets a dummy "last button chosen" so that the self.update_buttons function works
        self.prev_button_choice = random.randrange(len(self.buttons))

        self.update_interval = self.base_time

        # starts the first button update
        self.update_buttons()

    def check_fail(self):
        if self.fail_check == False:
            self.update_buttons()
        else:
            self.fail_click()

    def update_buttons(self):
        # states that there is currently no ongoing "root.after" function
        self.ongoing_timer = None

        # if fail_check is still true by this point, it means the user has not pressed a button
        # in time, so they lose.
        if self.fail_check == True:
            # causes the player to lose
            self.fail_click()

        # sets the fail_check to true -- if it is still true by the time the buttons next update,
        # the user loses the game
        self.fail_check = True

        # resets the previous button back to the default state
        self.buttons[self.prev_button_choice].config(bg=f"{self.colour_bg}", command=self.fail_click)

        self.button_choice = random.randrange(len(self.buttons))
        while self.button_choice == self.prev_button_choice:
            self.button_choice = random.randrange(len(self.buttons))

        # sets this button as the previous button choice
        self.prev_button_choice = copy.copy(self.button_choice)

        # creates/changes the active button
        self.buttons[self.button_choice].config(bg=f"{self.colour_active}", command=self.success_click,\
                                                state=NORMAL)
        self.ongoing_timer = root.after(self.update_interval, self.check_fail)

    def success_click(self):
        self.buttons[self.button_choice].config(bg=f"{self.colour_bg}", command=self.fail_click, \
                                                state=DISABLED)
        # reduces/updates the update_interval
        self.buttons_pressed += 1
        self.update_interval = math.floor(self.base_time * math.e ** (-0.02 * self.difficulty_multipler * self.buttons_pressed))
        # resets the fail check to False again, so the next button update does not trigger
        # the fail condition
        self.fail_check = False
        # print(f"Buttons Pressed: {self.buttons_pressed}")

    def fail_click(self):
        self.fail_check = True

        for button in self.buttons:
            button.config(state=DISABLED, bg="black")

        self.countdown_widget.config(text="YOU LOST!", bg="red")
        # self.countdown_widget.place_forget()
        self.countdown_widget.place(relx=0.5, rely=0.26, anchor=CENTER)
        self.difficulty_prompt.config(bg="red")
        self.difficulty_prompt.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.score_label = Label(self.difficulty_prompt, text=f"Score: {self.buttons_pressed}",\
                                 font=self.countdownFont, fg="white", bg="red")
        self.score_label.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.playAgainFont = Font(
            family="Helvetica",
            size=26,
            weight="bold"
        )

        self.play_again = Button(self.difficulty_prompt, text="Play Again", font=self.playAgainFont,\
                                 command=self.reset_game)
        self.play_again.place(relx=0.5, rely=0.78, anchor=CENTER)

    def reset_game(self):
        # resets the game
        game1.game_window()
        game1.game_buttons()
        game1.game_prompt()

root = Tk()
game1 = ReactionGame(root)
game1.game_window()
game1.game_buttons()
game1.game_prompt()

root.mainloop()