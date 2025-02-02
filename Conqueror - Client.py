import socket
import threading
import tkinter as tk
import random
import codecs
import json
import textwrap

#JSON FILES#
data = json.load(codecs.open('Questions.json', 'r', 'utf-8-sig'))
regions = json.load(codecs.open('Regions.json', 'r', 'utf-8-sig'))

#VARIABLES
Kosice = [475,185,462,210,479,230,477,257,487,255,494,244,536,235,561,242,578,236,601,230,623,244,644,268,664,261,673,249,674,234,690,217,696,199,673,203,648,199,628,219,597,203,569,211,553,190,510,183]
Presov = [462,121,451,144,432,137,430,146,448,155,448,180,462,182,484,162,511,161,545,166,561,177,583,187,597,179,624,197,641,174,666,181,700,176,706,160,691,145,665,139,652,120,634,116,614,104,572,107,553,124,533,125,514,109,488,111]   
Bystrica = [452,195,409,193,385,190,356,200,330,197,329,211,320,219,309,218,273,250,276,267,295,260,307,277,306,298,334,302,334,320,371,315,386,293,401,288,427,308,444,293,464,284,480,273,458,256,465,235,449,222]
Zilina = [262,114,280,139,280,164,296,172,295,186,302,198,314,202,315,186,323,177,354,178,381,171,405,180,429,180,426,162,417,146,397,128,402,116,377,81,363,82,348,103,318,105,314,87,282,89]
Nitra = [214,223,203,242,209,259,197,285,198,299,190,311,198,349,182,370,237,377,288,370,282,349,290,327,318,318,293,312,286,297,289,280,270,291,258,282,257,258,236,260,224,240]
Trencin = [156,200,163,217,182,220,199,224,208,206,223,209,237,219,246,240,270,232,284,222,293,208,284,195,280,182,268,184,255,178,259,167,271,154,249,121,234,134,226,165,213,168,202,184,168,196]
Trnava = [92,231,110,230,122,224,128,211,141,223,141,241,146,260,158,278,159,301,142,312,131,331,147,353,165,366,179,354,180,327,172,308,180,296,193,261,187,244,175,230,157,234,144,211,125,191,104,207]
Bratislava = [94,246,83,266,94,288,104,303,106,322,116,323,119,307,128,298,140,298,139,278,132,265,121,255,118,242]
RegionUnderAttack = ''
Claimed_Player = []
Claimed_Client = []
Unowned = ['Start']
Reply = ''
global_client = None

#SERVER SETUP#
SERVER = '127.0.0.1'
PORT = 5050
ADDR = (SERVER, PORT)

#UI SETUP#
root = tk.Tk()
root.resizable(width=False, height=False)
root.title('Conqueror Remastered - CLIENT')
root.geometry('800x900')

#UI CLASSES#
class Region:
    def __init__(self, master, coords, name, mode = None) -> None:
        self.master = master
        self.coords = coords
        self.name = name
        self.mode = mode

        match name:
            case name if name in Unowned:
                color = ''
            
            case name if name in Claimed_Player:
                if name == RegionUnderAttack:
                    color = 'Royal Blue'

                else:
                    color = 'Deep Sky Blue'

            case name if name in Claimed_Client:
                if name == RegionUnderAttack:
                    color = 'Red'

                else:
                    color = 'Tomato'
            case __:
                color = 'White'  

        self.polygon = master.create_polygon(coords, fill=color, outline="black")

        if mode is not None:
            master.tag_bind(self.polygon, '<Button-1>', self.on_click)

    def on_click(self, event):
        Claim(Claimed_Client, self.name)
        Waiting_For_Enemy()
        Map()

class Button:
    def __init__(self, master, name, text, action, row, column) -> None:
        self.master = master
        self.name = name
        self.text = text
        self.action = action
        self.row = row
        self.column = column


        name = tk.Button(master=master, text=textwrap.fill(text,40), command=lambda: self.command(action), font='Arial 15', bg="gray22",  activebackground="gray15", fg="Ivory2", activeforeground="Snow", borderwidth=0, highlightthickness=0, width=50)
        name.grid(padx = 10, pady = 10, row=row, column=column, sticky="NSEW")

        
    def command(self, x):
        global Reply
        if x in ('A', 'B', 'C', 'D'):
            Encoding('ANS', Answer=x)
            Waiting_For_Enemy()
        else:
            match x:
                case "Clear":
                    Reply = ""
                case "Enter":
                    Encoding('ANS', Answer=Reply)
                    Waiting_For_Enemy()
                    Reply = ""
                    pass
                case "Next":
                    #print("Next")
                    Encoding('RDY')
                    Waiting_For_Enemy()
                    global RegionUnderAttack
                    RegionUnderAttack = None
                    Map()
                    return
                case _:
                    Reply = Reply + x
            label2 = tk.Label(Display, text=Reply, font='Arial 15', bg="tomato3")
            label2.grid(row=0, column=0, sticky="NSEW")
