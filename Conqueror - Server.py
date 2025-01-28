import socket
import threading
import tkinter as tk
import random
import codecs
import json
import textwrap
import time

#JSON FILES#
data = json.load(codecs.open('Questions.json', 'r', 'utf-8-sig'))
regions = json.load(codecs.open('Regions.json', 'r', 'utf-8-sig'))

#VARIABLES#
Kosice = [475,185,462,210,479,230,477,257,487,255,494,244,536,235,561,242,578,236,601,230,623,244,644,268,664,261,673,249,674,234,690,217,696,199,673,203,648,199,628,219,597,203,569,211,553,190,510,183]
Presov = [462,121,451,144,432,137,430,146,448,155,448,180,462,182,484,162,511,161,545,166,561,177,583,187,597,179,624,197,641,174,666,181,700,176,706,160,691,145,665,139,652,120,634,116,614,104,572,107,553,124,533,125,514,109,488,111]   
Bystrica = [452,195,409,193,385,190,356,200,330,197,329,211,320,219,309,218,273,250,276,267,295,260,307,277,306,298,334,302,334,320,371,315,386,293,401,288,427,308,444,293,464,284,480,273,458,256,465,235,449,222]
Zilina = [262,114,280,139,280,164,296,172,295,186,302,198,314,202,315,186,323,177,354,178,381,171,405,180,429,180,426,162,417,146,397,128,402,116,377,81,363,82,348,103,318,105,314,87,282,89]
Nitra = [214,223,203,242,209,259,197,285,198,299,190,311,198,349,182,370,237,377,288,370,282,349,290,327,318,318,293,312,286,297,289,280,270,291,258,282,257,258,236,260,224,240]
Trencin = [156,200,163,217,182,220,199,224,208,206,223,209,237,219,246,240,270,232,284,222,293,208,284,195,280,182,268,184,255,178,259,167,271,154,249,121,234,134,226,165,213,168,202,184,168,196]
Trnava = [92,231,110,230,122,224,128,211,141,223,141,241,146,260,158,278,159,301,142,312,131,331,147,353,165,366,179,354,180,327,172,308,180,296,193,261,187,244,175,230,157,234,144,211,125,191,104,207]
Bratislava = [94,246,83,266,94,288,104,303,106,322,116,323,119,307,128,298,140,298,139,278,132,265,121,255,118,242]
RegionUnderAttack = None
Client_Region = None
Button_Next = False
Client_Next = False
Player_Answer = ''
Client_Answer = ''
Reply = ''
Start = False
global_client = None
Round = 1

if 1 == 2:  #1 - 1st Phase #2 - 2nd Phase#
    Unowned = [region['Name'] for region in regions['Regions']]
    Claimed_Client = ['Bratislava']
    Claimed_Player = ['Kosice']

else:
    Unowned = ['Nitra']
    Claimed_Client = ['Bratislava', 'Trnava', 'Trencin', 'Bystrica']
    Claimed_Player = ['Kosice','Presov', 'Zilina']

    """Unowned = ['Trnava', 'Zilina', 'Presov']
    Claimed_Client = ['Bratislava']
    Claimed_Player = ['Kosice', 'Bystrica', 'Nitra', 'Trencin']"""

    """Unowned = []
    Claimed_Client = ['Bratislava', 'Trnava', 'Nitra', 'Trencin']
    Claimed_Player = ['Kosice', 'Presov', 'Bystrica', 'Zilina']"""

Capital = ['Bratislava', 'Kosice']

for item in Unowned:
    if item in Capital:
        Unowned.remove(item) 
#SERVER SETUP#
    #SERVER = socket.gethostbyname(socket.gethostname())
SERVER = '0.0.0.0'
PORT = 5050
ADDR = (SERVER, PORT)

