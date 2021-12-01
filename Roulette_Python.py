#Last edit: 19/05/21
import operator
import re
import sqlite3

from datetime import date, datetime
from random import randint
from tkinter import *
from tkinter import messagebox
from tkinter import ttk  #Treeview and style are a ttk widgets therefore we need to import them as ttk

#Open source
try:
    from PIL import ImageTk, Image    #pip install Pillow
    from tkcalendar import Calendar  #pip install tkcalendar
except ModuleNotFoundError:
    print('Please install the required modules using\npip install Pillow\npip install tkcalendar ')
    quit()

"""
Create a database with the name Roulete, it contains two tables Players and History and they have one-to-many relationship respectively.
Table Players will store the data of players while table History will store any transactions such as deposit, widthraw or betting rewards.
The foreign key is field Username in History and it refers to field Username in Players as a primary key.

Each field within the tables is assigned with data type and sometimes a Validation
for example, Balance in table Players is a Real number (floating) and has two validations: Not empty and greater than or equal to 0.
Sqlite3 code is easy to understand as it has many similarities with other RDBMS.
"""
conn = sqlite3.connect('Roulette.db')
conn.execute("PRAGMA foreign_keys = 1")
c = conn.cursor()

c.execute(""" CREATE TABLE IF NOT EXISTS Players (
        Username  TEXT UNIQUE NOT NULL,
        Password  TEXT NOT NULL,
        Email     TEXT NOT NULL,
        Forename  TEXT,
        Surname   TEXT,
        Birth     TEXT,
        Balance   REAL NOT NULL DEFAULT 0,
        CHECK(Balance >= 0),
        PRIMARY KEY(Username)
            )""")

c.execute(""" CREATE TABLE IF NOT EXISTS History(
        Username  TEXT NOT NULL,
        Credit    REAL NOT NULL,
        BetType   TEXT,
        TimeDate  TEXT,
        FOREIGN KEY (Username) REFERENCES Players (Username)
            )""")

"""
The following functions are used to interact with the database such as adding new records or retrieve/query a specific record.
Notice that Python variables are not added directly but instead in a form of dictionary, and this is to prevent bad input
and hence a SQL injection attack.
"""

# Add and register a new player to table Players
def insert_player(Username, Password, Email, Forename, Surname, Birth, Balance=0):
    with conn:
        c.execute("INSERT INTO Players Values(:Username, :Password, :Email, :Forename, :Surname, :Birth, :Balance)",
        {'Username':Username, 'Password':Password, 'Email':Email, 'Forename':Forename, 'Surname':Surname, 'Birth':Birth, 'Balance':Balance})

# Update the balance of the specified username, in table Players, by adding the inserted credit
def update_balance(Username, Credit):
    with conn:
        c.execute("""UPDATE Players SET Balance = Balance + :Credit
                     WHERE Username=:Username
        """, {'Username':Username, 'Credit':Credit})

# Retrieve the specified username record in table Players and return the record as a list
def get_player(Username):
    c.execute("SELECT * FROM Players WHERE Username=:Username", {'Username':Username})
    return c.fetchall()

# Query the balance of the specified username by calling get_player function and extract the balance using list slicing
def get_balance(Username):
    return get_player(Username)[-1][-1]

# call function update_balance then add a transaction as a record to table Hisotry
def insert_transaction(Username, Credit, BetType=None):
    update_balance(Username, Credit)
    with conn:
        c.execute("INSERT INTO History VALUES(:Username, :Credit, :BetType, datetime('now', 'localtime'))",
        {'Username':Username, 'Credit':Credit, 'BetType': BetType})

# Query all records in table History for the specified username and return them as a list of tuples
# In other words, return all transactions for the specified username
def get_history(Username):
    c.execute("SELECT BetType, Credit, TimeDate FROM History WHERE Username=:Username", {'Username':Username})
    return c.fetchall()

"""
The following functions represent the betting options.
Every function has a similar process:
        0-Define label text variables in tkinter GUI as a global, so the variable can be called from other functions
        1-Retrieve the bet amount (aka staked amount) and player guess which was inserted in tkinter GUI
        2-Get a random number from 1 to 36 using randint in random library
        3-if the inserted data does not matche the validations such as the amount user bets is not a number or player guess is invalid,
        then create a label text in tkinter GUI informing the user to insert valid values
        4-If validation is passed: The code will compare player guess with the random generated number
        5-Depending on the comparison outcome,
            1-the code will create a label text in tkinter GUI informing if player won or not and include the value of the random generated number
            2-Call insert_transaction function to add the betting rewards or remove the stake from player balance
"""