#FUNCTIONS#
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
                if item not in Neighbouring and item not in Claimed_Client and item not in Claimed_Player:
                    Neighbouring.append(item)


    return Neighbouring


def Claim(Player, Region=None):      #Claim/Attacking Regions Input: Claimed_Player or Claimed_AI
    global Unowned, RegionUnderAttack

    if Unowned: #Claim
        Neighbours = Neighbouring_Func(Player=Player, Action='Claim')
        if len(Neighbours) > 1:
            CurrentRegion = Region
            if Region in Unowned and CurrentRegion in Neighbours:
                Encoding('REG', Region=CurrentRegion)
            else:
                Claim(Claimed_Client, 'No such region')
        elif len(Neighbours) == 1:
            Encoding('REG', Region=Neighbours[0])
        else:
            Encoding('REG', Region=random.choice(Unowned))

    else:   #Attack
        Neighbours = Neighbouring_Func(Player=Player)
        if len(Neighbours) > 1:
            if Region not in Claimed_Client and Region in Neighbours:
                Encoding('REG', Region=Region)
            else:
                RandomRegion = random.choice(Neighbours)
                Claim(Claimed_Client, RandomRegion)
                Region = RandomRegion
        else:
            Encoding('REG', Region=Neighbours[0])
        RegionUnderAttack = Region

def Declaration():
    def Check():
        global RegionUnderAttack
        if RegionUnderAttack != '':
            pass

        else:
            root.after(500, Check)

    Map(DrawMode=1)
    Waiting_For_Enemy(Message='Attack')
    Check()

#UI FUNCTIONS#
def END_Screen(Claimed_Client, Claimed_Player):
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

    Client_Value = tk.Label(master=Client_Frame, text=Claimed_Client, bg='tomato3', fg='black', font='Arial 25')
    Client_Value.grid(row=1, column=0, sticky='NSEW')

    Client_Frame.grid(row=0, column=0, sticky='NSEW')

    #Player
    Player_Frame = tk.Frame(master=Scoreboard)
    Player_Frame.rowconfigure(0, weight=1)
    Player_Frame.rowconfigure(1, weight=1)
    Player_Frame.grid_columnconfigure(0, weight=1)

    Player_Label = tk.Label(master=Player_Frame, text='Modrý', bg='deep sky blue', fg='black', font='Arial 25')
    Player_Label.grid(row=0, column=0, sticky='NSEW')

    Player_Value = tk.Label(master=Player_Frame, text=Claimed_Player, bg='deep sky blue3', fg='black', font='Arial 25')
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
        colour1 = 'Tomato'
        colour2 = 'Tomato3'
    
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
    ID = int(ID)
    Guess = tk.Frame(master=root, height='450', width='800', bg='gray20')
    Guess.grid_propagate(False)
    Guess.grid_columnconfigure(0, weight=1)
    Guess.grid_rowconfigure(0, weight=1)
    Guess.grid_rowconfigure(1, weight=1)
    Guess.grid_rowconfigure(2, weight=4)
    

    Question = tk.Frame(master=Guess)
    Question.grid_columnconfigure(0, weight=1)
    Question.grid_rowconfigure(0, weight=1)


    Question1 = tk.Label(Question, text=textwrap.fill([item['Question'] for item in data['Question_Guess']][ID],75), font='Arial 15', width=800, fg="Black", bg="Tomato")
    Question1.grid(row=0, column=0, sticky="NSEW")

    Question.grid(row=0, sticky="NSEW")

    global Display, Reply

    Display = tk.Frame(master=Guess, bg="deep sky blue")
    Display.grid_columnconfigure(0, weight=1)
    Display.grid_rowconfigure(0, weight=1)

    Preview = tk.Label(Display, text=Reply, font='Arial 15', bg="tomato3", fg="tomato3")
    Preview.grid(row=0, column=0, sticky="NSEW")

    Display.grid(row=1, column=0, sticky="NSEW")

    Buttons = tk.Frame(master=Guess, bg="grey15")
    Buttons.grid_columnconfigure(0, weight=1)
    Buttons.grid_columnconfigure(1, weight=1)
    Buttons.grid_columnconfigure(2, weight=1)
    Buttons.grid_rowconfigure(0, weight=1)
    Buttons.grid_rowconfigure(1, weight=1)
    Buttons.grid_rowconfigure(2, weight=1)
    Buttons.grid_rowconfigure(3, weight=1)

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
        if abs(int(Correct_Answer) - int(Player_Answer)) <= abs(int(Correct_Answer) - int(Client_Answer)):
            Button(ButtonsAnswer, 'NextQ', 'Pokračovať', 'Next', row=0, column=0)

        else:
            Continue = tk.Label(master=ButtonsAnswer, text='Vyberte si kraj', bg="grey20", fg="Ivory2", font='Arial 15')
            Continue.grid(row=0, column=0, sticky="NSEW")

    else: 
        Button(ButtonsAnswer, 'NextQ', 'Pokračovať', 'Next', row=0, column=0)

    ButtonsAnswer.grid(row=4, column=0, sticky="NSEW")

    Answers.grid(row=1, column=0, sticky="NSEW")