#DECODING#
def Decoding(Message):
    global Client_Answer, Client_Next
    if Message[:3] == 'STR':
        global Start
        Start == True
        print(f'[MATCH BEGINNING]: {Client_Answer}')

    if Message[:3] == 'ANS':    #ANSWER#
        Message = Message.removeprefix("ANS = ")
        Client_Answer = Message
        print(f'[CLIENT ANSWER RECIEVED]: {Client_Answer}')
    
    if Message[:3] == 'REG':    #REGION#
        Message = Message.removeprefix("REG = ")
        global Unowned
        if Unowned:
            global Client_Region
            Client_Region = Message
        else:
            global RegionUnderAttack
            RegionUnderAttack = Message
            Client_Next = True 

        print(f'[CLIENT REGION RECIEVED]: {Message}')
    
    if Message[:3] == 'RDY':    #REGION#
        Client_Next = True

#ENCODING#
def Encoding(Message, QID = None, EVA = None, Correct_Answer = None, Choice_Answers=None):
    if Message == 'MAP':    #MAP UPDATE#
        global Unowned, Claimed_Client, Claimed_Player, RegionUnderAttack

        message = "MAP = "
        message += " ".join(Unowned) + " ; "
        message += " ".join(Claimed_Client) + " ; "
        message += " ".join(Claimed_Player) + " ;"
        if RegionUnderAttack:
            message += " " + RegionUnderAttack
        else:
            message += " NONE"
        message += '#'
        if global_client:
            print(f'[MAP INTEL SEND TO CLIENT]: {message}')
            global_client.sendall(message.encode())

    elif Message == 'QID':  #QUESTION ID#
        message = "QID = "
        message += str(QID)
        if not Unowned:     #CHOICE ANSWERS
            message += ';'
            for item in Choice_Answers:
                message += str(item) + ',' 

        message += '#'
        if global_client:
            print(f'[QUESTION ID SEND TO CLIENT]: {message}')
            global_client.sendall(message.encode())
        return message

    elif Message == 'EVA':  #EVALUATION#
        global Player_Answer, Client_Answer
        if EVA == True:
            message = "EVA = " + 'TRUE'
        else:
            message = "EVA = " + 'FALSE'
        message  += '; ' + str(Client_Answer) + '; ' + str(Player_Answer) + '; ' + str(Correct_Answer)

        message += '#'
        if global_client:
            print(f'[EVALUATION SEND TO CLIENT]: {message}')
            global_client.sendall(message.encode())
        return message
    
    elif Message == 'TRN':
        message = 'TRN = TRUE#'
        print(f'[TURN SEND TO CLIENT]: {message}')
        global_client.sendall(message.encode())

    elif Message == 'END':
        message = 'END = ' + str(len(Claimed_Player)) + ',' + str(len(Claimed_Client)) + '#'
        print(f'[TURN SEND TO CLIENT]: {message}')
        global_client.sendall(message.encode())

    
#SERVER FUNCTIONS#
def socket_listener(client, address):
    global global_client
    global_client = client  # Store the client connection for later use
    print(f"Connection established with {address}")
    time.sleep(1)   #Tu by to chcelo shakehand
    client.sendall(str(Encoding('MAP')).encode())

    while True:
        try:
            data = client.recv(1024).decode()
            if not data:
                break
            Decoding(data)

        except ConnectionError:
            print(f"Disconnected from {address}.")
            break

    client.close()
    print(f"Connection closed with {address}")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(ADDR)
        server.listen(5)  # The server can handle 5 clients concurrently
        print(f"Server listening on {ADDR}...")
        
        while True:
            client, address = server.accept()
            threading.Thread(target=socket_listener, args=(client, address), daemon=True).start()