#Single Number bet option
def single_num(Username, Bet, UserGuess):
    global UserBetValidationLabel
    global UserGuessValidationLabel
    global ResultLabel

    RandValue = randint(1, 36)
    try:
        Bet = float(Bet)
        UserGuess = int(UserGuess)

        if UserGuess == RandValue:
            insert_transaction(Username, Bet*36, 'single_num')
            UserGuessEntry.delete(0, END)
            UserBetEntry.delete(0, END)
            ResultLabel = Label(Game, text=f'Congratulation, the ball landed on {RandValue}', font='Arial 18 bold', fg='#f00')
            ResultLabel.place(x=400, y=250)

        elif UserGuess in range(1, 37):
            insert_transaction(Username, Bet*-1, 'single_num')
            UserGuessEntry.delete(0, END)
            UserBetEntry.delete(0, END)
            ResultLabel = Label(Game, text=f'Sorry, the ball landed on {RandValue}', font='Arial 18 bold', fg='#f00')
            ResultLabel.place(x=400, y=250)

        else:
            UserGuessEntry.delete(0, END)
            UserGuessValidationLabel = Label(UserBetFrame, text="*You can choose only from 1 to 36, try again", fg="#f00")
            UserGuessValidationLabel.grid(row=0, column=2)

    except ValueError:
        if not UserGuess.isdigit():
            UserGuessEntry.delete(0, END)
            UserGuessValidationLabel = Label(UserBetFrame, text="*You can choose only from 1 to 36", fg="#f00")
            UserGuessValidationLabel.grid(row=0, column=2)

        if not str(Bet).replace('.', '', 1).isdigit():
            UserBetEntry.delete(0, END)
            UserBetValidationLabel = Label(UserBetFrame, text="*Bet should be numeric", fg="#f00")
            UserBetValidationLabel.grid(row=1, column=2)

#Odd or Even bet option
def odd_even(Username, Bet, UserGuess):
    global UserBetValidationLabel
    global UserGuessValidationLabel
    global ResultLabel

    RandValue = randint(1, 36)
    try:
        Bet = float(Bet)
        UserGuess = UserGuess.lower()

        if UserGuess == ('even' if RandValue % 2 == 0 else 'odd'):
            insert_transaction(Username, Bet*2, 'odd_even')
            UserGuessEntry.delete(0, END)
            UserBetEntry.delete(0, END)
            ResultLabel = Label(Game, text=f'Congratulation, the ball landed on {RandValue}', font='Arial 18 bold', fg='#f00')
            ResultLabel.place(x=400, y=250)

        elif UserGuess in ('even', 'odd'):
            insert_transaction(Username, Bet*-1, 'odd_even')
            UserGuessEntry.delete(0, END)
            UserBetEntry.delete(0, END)
            ResultLabel = Label(Game, text=f'Sorry, the ball landed on {RandValue}', font='Arial 18 bold', fg='#f00')
            ResultLabel.place(x=400, y=250)


        else:
            UserGuessEntry.delete(0, END)
            UserGuessValidationLabel = Label(UserBetFrame, text="*You can choose only odd or even, try again", fg="#f00")
            UserGuessValidationLabel.grid(row=0, column=2)

    except ValueError:
        UserBetEntry.delete(0, END)
        UserBetValidationLabel = Label(UserBetFrame, text="*Bet should be numeric", fg="#f00")
        UserBetValidationLabel.grid(row=1, column=2)

#High or low bet option
def high_low(Username, Bet, UserGuess):
    global UserBetValidationLabel
    global UserGuessValidationLabel
    global ResultLabel

    RandValue = randint(1, 36)
    try:
        Bet = float(Bet)
        UserGuess = UserGuess.lower()

        if UserGuess == ('low' if RandValue <= 18 else 'high'):
            insert_transaction(Username, Bet*2, 'high_low')
            UserGuessEntry.delete(0, END)
            UserBetEntry.delete(0, END)
            ResultLabel = Label(Game, text=f'Congratulation, the ball landed on {RandValue}', font='Arial 18 bold', fg='#f00')
            ResultLabel.place(x=400, y=250)

        elif UserGuess in ('low', 'high'):
            insert_transaction(Username, Bet*-1, 'high_low')
            UserGuessEntry.delete(0, END)
            UserBetEntry.delete(0, END)
            ResultLabel = Label(Game, text=f'Sorry, the ball landed on {RandValue}', font='Arial 18 bold', fg='#f00')
            ResultLabel.place(x=400, y=250)

        else:
            UserGuessEntry.delete(0, END)
            UserGuessValidationLabel = Label(UserBetFrame, text="*You can choose only high or low, try again", fg="#f00")
            UserGuessValidationLabel.grid(row=0, column=2)

    except ValueError:
        UserBetEntry.delete(0, END)
        UserBetValidationLabel = Label(UserBetFrame, text="*Bet should be numeric", fg="#f00")
        UserBetValidationLabel.grid(row=1, column=2)

# Merge sort algorithm, the operator variable represents the type of sort i.e. Ascending or Descending
def merge_sort(SortList, Operator):
    OperatorFunction = { ">": operator.gt, "<": operator.lt }

    if len(SortList) > 1:
        # Divide orginal list
        Middle = len(SortList) // 2
        Left = SortList[:Middle]
        Right = SortList[Middle:]

        # Call each half recursively
        merge_sort(Left, Operator)
        merge_sort(Right, Operator)

        # Two Counters for the two halves
        x = 0
        y = 0

        # Counter for the orginal list
        i = 0

        while x < len(Left) and y < len(Right):
            # if operator variable is '<' then it is ascending sort
            # if operator variable is '>' then it is descending sort
            if OperatorFunction[Operator](Left[x] [1], Right[y] [1]):
              #Use the array from left half
              SortList[i] = Left[x]
              x += 1

            else:
                #Use the array from right half
                SortList[i] = Right[y]
                y += 1

            i += 1

        # For all the remaining arrays
        while x < len(Left):
            SortList[i] = Left[x]
            x += 1
            i += 1

        while y < len(Right):
            SortList[i]=Right[y]
            y += 1
            i += 1