def Choice(QID, Choice_Answers):
        Final = Choice_Answers

        Choice = tk.Frame(master=root, height='450', width='800', bg='grey20')
        Choice.grid_propagate(False)
        Choice.grid_columnconfigure(0, weight=1)
        Choice.grid_rowconfigure(0, weight=1)
        Choice.grid_rowconfigure(1, weight=4)

        Question = tk.Frame(master=Choice, bg= "grey25")
        Question.grid_columnconfigure(0, weight=1)
        Question.grid_rowconfigure(0, weight=1)

        Question1 = tk.Label(Question, text=textwrap.fill([item['Question'] for item in data['Question_Choice']][QID], 75), font='Arial 15', bg="Tomato", fg="Black")
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

#DECODING#
def Decoding(Message):
    global Unowned
    if Message[:3] == 'MAP':    #MAP UPDATE#
        global Unowned, Claimed_Client, Claimed_Player, RegionUnderAttack
        Unowned = []
        Claimed_Client = []
        Claimed_Player = []
        RegionUnderAttack = None
        List = []

        Message = Message.removeprefix("MAP = ")
        List = Message.split(';')

        for item in List[0].split():
            Unowned.append(item)
        for item in List[1].split():
            Claimed_Client.append(item)
        for item in List[2].split():
            Claimed_Player.append(item)

        print(f'[MAP INTEL RECIEVED]')
        if Unowned:
            Map()
        else:
            print(List[3])
            RegionUnderAttack = List[3].strip()
            Map()
            #Declaration()

    elif Message[:3] == 'QID':  #QUESTION ID#
        Message = Message.removeprefix("QID = ")
        if Unowned:
            Guess(int(Message))
        else:
            Choice_Answers = []
            List = Message.split(';')
            QID = int(List[0])
            for item in List[1].split(','):
                Choice_Answers.append(item)
            Choice(QID=QID, Choice_Answers=Choice_Answers)
        print(f'[QUESTION ID RECIEVED]')
    
    elif Message[:3] == 'EVA':  #EVALUATION#
        Message = Message.removeprefix("EVA = ")
        List = Message.split(';')
        Client_Answer = List[1]
        Player_Answer = List[2]
        Correct_Answer = List[3]
        Answers(Correct_Answer=Correct_Answer, Player_Answer=Player_Answer, Client_Answer=Client_Answer)
        if List[0] == 'TRUE':
            Map(DrawMode=1)

        print(f'[EVALUATION RECIEVED]')
        #dorobiť
    
    elif Message[:3] == 'TRN':
        Message = Message.removeprefix("TRN = ")
        if Message == 'TRUE':
            print('[TURN RECIEVED]')
            Declaration()
    
    elif Message[:3] == 'END':
        Message = Message.removeprefix('END = ')
        List = Message.split(',')
        END_Screen(Claimed_Player=List[0].strip(), Claimed_Client=List[1].strip())
        Map()
        
            

#ENCODING#
def Encoding(Message, Answer = None, Region = None):
    if Message == 'STR':
        message = 'STR = TRUE'
        print(f'[START SEND TO SERVER]')
        global_client.sendall(message.encode())

    if Message == 'ANS':    #CLIENT ANSWER#
        message = 'ANS = ' + str(Answer)

        print(f'[ANSWER SEND TO SERVER]')
        global_client.sendall(message.encode())

    elif Message == 'REG':   #CLIENT REGION#
        message = 'REG = ' + Region

        print(f'[REGION SEND TO SERVER] {message}')
        global_client.sendall(message.encode())
    
    elif Message == 'RDY':   #READY FOR NEXT QUESTION#
        message = 'RDY = ' + 'TRUE'
        print(f'[STATUS READY SEND TO SERVER]')
        global_client.sendall(message.encode())


#SERVER FUNCTIONS#
def socket_listener(client):
    while True:
        try:
            data = client.recv(1024).decode()
            if not data:
                break
            data = data.split('#')
            print(data[0])
            Decoding(data[0])
            del data

        except ConnectionError:
            print("Disconnected from server.")
            break


def main():
    # Start the socket connection in a separate thread
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        global global_client
        global_client = client
        client.connect(ADDR)
        threading.Thread(target=socket_listener, args=(client,), daemon=True).start()
        # Start the Tkinter main loop
        root.mainloop()

main()