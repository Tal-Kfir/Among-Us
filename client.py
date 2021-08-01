from pynput.keyboard import Listener, Key
import config
import clientnetwork
import clientgraphics
import time
import threading
from moviepy.editor import *
from random import randint
import pygame


# Initializing Vars
Pos = config.POS
Alive = True
WhereTo = [config.LEFT, config.NOT_MOVING]
Legal = True
Timer = time.time()
Moving = False
SelfGraph = ""
Running = True
Players = 1
SelfHue = randint(0,255)
Lock = threading.Lock()
Pressed = config.KEY_NONE
Connected = False
Data = b''
To_Send = b''
Good_To_Go = True
Screen = config.SCREEN_NORMAL
Vote = config.VOTE_DEFAULT
KeyListener = ""

def main():
    global pos, WhereTo, Alive, Timer, Legal, Moving, Players, SelfHue, Connected, Start, Data, To_Send, Pressed, Screen, Vote, Good_To_Go
    # Self Explanatory
    x = threading.Thread(target=keyboard_thread)
    y = threading.Thread(target=audio_thread)
    z = threading.Thread(target=network_thread)
    z.start()
    
    SelfGraph = clientgraphics.clientgraphics()
    clientgraphics.clientgraphics.openingscreen(SelfGraph)
    
    # Opening Screen, waiting for a click on the "PLAY" button (Otherwise, acts as said)
    while True:
        a = clientgraphics.clientgraphics.getclick(SelfGraph, config.GETCLICK_OPENING)
        clientgraphics.clientgraphics.tick(SelfGraph)
        if a is False:
            break
        if a is True:
            time.sleep(0.25)
            clientgraphics.clientgraphics.Quit(SelfGraph)
            Lock.acquire()
            Good_To_Go = False
            Lock.release()
            z.join()
            exit()
    
    # Waiting for server to respond
    while not Connected:
        clientgraphics.clientgraphics.Glow(SelfGraph,1)
        clientgraphics.clientgraphics.pump(SelfGraph)
    
    # Waiting for enough players
    while True:
        Condition = cleanXYZ(Data.decode())
        if Condition.startswith(config.START_CON):
            break
        else:
            if Condition.count(config.NETWORK_MESSAGE_DIV) - 1 > 0:
                Players = Condition.count(config.NETWORK_MESSAGE_DIV)
            clientgraphics.clientgraphics.WaitingScreen(SelfGraph, Players)
            clientgraphics.clientgraphics.pump(SelfGraph)
    
    # Starting
    clientgraphics.clientgraphics.play_START(SelfGraph)
    y.start()
    x.start()
    Winner = ""
    
    # Main Loop
    while Good_To_Go:
        try:
            if Screen == config.SCREEN_NORMAL:
                clientgraphics.clientgraphics.pump(SelfGraph)
            ECOORDS = cleanXYZ(Data.decode())
            if ECOORDS.startswith(config.FINISH_CON):
                Winner = ECOORDS.split(config.NETWORK_MESSAGE_DIV)[1]
                break
            ECOORDS = ECOORDS.replace(config.START_CON + config.NETWORK_MESSAGE_DIV,"")
            move(SelfGraph)
            IsMoving()
            if not x.is_alive():
                break
            if not clientgraphics.clientgraphics.update(SelfGraph, Pos, ECOORDS, WhereTo, Legal):
                break

            Lock.acquire()
            Alive = clientgraphics.clientgraphics.IsAlive(SelfGraph)
            Screen = clientgraphics.clientgraphics.GetScreen(SelfGraph)
            if Screen == config.SCREEN_IN_MEETING:
                Vote = clientgraphics.clientgraphics.GetVote(SelfGraph)
            else:
                Vote = config.VOTE_DEFAULT
            To_Send = to_send().encode()
            Pressed = config.KEY_NONE
            Lock.release()
        except Exception as e:
            pass
    
    # Loop Done
    Lock.acquire()
    Good_To_Go = False
    Lock.release()
    
    time.sleep(0.25)
    Lock.acquire()
    KeyListener.stop()
    Lock.release()
    x.join()
    y.join()
    z.join()
    
    temptime = time.time()
    while (time.time() - temptime) < 4:
        clientgraphics.clientgraphics.pump(SelfGraph)
        clientgraphics.clientgraphics.EndScreen(SelfGraph, Winner)
    print("Thanks for playing!")