"""
The following functions are for the GUI, there are three main pages:
        1-Login page:        the player enter his username and password to access Game page
        2-Registration page: the player can register a new account
        3-Gaame page:        the main page where the player can:
                                    1-choose a bet option and insert a stake
                                    2-View his data such as username, fullname, birth date and balance
                                    3-Desposit or withdraw credit
                                    4-View the results of previous games and transactions
                                    5-View a guide on how the Game works
                                    6-Log out from the game

Notice in each page we define variables scope and the window and its geometry, then any widget in the window
and where it is located. In this software we used the three of tkinter built-in layout managers: pack, grid and place.
"""

#Check if any of the Validation labels exsit and remove them when the function is called
def destroy_label():
    if 'LoginLabel' in globals():
        LoginLabel.destroy()
    if 'WrongUserLbael' in globals():
        WrongUserLbael.destroy()
    if 'WrongPassLbael' in globals():
        WrongPassLbael.destroy()
    if 'UserValidationLabel' in globals():
        UserValidationLabel.destroy()
    if 'PassValidationLabel' in globals():
        PassValidationLabel.destroy()
    if 'EmailValidationLabel' in globals():
        EmailValidationLabel.destroy()
    if 'ForenameValidationLabel' in globals():
        ForenameValidationLabel.destroy()
    if 'SurnameValidationLabel' in globals():
        SurnameValidationLabel.destroy()
    if 'BirthValidationLabel' in globals():
        BirthValidationLabel.destroy()
    if 'PassValidationLabel' in globals():
        PassValidationLabel.destroy()
    if 'UserBetValidationLabel' in globals():
        UserBetValidationLabel.destroy()
    if 'UserGuessValidationLabel' in globals():
        UserGuessValidationLabel.destroy()
    if 'AmountValidationLabel' in globals():
        AmountValidationLabel.destroy()
    if 'ResultLabel' in globals():
        ResultLabel.destroy()

#Login page, the first page appears to the player
def login_page():
    # Defining variables scope
    global UsernameEntry
    global PasswordEntry
    global LoginButton
    global Root
    global LoginFrame
    global Counter


    Counter = 3 #Number of tries

    #Defining the login page window
    Root = Tk()
    Root.geometry("600x600")
    Root.title("Login page")

    #Background picture
    RCasino = ImageTk.PhotoImage(Image.open("Casino.jpg"))
    Imagebg = Label(Root, image=RCasino)
    Imagebg.place(x=0, y=0, relwidth=1, relheight=1)


    #Defining a frame for the labels, entry boxes and buttons.
    LoginFrame = Frame(Root, bg='#3eb2f5')
    LoginFrame.place(x=50, y=100)

    #Labels
    UsernameLabel  = Label(LoginFrame, text='Username:')
    PasswordLabel  = Label(LoginFrame, text='Password:')
    UsernameEntry  = Entry(LoginFrame, width=40, borderwidth=4)

    #Entry boxes and buttins
    PasswordEntry  = Entry(LoginFrame, width=40, borderwidth=4, show='*')
    LoginButton    = Button(LoginFrame, text='Login', width="20", borderwidth=4, command=login_verify)
    RegisterButton = Button(LoginFrame, text='Register', width="20", borderwidth=4, command=register_page)

    #Location of widgets according to each other in the frame 'LoginFrame'
    UsernameLabel.grid(row=0, column=0, pady=10, padx=10)
    UsernameEntry.grid(row=0, column=1, pady=10)

    PasswordLabel.grid(row=1, column=0, pady=10, padx=10)
    PasswordEntry.grid(row=1, column=1, pady=10)

    LoginButton.grid(row=2, column=1, pady=20)
    RegisterButton.grid(row=3, column=1, pady=10)

    Root.mainloop()

#Verifing that the data player enters are correct
def login_verify():
    #Defining variables scope
    global LoginLabel
    global WrongUserLbael
    global WrongPassLbael
    global Counter
    destroy_label()

    #Check that the player has entered the password and username
    if not UsernameEntry.get() or not PasswordEntry.get():
        LoginLabel = Label(LoginFrame, text="**Please enter your password and username", fg='#f00')
        LoginLabel.grid(row=4, column=1, pady=10)
        UsernameEntry.delete(0, END)
        PasswordEntry.delete(0, END)

    else:
        #Check if Username exist in the database
        if len(get_player(UsernameEntry.get())) == 0:
            WrongUserLbael = Label(LoginFrame, text='**Username is incorrect', fg='#f00')
            WrongUserLbael.grid(row=0, column=2, padx=20)
            UsernameEntry.delete(0, END)
            PasswordEntry.delete(0, END)

        #Check that the password is correct
        elif get_player(UsernameEntry.get())[0][1] == PasswordEntry.get():
            PasswordEntry.delete(0, END)
            #Declaration message appears to warn the user after a successful login
            Response = messagebox.askyesno('Declaration',
             "I understand that I can lose all of my funds when gambling as the odds are against me.\n I understand that I am not diagnosed with gambling addiction.")

            #Response == True if user click yes
            if Response:
                game_page()
            else:
                print('Then buy crypto rug pulls better than gambling, xD')

        #If password is incorrect
        elif get_player(UsernameEntry.get())[0][1] != PasswordEntry.get():
            WrongPassLbael = Label(LoginFrame, text='**Password is incorrect', fg='#f00')
            WrongPassLbael.grid(row=1, column=2, padx=20)
            PasswordEntry.delete(0, END)

            #Count the number of tries and prompt a window Warning the user how many tries left
            Counter -= 1
            if Counter == 0:
                LoginButton.config(state='disabled')
                messagebox.showwarning('Password incorrect', f'Please contact the casino to reset your password')
            else:
                WarningMessage = f"{Counter} tries" if Counter !=1 else f"one try"
                messagebox.showwarning('Password incorrect', f'You have {WarningMessage} left')