def main():
    #SERVER START#
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    #TKINTER MAINLOOP#

    #UI CLASSES#
    class Region:
        def __init__(self, master, coords, name, mode=None) -> None:
            self.master = master
            self.coords = coords
            self.name = name
            self.mode = mode

            # Determine color based on region ownership
            #color = None  # Default is None, indicating no rendering

            if name in Claimed_Player:
                color = 'Royal Blue' if name == RegionUnderAttack else 'Deep Sky Blue'
            elif name in Claimed_Client:
                color = 'Red' if name == RegionUnderAttack else 'Tomato'
            else:
                color = ''

            # Render only if color is set
            #if color:
            self.polygon = master.create_polygon(coords, fill=color, outline="black")
            if mode is not None:
                master.tag_bind(self.polygon, '<Button-1>', self.on_click)


            if mode is not None:
                master.tag_bind(self.polygon, '<Button-1>', self.on_click)

        def on_click(self, event):
            global Button_Next, RegionUnderAttack
            Claim(Claimed_Player, self.name)

            Button_Next = True
            Waiting_For_Enemy()
            Map()
            Encoding('MAP')

    class Button:
        def __init__(self, master, name, text, action, row, column) -> None:
            self.master = master
            self.name = name
            self.text = text
            self.action = action
            self.row = row
            self.column = column


            name = tk.Button(master=master, text=textwrap.fill(text,40), command=lambda: self.command(action), font="Arial 15", bg="gray22",  activebackground="gray15", fg="Ivory2", activeforeground="Snow", borderwidth=0, highlightthickness=0, width=50)
            name.grid(padx = 10, pady = 10, row=row, column=column, sticky="NSEW")

            
        def command(self, x):
            global Reply, Player_Answer
            if x in ('A', 'B', 'C', 'D'):
                Player_Answer = x
                Waiting_For_Enemy()
                return

            else:
                match x:
                    case "Clear":
                        Reply = ""
                    case "Enter":
                        Player_Answer = Reply
                        Reply = ""
                        Waiting_For_Enemy()
                        pass
                    case "Next":
                        #print("Next")
                        global Button_Next
                        Button_Next = True
                        Waiting_For_Enemy()
                        return
                    case _:
                        Reply = Reply + x
                label2 = tk.Label(Display, text=Reply, font='Arial 15', bg="Deep Sky Blue3")
                label2.grid(row=0, column=0, sticky="NSEW")

    #UI SETUP#
    
    root = tk.Tk()
    root.resizable(width=False, height=False)
    root.title('Conqueror Remastered - SERVER')
    root.geometry('800x900')

    #FUNCTIONS#
    def Quess_Setup():
        if global_client and Unowned:
            Guess_ID = random.randint(1, len(data['Question_Guess'])-3)
            Guess(Guess_ID)
            Encoding('QID', QID=Guess_ID)
        else:
            root.after(5, Quess_Setup)
    
    def Choice_Setup():
        if global_client and not Unowned and RegionUnderAttack:
            Choice_ID = random.randint(1, len(data['Question_Choice'])-3)
            Choice(Choice_ID)
            Map()
        else:
            root.after(500, Choice_Setup)

    def Declaration():
        def Check():
            global RegionUnderAttack, Round

            if RegionUnderAttack:
                Choice_Setup()
                Map()
                Round +=1

            else:
                root.after(500, Check)
        
        global Round
        if Round <= 2:
            if Round %2 == 0:
                print(Round)
                Waiting_For_Enemy(Message='Attack')
                Map(DrawMode=1)
            else:
                Encoding('TRN')
            Check()
        else:
            Encoding('END')
            END_Screen()
                
    def Neighbouring_Func(Player, Action=None):
        global Unowned
        if Action is None:
            Neighbouring = []
            for region in Player:
                region = next((item for item in regions['Regions'] if item['Name'] == region), None)
                Neighbour = region['Neighbour']
                for item in Neighbour:
                    if item not in Neighbouring and item not in Player:
                        Neighbouring.append(item)

        else:
            Neighbouring = []
            for region in Player:
                region = next((item for item in regions['Regions'] if item['Name'] == region), None)
                Neighbour = region['Neighbour']
                for item in Neighbour:
                    if item not in Neighbouring and item not in Claimed_Player and item not in Claimed_Client:
                        Neighbouring.append(item)

        return Neighbouring
        
    def Gameloop():

        global Button_Next, Round, Client_Next
        if Button_Next is True and Client_Next is True:
            print(f"BUTTON{Button_Next}, CLIENT{Client_Next}")
            if Unowned:
                Quess_Setup()

            elif not Unowned:
                Declaration()
                Button_Next = False
                Client_Next = False
                #Choice_Setup()
                #Round += 1
            
            root.after(1000, Gameloop)

        else:
            root.after(1000, Gameloop)

    def Claim(Player, Region):      #Claim/Attacking Regions Input: Claimed_Player or Claimed_AI
        global RegionUnderAttack, Button_Next
        if Player == Claimed_Client:
            Unowned.remove(Region)
            Player.append(Region)
            return
        if Unowned:
            Neighbours = Neighbouring_Func(Claimed_Player, Action='Clailm')
            print(Neighbours)
            if len(Neighbours) > 1:
                if Region in Unowned and Region in Neighbours:
                    Unowned.remove(Region)
                    Claimed_Player.append(Region)
                
            elif len(Neighbours) == 1:
                Unowned.remove(Neighbours[0])
                Claimed_Player.append(Neighbours[0])

            else:
                RandomRegion = random.choice(Unowned)
                Unowned.remove(RandomRegion)
                Claimed_Player.append(RandomRegion)
        
        else:
            Neighbours = Neighbouring_Func(Claimed_Player)
            if len(Neighbours) > 1:
                if Region not in Claimed_Player and Region in Neighbours:
                    RegionUnderAttack = Region
                else:
                    RegionUnderAttack = random.choice(Neighbours)

            if len(Neighbours) == 1:
                RegionUnderAttack = Neighbours[0]
    
        Button_Next = True
        Map()
        Encoding('MAP')

    #UI FUNCTIONS#
    def END_Screen():
        Screen = tk.Frame(master=root, width='800', height='450', bg='grey20')
        Screen.grid_propagate(False)
        Screen.grid_columnconfigure(0, weight=1)
        Screen.grid_rowconfigure(0, weight=1)
        Screen.grid_rowconfigure(1, weight=1)

        END_Text = tk.Frame(master=Screen, bg='grey20')
        END_Text.grid_rowconfigure(0, weight=0)
        END_Text.grid_rowconfigure(1, weight=0)
        END_Text.grid_columnconfigure(0, weight=1)
        END_Text.grid_propagate(False)

        END_Text1 = tk.Label(master=END_Text, text="Koniec Hry", font="Arial 35", bg="ivory2", fg="Black")
        END_Text1.grid(row=0, column=0, sticky='NSEW')

        END_Text2 = tk.Label(master=END_Text, text="Počet krajov", font="Arial 20", bg="ivory4", fg="Black")
        END_Text2.grid(row=1, column=0, sticky='NSEW')
        END_Text.grid(row=0, column=0, sticky='NSEW')

        Scoreboard = tk.Frame(master=Screen, bg='grey20')
        Scoreboard.grid_rowconfigure(0, weight=1)
        Scoreboard.grid_rowconfigure(1, weight=1)
        Scoreboard.grid_columnconfigure(0, weight=1)
        Scoreboard.grid_columnconfigure(1, weight=1)

        Client_Frame = tk.Frame(master=Scoreboard)
        Client_Frame.rowconfigure(0, weight=1)
        Client_Frame.rowconfigure(1, weight=1)
        Client_Frame.grid_columnconfigure(0, weight=1)

        Client_Label = tk.Label(master=Client_Frame, text='Červený', bg='tomato', fg='black', font='Arial 25')
        Client_Label.grid(row=0, column=0, sticky='NSEW')

        Client_Value = tk.Label(master=Client_Frame, text=len(Claimed_Client), bg='tomato3', fg='black', font='Arial 25')
        Client_Value.grid(row=1, column=0, sticky='NSEW')

        Client_Frame.grid(row=0, column=0, sticky='NSEW')

        #Player
        Player_Frame = tk.Frame(master=Scoreboard)
        Player_Frame.rowconfigure(0, weight=1)
        Player_Frame.rowconfigure(1, weight=1)
        Player_Frame.grid_columnconfigure(0, weight=1)

        Player_Label = tk.Label(master=Player_Frame, text='Modrý', bg='deep sky blue', fg='black', font='Arial 25')
        Player_Label.grid(row=0, column=0, sticky='NSEW')

        Player_Value = tk.Label(master=Player_Frame, text=len(Claimed_Player), bg='deep sky blue3', fg='black', font='Arial 25')
        Player_Value.grid(row=1, column=0, sticky='NSEW')

        Player_Frame.grid(row=0, column=1, sticky='NSEW')

        Scoreboard.grid(row=1, column=0, sticky='NSEW')
        Screen.grid(row=1, column=0, sticky='NSEW')

    def Waiting_For_Enemy(Message = None):
        Waiting = tk.Frame(master=root, height='450', width='800', bg='grey15')
        Waiting.grid_rowconfigure(0, weight=1)
        Waiting.grid_rowconfigure(1, weight=0)
        Waiting.grid_rowconfigure(2, weight=0)
        Waiting.grid_rowconfigure(3, weight=1)
        Waiting.grid_columnconfigure(0, weight=1)

        Divider1 = tk.Label(master=Waiting, text='', bg='grey15')
        Divider1.grid(row=0, column=0, sticky='NSEW')

        if not Message:
            Label1_Text = 'Počkajte prosím'
            Label2_Text = 'Oponent nie je pripravený'
            colour1 = 'Deep Sky Blue'
            colour2 = 'Deep Sky Blue3'
        
        else:
            Label1_Text = 'Vyberte si kraj'
            Label2_Text = 'Na ktorý budete útočiť'
            colour1 = 'ivory2'
            colour2 = 'ivory4'

        Label1 = tk.Label(master=Waiting, text=Label1_Text, bg=colour1, fg='Black', font='Arial 20')
        Label1.grid(row=1, column=0, sticky='NSEW')

        Label2 = tk.Label(master=Waiting, text=Label2_Text, bg=colour2, fg='Black', font='Arial 20')
        Label2.grid(row=2, column=0, sticky='NSEW')
        
        Divider2 = tk.Label(master=Waiting, text='', bg='grey15')
        Divider2.grid(row=3, column=0, sticky='NSEW')

        Waiting.grid(row=1, sticky='NSEW')

    def Map(DrawMode = None):
        Map = tk.Frame(master=root, height='450', width='800', bg='grey15')

        canvas = tk.Canvas(master=Map, width='800', height='450', bg="grey15", highlightthickness=0)

        global Slovakia
        Slovakia = tk.PhotoImage(file="slovakia2.png")
        canvas.create_image(400,225,image=Slovakia)

        def RegionDraw(mode = None):
            Region(canvas, Kosice, "Kosice", mode)
            Region(canvas, Presov, "Presov", mode)
            Region(canvas, Bystrica, "Bystrica", mode)
            Region(canvas, Zilina, "Zilina", mode)
            Region(canvas, Nitra, "Nitra", mode)
            Region(canvas, Trencin, "Trencin", mode)
            Region(canvas, Trnava, "Trnava", mode)
            Region(canvas, Bratislava, "Bratislava", mode)

        RegionDraw(DrawMode)


        canvas.pack()
        Map.grid(row=0, sticky='NSEW')

    def Guess(ID):
        global Button_Next, Client_Next
        Button_Next = False
        Client_Next = False
        Guess = tk.Frame(master=root, height='450', width='800', bg='gray20')
        Guess.grid_propagate(False)
        Guess.grid_columnconfigure(0, weight=1)
        Guess.grid_rowconfigure(0, weight=1)
        Guess.grid_rowconfigure(1, weight=1)
        Guess.grid_rowconfigure(2, weight=4)
        

        Question = tk.Frame(master=Guess)
        Question.grid_columnconfigure(0, weight=1)
        Question.grid_rowconfigure(0, weight=1)


        Question1 = tk.Label(Question, text=textwrap.fill([item['Question'] for item in data['Question_Guess']][ID],75), font='Arial 15', width=800, fg="Black", bg="Deep Sky Blue")
        Question1.grid(row=0, column=0, sticky="NSEW")

        Question.grid(row=0, sticky="NSEW")

        global Display, Reply

        Display = tk.Frame(master=Guess, bg="deep sky blue")
        Display.grid_columnconfigure(0, weight=1)
        Display.grid_rowconfigure(0, weight=1)

        Preview = tk.Label(Display, text=Reply, font='Arial 15', bg="Deep Sky Blue3", fg="Deep Sky Blue3")
        Preview.grid(row=0, column=0, sticky="NSEW")

        Display.grid(row=1, column=0, sticky="NSEW")

        Buttons = tk.Frame(master=Guess, bg="grey15")
        for col in range(3):
            Buttons.grid_columnconfigure(col, weight=1)
        for row in range(4):
            Buttons.grid_rowconfigure(row, weight=1)

        Button(Buttons, 'ButtonEnter', 'POTVRDIŤ', 'Enter', row=3, column=2)
        Button(Buttons, 'ButtonRemove', 'ZMAZAŤ', 'Clear', row=3, column=0)
        Button(Buttons, 'Button0', '0', '0', row=3, column=1)
        Button(Buttons, 'Button1', '1', '1', row=2, column=0)
        Button(Buttons, 'Button2', '2', '2', row=2, column=1)
        Button(Buttons, 'Button3', '3', '3', row=2, column=2)
        Button(Buttons, 'Button4', '4', '4', row=1, column=0)
        Button(Buttons, 'Button5', '5', '5', row=1, column=1)
        Button(Buttons, 'Button6', '6', '6', row=1, column=2)
        Button(Buttons, 'Button7', '7', '7', row=0, column=0)
        Button(Buttons, 'Button8', '8', '8', row=0, column=1)
        Button(Buttons, 'Button9', '9', '9', row=0, column=2)
        Buttons.grid(column=0, row=2, sticky="NSEW")

        Guess.grid(row=1, sticky="NSEW")

        AnswerCheck(ID=ID)

    def Answers(Correct_Answer, Player_Answer, Client_Answer):
        Answers = tk.Frame(master=root, height='450', width='800', bg='grey25')
        Answers.grid_propagate(False)
        Answers.grid_columnconfigure(0, weight=1)
        Answers.grid_rowconfigure(0, weight=1)
        Answers.grid_rowconfigure(1, weight=1)
        Answers.grid_rowconfigure(2, weight=1)
        Answers.grid_rowconfigure(3, weight=1)
        Answers.grid_rowconfigure(4, weight=2)

        Devider = tk.Label(master=Answers, bg='grey20', text='Odpovede', font='Arial 15', fg='Ivory2')
        Devider.grid(row=0, column=0, sticky='NSEW')
        #CORRECT#
        Correct_Answer_Frame = tk.Frame(master=Answers, bg='grey25')
        Correct_Answer_Frame.grid_rowconfigure(0, weight=1)
        Correct_Answer_Frame.grid_rowconfigure(1, weight=2)
        Correct_Answer_Frame.columnconfigure(0, weight=1)
        Correct_Answer_Frame.propagate(False)
        
        CorrectLabel = tk.Label(master=Correct_Answer_Frame, bg='chartreuse', text='Správna', font='arial 15')
        CorrectLabel.grid(row=0, column=0, sticky='NSWE')

        CorrectValue = tk.Label(master=Correct_Answer_Frame, bg='chartreuse3', text=Correct_Answer, font='arial 15')
        CorrectValue.grid(row=1, column=0, sticky='NSWE')

        Correct_Answer_Frame.grid(row=1, column=0, sticky='NSWE')
        #PLAYER#
        Player_Answer_Frame = tk.Frame(master=Answers, bg='grey25')
        Player_Answer_Frame.grid_rowconfigure(0, weight=1)
        Player_Answer_Frame.grid_rowconfigure(1, weight=2)
        Player_Answer_Frame.columnconfigure(0, weight=1)
        Player_Answer_Frame.propagate(False)
        
        PlayerLabel = tk.Label(master=Player_Answer_Frame, bg='Deep Sky Blue', text='Modrý', font='arial 15')
        PlayerLabel.grid(row=0, column=0, sticky='NSWE')

        PlayerValue = tk.Label(master=Player_Answer_Frame, bg='Deep Sky Blue3', text=Player_Answer, font='arial 15')
        PlayerValue.grid(row=1, column=0, sticky='NSWE')

        Player_Answer_Frame.grid(row=2, column=0, sticky='NSWE')
        #CLIENT#
        Client_Answer_Frame = tk.Frame(master=Answers, bg='grey25')
        Client_Answer_Frame.grid_rowconfigure(0, weight=1)
        Client_Answer_Frame.grid_rowconfigure(1, weight=2)
        Client_Answer_Frame.columnconfigure(0, weight=1)
        Client_Answer_Frame.propagate(False)
        
        ClientLabel = tk.Label(master=Client_Answer_Frame, bg='tomato', text='Červený', font='arial 15')
        ClientLabel.grid(row=0, column=0, sticky='NSWE')

        ClientValue = tk.Label(master=Client_Answer_Frame, bg='tomato3', text=Client_Answer, font='arial 15')
        ClientValue.grid(row=1, column=0, sticky='NSWE')

        Client_Answer_Frame.grid(row=3, column=0, sticky='NSWE')
        #BUTTONS#
        ButtonsAnswer = tk.Frame(master=Answers, bg="grey20")
        ButtonsAnswer.grid_columnconfigure(0, weight=1)
        ButtonsAnswer.grid_rowconfigure(0, weight=1)
        if Unowned:
            if abs(Correct_Answer - Player_Answer) >= abs(Correct_Answer - Client_Answer):
                Button(ButtonsAnswer, 'NextQ', 'Pokračovať', 'Next', row=0, column=0)

            else:
                Continue = tk.Label(master=ButtonsAnswer, text='Vyberte si kraj', bg="grey20", fg="Ivory2", font='Arial 15')
                Continue.grid(row=0, column=0, sticky="NSEW")

        else: 
            Button(ButtonsAnswer, 'NextQ', 'Pokračovať', 'Next', row=0, column=0)

        ButtonsAnswer.grid(row=4, column=0, sticky="NSEW")

        Answers.grid(row=1, column=0, sticky="NSEW")
                
    def AnswerCheck(ID):
        def WaitForReply():
            global Client_Answer, Player_Answer
            if Client_Answer and Player_Answer:
                Check()
            else:
                root.after(5, WaitForReply)

        def WaitForRegion():
            global Client_Region, Client_Next
            if Client_Region:
                Claim(Claimed_Client, Client_Region)
                Map()
                Encoding('MAP')
                Client_Next = True
                Client_Region = None
            else:
                root.after(1, WaitForRegion)

        def Check():
            global Unowned, Player_Answer, Client_Answer
            if Unowned:
                Correct_Answer = ([item['Answer'] for item in data['Question_Guess']][ID])
                Player_Answer = int(Player_Answer)
                Client_Answer = int(Client_Answer)
                Answers(Correct_Answer=Correct_Answer, Player_Answer=Player_Answer, Client_Answer=Client_Answer)
                if abs(Player_Answer - Correct_Answer) == abs(Client_Answer - Correct_Answer):
                    print('Remiza')
                    Encoding('EVA', EVA=False, Correct_Answer=Correct_Answer)
                elif abs(Player_Answer - Correct_Answer) < abs(Client_Answer - Correct_Answer):
                    Map(DrawMode=1)
                    Encoding('EVA', EVA=False, Correct_Answer=Correct_Answer)
                else:
                    Encoding('EVA', EVA=True, Correct_Answer=Correct_Answer)
                    WaitForRegion()
            
            else:
                global RegionUnderAttack, Correct_Choice
                print(f'Player Answer{Player_Answer}, Client Answer{Client_Answer}, RegionUA{RegionUnderAttack}, Correct{Correct_Choice}')
                Answers(Correct_Answer=Correct_Choice, Player_Answer=Player_Answer, Client_Answer=Client_Answer)
                
                if Player_Answer == Correct_Choice and Client_Answer != Correct_Choice:
                    if RegionUnderAttack in Claimed_Client:
                        Claimed_Client.remove(RegionUnderAttack)
                        Claimed_Player.append(RegionUnderAttack)

                
                elif Client_Answer == Correct_Choice and Player_Answer != Correct_Choice:
                    if RegionUnderAttack in Claimed_Player:
                        Claimed_Player.remove(RegionUnderAttack)
                        Claimed_Client.append(RegionUnderAttack)

                Encoding('EVA', EVA=False, Correct_Answer=Correct_Choice)
                Correct_Choice = None
                Encoding('MAP')
                RegionUnderAttack = None
                Map()
            Player_Answer = ''
            Client_Answer = ''
            
        WaitForReply()

    def Choice(QID):
        global Reply_Choice, Button_Next, Client_Next
        Client_Next = False
        Button_Next = False
        Wrong_Answers = []
        Choices = ["A", "B", "C", "D"]
        Final = []

    # id = random <0, max); Wrong_Answers = tu sa načitaju nespravne odpovede z json; Final = tu kombinujem moznosti s odpovedami

        for item in [value['IncorrectAnswers'] for value in data['Question_Choice']][QID]:
            Wrong_Answers.append(item)

        global Correct_Choice
        Correct_Choice = random.choice(Choices)
        Final.append(Correct_Choice + ") " + ([card['Answer'] for card in data['Question_Choice']][QID]))
        Choices.remove(Correct_Choice)

        for item in Choices:
            i = 0
            Answer = Wrong_Answers[i]
            Final.append(item + ") " + Answer)
            Wrong_Answers.remove(Answer)
            i += 1
        
        Final.sort()
        Encoding('QID', QID=QID, Choice_Answers=Final)
        #Posledná možnosť == správna, priradená ku "Answer" z json

    
        Choice = tk.Frame(master=root, height='450', width='800', bg='grey20')
        Choice.grid_propagate(False)
        Choice.grid_columnconfigure(0, weight=1)
        Choice.grid_rowconfigure(0, weight=1)
        Choice.grid_rowconfigure(1, weight=4)

        Question = tk.Frame(master=Choice, bg= "grey25")
        Question.grid_columnconfigure(0, weight=1)
        Question.grid_rowconfigure(0, weight=1)

        Question1 = tk.Label(Question, text=textwrap.fill([item['Question'] for item in data['Question_Choice']][QID], 75), font="Arial 15", bg="Deep Sky Blue", fg="Black")
        Question1.grid(row=0, column=0, sticky="NSEW")
        Question.grid(row=0, sticky="NSEW")


        #Choice Buttons
        Buttons = tk.Frame(master=Choice, bg="grey15")
        Buttons.grid_columnconfigure(0, weight=1)
        Buttons.grid_columnconfigure(1, weight=1)
        Buttons.grid_rowconfigure(0, weight=1)
        Buttons.grid_rowconfigure(1, weight=1)


        Button(Buttons, 'ButtonA', Final[0], 'A', row=0, column=0) #Dorobiť wrap
        Button(Buttons, 'ButtonB', Final[1], 'B', row=0, column=1)
        Button(Buttons, 'ButtonC', Final[2], 'C', row=1, column=0)
        Button(Buttons, 'ButtonD', Final[3], 'D', row=1, column=1)

        Buttons.grid(column=0, row=1, sticky="NSEW")
        Choice.grid(column=0, row=1, sticky="NSEW")

        Button(Buttons, 'ButtonA', Final[0], 'A', row=0, column=0) #Dorobiť wrap
        Button(Buttons, 'ButtonB', Final[1], 'B', row=0, column=1)
        Button(Buttons, 'ButtonC', Final[2], 'C', row=1, column=0)
        Button(Buttons, 'ButtonD', Final[3], 'D', row=1, column=1)

        Buttons.grid(column=0, row=1, sticky="NSEW")
        Choice.grid(column=0, row=1, sticky="NSEW")

        AnswerCheck(ID=QID)

    #MAIN GAME CODE#
    Map()
    Gameloop()
    Quess_Setup()
    root.mainloop()
main()