# Returning a build message
def to_send():
    send = str(Pos[0]-15) + config.NETWORK_FIELD_DIV + str(Pos[1]-25) + config.NETWORK_FIELD_DIV + str(WhereTo[0][len(WhereTo[0])-1])
    send += config.NETWORK_FIELD_DIV + str(WhereTo[1]) + config.NETWORK_FIELD_DIV + str(SelfHue) + config.NETWORK_FIELD_DIV + str(int(Alive))
    send += config.NETWORK_FIELD_DIV + Pressed + config.NETWORK_FIELD_DIV + str(Screen) + config.NETWORK_FIELD_DIV + str(Vote) + config.NETWORK_MESSAGE_DIV
    return send

# Getting the first message in the mess from the server
def cleanXYZ(Ec):
    try:
        return Ec.split(config.NETWORK_EOM)[0]
    except Exception as e:
        return Ec

# Moves the character
def move(SelfGraph):
    global pos, WhereTo, Alive, Timer, Legal, Moving
    if (Moving and clientgraphics.clientgraphics.legal(SelfGraph, WhereTo)):
        if WhereTo[0][0] == config.UP:
            Pos[1] -= clientgraphics.clientgraphics.getcorrectsizeY(SelfGraph, config.MOVEMENT)
        elif WhereTo[0][0] == config.DOWN:
            Pos[1] += clientgraphics.clientgraphics.getcorrectsizeY(SelfGraph, config.MOVEMENT)
        elif WhereTo[0][0] == config.LEFT:
            Pos[0] -= clientgraphics.clientgraphics.getcorrectsizeX(SelfGraph, config.MOVEMENT)
        elif WhereTo[0][0] == config.RIGHT:
            Pos[0] +=clientgraphics.clientgraphics.getcorrectsizeX(SelfGraph,  config.MOVEMENT)

# Stopping movement if needed
def IsMoving():
    global pos, WhereTo, Alive, Timer, Legal, Moving
    if float(time.time() - Timer) > 0.1 and WhereTo[1] == 0:
        WhereTo[1] = config.NOT_MOVING
        Moving = False

# The network thread
def network_thread():
    global Connected, Lock, Start, Data, To_Send, Good_To_Go
    try:
        SelfNet = clientnetwork.clientnetwork()
        
        while not clientnetwork.clientnetwork.connect(SelfNet):
            SelfNet = clientnetwork.clientnetwork()
        
        Lock.acquire()
        Connected = True
        Lock.release()
        
        while Good_To_Go:
            temp = clientnetwork.clientnetwork.get_data(SelfNet)[1]
            Lock.acquire()
            Data = temp
            Lock.release()
            clientnetwork.clientnetwork.send_data(SelfNet, To_Send)
        
        clientnetwork.clientnetwork.close(SelfNet)
        del SelfNet
    except Exception as e:
        pass
    

# Background audio
def audio_thread():
    try:
        pygame.init()
        pygame.mixer.music.load(config.AUDIO_FILE)
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play()
    except Exception as e:
        pass

 # Keyboard listener start
def keyboard_thread():
    global KeyListener, Lock
    with Listener(on_press=on_press, on_release=on_release) as listener:
        Lock.acquire()
        KeyListener = listener
        Lock.release()
        listener.join()

# Keyboard listener main
def on_press(key):
    if Screen != 0:
        return
    global pos, WhereTo, Alive, Timer, Legal, Moving, running, Pressed, Good_To_Go, Lock
    if not (key != Key.up and key != Key.down and key != Key.left and key != Key.right and key != Key.esc):
        Moving = True
        WhereTo[1] = config.MOVING
        if float(time.time() - Timer) < 0.2:
            return
        Timer = time.time()
        if key == Key.up:
            WhereTo[0] = (config.UP + WhereTo[0][len(WhereTo[0])-1])[0:2]
        elif key == Key.down:
            WhereTo[0] = (config.DOWN + WhereTo[0][len(WhereTo[0])-1])[0:2]
        elif key == Key.right:
            WhereTo[0] = config.RIGHT
        elif key == Key.left:
            WhereTo[0] = config.LEFT
        elif key == Key.esc:
            #clientgraphics.clientgraphics.Quit(SelfGraph)
            Lock.acquire()
            Good_To_Go = False
            Lock.release()
            exit()
    try:
        if float(time.time() - Timer) < 0.2:
            return
        if key == Key.space:
            Pressed = config.KEY_FUNC
        elif key.char == config.KEY_KILL:
            Pressed = config.KEY_KILL
    except Exception as e:
        pass


def on_release(key):
    pass

if __name__ == "__main__":
    main()