def register_page():
    #Defining variables scope
    global Register
    global RUsernameEntry
    global RPasswordEntry
    global REmailEntry
    global RForenameEntry
    global RSurnameEntry
    global RBirthEntry
    global RBalanceEntry

    #Navigate from Registration page to the login page
    def register_to_root():
        Register.destroy()
        Root.deiconify()

    #Calendar for inserting birth date
    def birth():
        DateSelection = Toplevel(Register)
        DateSelection.title('Calendar')
        # Register.withdraw()

        def insert_date():

            RBirthEntry.config(state="normal")
            RBirthEntry.delete(0, END)
            RBirthEntry.insert(0, Date.selection_get())
            RBirthEntry.config(state='disabled')
            DateSelection.destroy()
            # print(Date.selection_get())

        Date = Calendar(DateSelection,
                       font="Arial 20", selectmode='day',
                       cursor="hand1", year=date.today().year, month=date.today().month,
                       day=date.today().day)


        Date.pack(fill="both", expand=True)
        Sub = Button(DateSelection, text='Select date',width=20, command=insert_date)
        Sub.pack()

        DateSelection.mainloop()

    #Validtion points
    def validation():
        destroy_label()

        """
        Check if username is not taken by another player previously,
        username should be 4 characters long at least and contain only alphabetic letters and numbers
        """
        def username_validation():
            global UserValidationLabel

            if len(get_player(RUsernameEntry.get())) != 0:
                UserValidationLabel = Label(RegisterFrame, text='*Username alread exist, please choose another one', fg="#f00")
                UserValidationLabel.grid(row=0, column=2, padx=10)

            elif len(RUsernameEntry.get()) < 4:
                UserValidationLabel = Label(RegisterFrame, text='*Username should be 4 characters long at least', fg="#f00")
                UserValidationLabel.grid(row=0, column=2, padx=10)

            elif not RUsernameEntry.get().isalnum():
                UserValidationLabel = Label(RegisterFrame, text='*Username should contain only alphabetic letters and numbers', fg="#f00")
                UserValidationLabel.grid(row=0, column=2, padx=10)
            else:
                return True


        """
        Check if password is 6-10 characters long and contain at least:
        one uppercase, one lowercase, one digit and one special character. Moreover, does not contain a whitespace.
        """
        def passowrd_validation():
            global PassValidationLabel


            if (len(RPasswordEntry.get()) < 6) or (len(RPasswordEntry.get()) > 10):
                PassValidationLabel = Label(RegisterFrame, text='*Password should be 6-10 characters long', fg="#f00")
                PassValidationLabel.grid(row=1, column=2)
            elif not re.search("[A-Z]", RPasswordEntry.get()):
                PassValidationLabel = Label(RegisterFrame, text='*Password should contain one uppercase at least', fg="#f00")
                PassValidationLabel.grid(row=1, column=2)
            elif not re.search("[a-z]", RPasswordEntry.get()):
                PassValidationLabel = Label(RegisterFrame, text='*Password should contain one lowercase at least', fg="#f00")
                PassValidationLabel.grid(row=1, column=2)
            elif not re.search("[0-9]", RPasswordEntry.get()):
                PassValidationLabel = Label(RegisterFrame, text='*Password should contain one digit at least', fg="#f00")
                PassValidationLabel.grid(row=1, column=2)
            elif not re.search("[#$%&(_)*-]", RPasswordEntry.get()):
                PassValidationLabel = Label(RegisterFrame, text='*Password should contain at least one special characters from #$%&(_)*-', fg="#f00")
                PassValidationLabel.grid(row=1, column=2)
            elif re.search("\s", RPasswordEntry.get()):
                PassValidationLabel = Label(RegisterFrame, text='*Password should not contain space', fg="#f00")
                PassValidationLabel.grid(row=1, column=2)
            else:
                return True


        #Check if email in a correct format: example@domain.com
        def email_validation():
            global EmailValidationLabel
            pattern = re.compile('^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$')

            if REmailEntry.get() == 'example@domain.com' or len(REmailEntry.get()) == 0:
                EmailValidationLabel = Label(RegisterFrame, text='*Please enter your email', fg="#f00")
                EmailValidationLabel.grid(row=2, column=2, padx=10)
                REmailEntry.delete(0, END)

            elif  pattern.search(REmailEntry.get()) is None:
                EmailValidationLabel = Label(RegisterFrame, text='*Please enter your email in a correct format: example@domain.com', fg="#f00")
                EmailValidationLabel.grid(row=2, column=2, padx=10)
                REmailEntry.delete(0, END)
            else:
                return True


        """
        Check if forename and surname contain only alphabetic letters (with exception for ‘.’ string)
        and are not more than 10 characters long
        """
        def forename_validation():
            global ForenameValidationLabel

            if len(RForenameEntry.get()) == 0:
                 ForenameValidationLabel = Label(RegisterFrame, text='*Please enter your forename ', fg="#f00")
                 ForenameValidationLabel.grid(row=3, column=2, padx=10)

            elif len(RForenameEntry.get()) >= 10:
                 ForenameValidationLabel = Label(RegisterFrame, text='*Forename can not be more than 10 characters', fg="#f00")
                 ForenameValidationLabel.grid(row=3, column=2, padx=10)

            elif not RForenameEntry.get().replace('.', '').isalpha():
                ForenameValidationLabel = Label(RegisterFrame, text='*Forename should only contain alphabetic letters ', fg="#f00")
                ForenameValidationLabel.grid(row=3, column=2, padx=10)

            else:
                return True
        def surname_validation():
            global SurnameValidationLabel

            if len(RSurnameEntry.get()) == 0:
                 SurnameValidationLabel = Label(RegisterFrame, text='*Please enter your Surname ', fg="#f00")
                 SurnameValidationLabel.grid(row=4, column=2, padx=10)

            elif len(RSurnameEntry.get()) >= 10:
                 SurnameValidationLabel = Label(RegisterFrame, text='*Surname can not be more than 10 characters ', fg="#f00")
                 SurnameValidationLabel.grid(row=4, column=2, padx=10)

            elif not RSurnameEntry.get().replace('.', '').isalpha():
                SurnameValidationLabel = Label(RegisterFrame, text='*Surname should only contain alphabetic letters ', fg="#f00")
                SurnameValidationLabel.grid(row=4, column=2, padx=10)
            else:
                return True

        #Check if Player age is 18 or above
        def birth_validation():
            global BirthValidationLabel

            CurrentDate = date.today()
            try:
                BirthDate = datetime.strptime(RBirthEntry.get(), '%Y-%m-%d').date()
                UserAge = CurrentDate.year - BirthDate.year - ((CurrentDate.month, CurrentDate.day) < (BirthDate.month, BirthDate.day))
                if UserAge < 18:
                    BirthValidationLabel = Label(RegisterFrame, text='*User should be 18 or over', fg="#f00")
                    BirthValidationLabel.grid(row=5, column=2)
                else:
                    return True

            except ValueError:
                BirthValidationLabel = Label(RegisterFrame, text='*Please use the Calendar to input your birth date', fg="#f00")
                BirthValidationLabel.grid(row=5, column=2)


        #Calling validation functions and check that all of them are met
        if (username_validation() and passowrd_validation()
            and email_validation() and forename_validation()
            and surname_validation() and birth_validation()):
            #Add the new player to the database
            insert_player(RUsernameEntry.get(), RPasswordEntry.get(),
                          REmailEntry.get(), RForenameEntry.get(),
                          RSurnameEntry.get(), RBirthEntry.get())
            #Message congratualing the player of registration
            messagebox.showinfo('Confirming registration', 'Congratulation you are now registered with us, please login with your account')
            register_to_root()

    #Removing the login page and defining the Registration page window
    Root.withdraw()
    Register = Toplevel(Root)
    Register.geometry("900x600")
    Register.title("Registration page")

    #Background Image
    RCasino = ImageTk.PhotoImage(Image.open("Casino.jpg"))
    Imagebg = Label(Register, image=RCasino)
    Imagebg.place(x=0, y=0, relwidth=1, relheight=1)

    #The frame where the labels, entries, buttons are placed
    RegisterFrame = Frame(Register, bg='#3eb2f5')
    RegisterFrame.place(x=200, y=10)
    font ='Arial 14'
    #Defining labels
    RUsernameLabel = Label(RegisterFrame, text='Username:  ', font=font)
    RPasswordLabel = Label(RegisterFrame, text='Password:  ', font=font)
    REmailLabel    = Label(RegisterFrame, text='Email:  ', font=font)
    RForenameLabel = Label(RegisterFrame, text='Forename:  ', font=font)
    RSurnameLabel  = Label(RegisterFrame, text='Surname:  ', font=font)
    RBirthLabel    = Label(RegisterFrame, text='Birth:  ', font=font)
    RBalanceLabel  = Label(RegisterFrame, text='Balance:  ', font=font)
    #Defining Registration page entry boxes
    RUsernameEntry = Entry(RegisterFrame, width=40, borderwidth=3)
    RPasswordEntry = Entry(RegisterFrame, width=40, borderwidth=3, show='*')
    REmailEntry    = Entry(RegisterFrame, width=40, borderwidth=3)
    RForenameEntry = Entry(RegisterFrame, width=40, borderwidth=3)
    RSurnameEntry  = Entry(RegisterFrame, width=40, borderwidth=3)
    RBirthEntry    = Entry(RegisterFrame, width=30, borderwidth=3, state='disabled')
    RBalanceEntry  = Entry(RegisterFrame, width=40, borderwidth=3, state='disabled')
    #Defining buttons and the command called when they are pressed
    RBirthButton = Button(RegisterFrame, text='*', width=2,font=font, height=1, command=birth)
    RRegister = Button(RegisterFrame, text='Register',font=font, command=validation)
    RBack = Button(RegisterFrame, text='Back',font=font, command=register_to_root)

    REmailEntry.insert(0, 'example@domain.com')

    #Location of widgets in the page
    RUsernameLabel.grid(row=0, column=0, pady=20, padx=10)
    RUsernameEntry.grid(row=0, column=1)

    RPasswordLabel.grid(row=1, column=0, pady=20, padx=10)
    RPasswordEntry.grid(row=1, column=1)

    REmailLabel.grid(row=2, column=0, pady=20, padx=10)
    REmailEntry.grid(row=2, column=1)

    RForenameLabel.grid(row=3, column=0, pady=20, padx=10)
    RForenameEntry.grid(row=3, column=1)

    RSurnameLabel.grid(row=4, column=0, pady=20, padx=10)
    RSurnameEntry.grid(row=4, column=1)

    RBirthLabel.grid(row=5, column=0, pady=5)
    RBirthEntry.grid(row=5, column=1)
    RBirthButton.place(x=350, y=345)

    RBalanceLabel.grid(row=6, column=0, pady=20, padx=10)
    RBalanceEntry.grid(row=6, column=1)

    RRegister.grid(row=7, column=1,pady=30, padx=5)
    RBack.grid(row=8, column=1)

    Register.mainloop()

#Check above comments about the game page
def game_page():
    #defining variables scope
    global Game
    global UserBetFrame
    global UserBetEntry
    global UserGuessEntry

    #Removing the login page and defining the Game page window
    Root.withdraw()
    Game = Toplevel(Root)
    Game.geometry('1100x600')
    Game.title('Roulette')

    def setting_page():
        Game.withdraw()
        Setting = Toplevel(Game)
        Setting.geometry('600x500')
        Setting.title('Setting')

        #Navigating from setting page to game page
        def setting_to_game():
            Setting.destroy()
            Game.deiconify()
        #Querying user data from the database
        PlayerInfo = get_player(UsernameEntry.get())[0]

        #Widgets and their location within the page
        RecordsFramee = LabelFrame(Setting, bd=0)
        RecordsFramee.place(x=30, y=30, width=150, height=330)
        UserLabel = Label(RecordsFramee, text='Username:', font='Arial 12').pack(pady=20)
        PassLabel = Label(RecordsFramee, text='Password:', font='Arial 12').pack(pady=20)
        EmailLabel = Label(RecordsFramee, text='Email:', font='Arial 12').pack(pady=20)
        FullNameLabel = Label(RecordsFramee, text='Full Name:', font='Arial 12').pack(pady=20)
        BirthLabel = Label(RecordsFramee, text='Birth Date:', font='Arial 12').pack(pady=20)

        RecordsFramee = LabelFrame(Setting, bd=0)
        RecordsFramee.place(x=180, y=30, width=400, height=330)
        UserLabel = Label(RecordsFramee, text=PlayerInfo[0], font='Arial 12 bold').pack(pady=20, anchor=W)
        PassLabel = Label(RecordsFramee, text=''.join(['*' for i in PlayerInfo[1]]), font='Arial 12 bold').pack(pady=20, anchor=W)
        EmailLabel = Label(RecordsFramee, text=PlayerInfo[2], font='Arial 12 bold').pack(pady=20, anchor=W)
        FullNameLabel = Label(RecordsFramee, text=' '.join(PlayerInfo[3:5]), font='Arial 12 bold').pack(pady=20, anchor=W)
        BirthLabel = Label(RecordsFramee, text=PlayerInfo[5], font='Arial 12 bold').pack(pady=20, anchor=W)

        InfoLabel= Label(Setting, text='If you wish to change any of the above data or delete \nyour account, then please contact the casino directly', font='Arial 16')
        InfoLabel.place(x=30, y=370)

        #Back button when clicked it call function "setting_to_game"
        BackButton = Button(Setting, text='Back', font='Arial 14', command=setting_to_game)
        BackButton.place(x=200, y=430)
        Setting.mainloop()

    def credit_page():
        Game.withdraw()
        Credit = Toplevel(Game)
        Credit.geometry('600x500')
        Credit.title('Credit')

        def credit_to_game():
            Credit.destroy()
            BalanceLabel.config(text=f"Balance: ${get_balance(UsernameEntry.get())}")
            Game.deiconify()

        def add_credit(Type):
            global AmountValidationLabel
            destroy_label()

            try:
                if float(AmountEntry.get()) <= 0:
                    AmountValidationLabel = Label(Credit,  text="**Please enter a valid amount in usd", fg='#f00')
                    AmountValidationLabel.place(x=400, y=300)
                    AmountEntry.delete(0, END)
                else:
                    insert_transaction(UsernameEntry.get(), float(AmountEntry.get())*Type)
                    DBalanceLabel.config(text=f"Balance: ${get_balance(UsernameEntry.get())}")
                    AmountEntry.delete(0, END)

            #sqlite3.IntegrityError ia raised when the player try to withdraw more than his balance
            except (sqlite3.IntegrityError, ValueError):
                AmountValidationLabel = Label(Credit,  text="**Please enter a valid amount in usd", fg='#f00')
                AmountValidationLabel.place(x=400, y=300)
                AmountEntry.delete(0, END)


        DBalanceLabel = Label(Credit, text=f"Your Balance: ${get_balance(UsernameEntry.get())}", font="Arial 16")
        DBalanceLabel.place(x=50, y=20)
        GuideLable = Label(Credit, text='Warning! please refer to the guide page \non how deposit and withdraw work\n otherwise you risk restricting your account',
        font="Arial 21", fg="#f00")
        GuideLable.place(x=50, y=80)

        AmountLabel = Label(Credit, text='Amount in USD:', font="Arial 14")
        AmountEntry = Entry(Credit)
        DepositButton =Button(Credit, text="Deposit", font="Arial 14", command=lambda: add_credit(1))
        WithdrawButton =Button(Credit, text="Withdraw", font="Arial 14", command=lambda: add_credit(-1))
        BackButton = Button(Credit, text='Back', font="Arial 14", command=credit_to_game)

        AmountLabel.place(x=150, y=300)
        AmountEntry.place(x=300, y=300)
        DepositButton.place(x=200, y=350)
        WithdrawButton.place(x=300, y=350)
        BackButton.place(x=250, y=400)

        Credit.mainloop()

    def history_page():
        Game.withdraw()

        History = Toplevel(Game)
        History.geometry("900x700")
        History.title('Hisotry page')

        #defining the frame for GUI table
        TreeFrame = Frame(History)
        TreeFrame.place(x=0, y=100, width=900, height=600)
        #Define the style of the GUI table
        Style = ttk.Style()
        Style.theme_use("clam")
        #Defining scroll bar for the GUI table, so user can navigate
        tree_scroll = Scrollbar(TreeFrame)
        tree_scroll.pack(side=RIGHT, fill=Y)

        #This function deletes the data in the GUI table
        def delete_data():
            for i in TableData.get_children():
                TableData.delete(i)

        #This function retrieve the data in the GUI table before calling delete_data
        #The data is stored as a list of tuples
        def get_table_data():
            global Data
            Data = list()
            for line in TableData.get_children():
                Data.append(tuple(TableData.item(line)['values']))
            delete_data()

        #filtering the data in the table according to user preference
        def table_filter(Type):
            get_table_data()
            if Type == 'Games':
                Holding = filter(lambda List: List[0] is not None, Data)
            else:
                Holding = filter(lambda List: List[0] is None, Data)

            i = 0
            while True:
                try:
                    Place = next(Holding)
                except StopIteration:
                    break
                TableData.insert(parent='', index='end', iid=i, text="", values=(i, Place[0], Place[1], Place[2]))
                i += 1

        #Return to game page
        def history_to_game():
            History.destroy()
            Game.deiconify()

        #Sort the data for the user according to his preference (Ascending or Descending)
        def sort(Operator):
            # global Data
            get_table_data()
            merge_sort(Data, Operator)

            for i in range(len(Data)):
                TableData.insert(parent='', index='end', iid=i, text="", values=(i, Data[i][0], Data[i][1], Data[i][2]))

        #Retrieve orginal data (without filtering or sorting) from the Hisotry table and insert data to a table in the GUI
        def orginal_table():
            global Data
            delete_data()

            Data = get_history(UsernameEntry.get())
            for i in range(len(Data)):
            	TableData.insert(parent='', index='end', iid=i, text="", values=(i, Data[i][0], Data[i][1], Data[i][2]))

        #Defining the GUI table
        TableData = ttk.Treeview(TreeFrame, yscrollcommand=tree_scroll.set, selectmode="extended")
        tree_scroll.config(command=TableData.yview)

        #Defining the GUI table columns/rows and their size
        TableData['columns'] = ('Row', "BetType", "Credit", "TimeDate")
        TableData.column("#0", width=0, stretch=NO)
        TableData.column("Row", anchor=CENTER, width=100, minwidth=100)
        TableData.column("BetType", anchor=CENTER, width=100, minwidth=100)
        TableData.column("Credit", anchor=CENTER, width=140, minwidth=100)
        TableData.column("TimeDate", anchor=CENTER, width=140, minwidth=140)
        TableData.heading("#0", text="", anchor=W)
        TableData.heading("Row", text="Row", anchor=CENTER)
        TableData.heading("BetType", text="Game", anchor=CENTER)
        TableData.heading("Credit", text="Credit", anchor=CENTER)
        TableData.heading("TimeDate", text="Date Time", anchor=CENTER)

        #Clear sorting and filtering
        ClearButton = Button(History, text='Clear', command=orginal_table)
        ClearButton.place(x=20, y=10)
        #Return to game page
        BackButton = Button(History, text='Back', command=history_to_game)
        BackButton.place(x=20, y=60)

        #Ascending and Descending sort buttons and their location in the window
        ASortButton = Button(History, text='Ascending orde of credit', command=lambda: sort('<'))
        ASortButton.place(x=450, y=10)
        DSortButton = Button(History, text='Descending orde of credit', command=lambda: sort('>'))
        DSortButton.place(x=450, y=60)

        #filtering buttons and their location in the window
        ShowGamestButton = Button(History, text='Show games', command=lambda: table_filter('Games'))
        ShowGamestButton.place(x=250, y=10)
        ShowTransactButton = Button(History, text='Show Withdraws/Deposits', command=lambda: table_filter('Deposit/Withdraws'))
        ShowTransactButton.place(x=250, y=60)


        #Get the records for the specfied username in table History
        Data = get_history(UsernameEntry.get())
        orginal_table()

        TableData.pack(side=TOP, fill=BOTH, expand=1)
        History.mainloop()

    def guide():
        #Notice that guide page does not remove the game page
        Guide = Toplevel(Game)
        Guide.geometry('800x500')
        Guide.title('How to play')
        Label(Guide, text="""
        Single Number: In this bet you need to choose a number from 1 to 36,
        if the roulette landed on your guess then you will be rewarded 36 times your bet amount\n

        Even or Odd: In this bet you need to choose even or odd,
        if the ball landed on a number matches you bet you will be rewarded twice your bet amount\n

        High Low; In this bet you need to choose high or low (1 <= low <=18, 19 <= high <= 36 )
        if the ball landed on a number matches you bet you will be rewarded twice your bet amount\n

        You can deposit or withdraw credit by clicking on account dropdown menu and choose Credit,
        please notice the casino has the right to disable your account if suspicious activities were seen.\n

        Please notice that whenver you make a deposit you will need to head to the casino website to pay it,
        otherwise any rewards profited from the betting are not guaranteed.\n
        After withdrawing credit please head to the casino website to complete the transaction manually,
        expect the widthrawn credit to reach your bank account wihtin 5-10 working days
        and that's to confirm that you did not violate any rules
        """, font='Arial 12', fg="#F00").pack()
        Guide.mainloop()

    #When called it terminate the software
    def log_out():
        quit()


    def bet_type(function):
        global UserBetValidationLabel
        global UserGuessValidationLabel
        destroy_label()

        #Check that user has inserted his guess
        if len(UserGuessEntry.get()) == 0:
            UserGuessValidationLabel = Label(UserBetFrame, text="*Please enter your guess", fg="#f00")
            UserGuessValidationLabel.grid(row=0, column=2)
        #Check that user inserted a bet (stake)
        elif len(UserBetEntry.get()) == 0 or UserBetEntry.get() == '0':
            UserBetValidationLabel = Label(UserBetFrame, text="*Please enter your bet", fg="#f00")
            UserBetValidationLabel.grid(row=1, column=2)

        else:
            try:
                #Depending on the type of bet, the code will run the suitable function:single_num, odd_even or high_low
                function(UsernameEntry.get(), UserBetEntry.get(), UserGuessEntry.get())
                #Update player balance in the game window
                BalanceLabel.config(text=f"Balance: ${get_balance(UsernameEntry.get())}")

            #sqlite3.IntegrityError ia raised when the player try to stake more than his balance
            except sqlite3.IntegrityError:
                UserBetValidationLabel = Label(UserBetFrame, text="*Your balance is insufficient, please deposit\n or decrease your bet", fg="#f00")
                UserBetValidationLabel.grid(row=1, column=2)
                UserBetEntry.delete(0, END)


    #The tilte label and its location
    TitleLable = Label(Game, text="Game of Chance", font="Gabriola 48")
    TitleLable.place(x=400, y=0)

    #Defining a menu of buttons so the user can navigate to the choosen page
    AccountMenu = Menubutton(Game, text="Account", font="Arial 20", bg='grey')
    AccountMenu.menu = Menu(AccountMenu, tearoff=False)
    AccountMenu['menu'] = AccountMenu.menu

    AccountMenu.menu.add_command(label='Setting', font="Arial 16", command=setting_page)
    AccountMenu.menu.add_separator() #This adds a small line between each button
    AccountMenu.menu.add_command(label='Credit', font="Arial 16", command=credit_page)
    AccountMenu.menu.add_separator()
    AccountMenu.menu.add_command(label='History', font="Arial 16", command=history_page)
    AccountMenu.menu.add_separator()
    AccountMenu.menu.add_command(label='Guide', font="Arial 16", command=guide)
    AccountMenu.menu.add_separator()
    AccountMenu.menu.add_command(label='Log out', font="Arial 16", command=log_out)

    AccountMenu.place(x=900, y=20)

    #Defining teh frame where the text welcome username is diplayed together with his balance
    TopFrame = LabelFrame(Game, pady=5, bd=0)
    TopFrame.place(x=50, y=20, width=200, height=100)
    WelcomeLabel = Label(TopFrame, text=f"Welcome {UsernameEntry.get()}", font="Arial 14")
    BalanceLabel = Label(TopFrame, text=f"Balance: ${get_balance(UsernameEntry.get())}", font="Arial 14")
    WelcomeLabel.pack(pady=10)
    BalanceLabel.pack(pady=10)

    #Defining the frame where the user enters his guess and bet
    UserBetFrame = LabelFrame(Game, text="My Bet",font="Arial 21", pady=10, bd=0)
    UserBetFrame.place(x=50, y=150, width=500, height=150)
    UserBetLabel = Label(UserBetFrame, text="Amount I bet:  ", font="Arial 14")
    UserGuessLabel = Label(UserBetFrame, text="My Guess:", font="Arial 14")
    UserBetEntry = Entry(UserBetFrame)
    UserGuessEntry = Entry(UserBetFrame)
    UserGuessLabel.grid(row=0, column=0, pady=20)
    UserGuessEntry.grid(row=0, column=1)
    UserBetLabel.grid(row=1, column=0)
    UserBetEntry.grid(row=1, column=1)

    #defining the frame where the user can choose the bet option
    BetFrame = LabelFrame(Game, text='Bet Type',font="Arial 21", pady=10, bd=0)
    BetFrame.place(x=50, y=330, width=150, height=250)
    #Each button will call the counterpart function for the bet option (type)
    SingleNumButton = Button(BetFrame, text="Single number", font="Arial 14", command=lambda: bet_type(single_num))
    OddEvenButton = Button(BetFrame, text="Odd or Even", font="Arial 14", command=lambda: bet_type(odd_even))
    HighLowButton = Button(BetFrame, text="High or Low", font="Arial 14", command=lambda: bet_type(high_low))
    SingleNumButton.pack(pady=20)
    OddEvenButton.pack(pady=10)
    HighLowButton.pack(pady=10)

    Game.mainloop()

login_page()

Root.mainloop()
################################################################################
################################################################################
################################################################################