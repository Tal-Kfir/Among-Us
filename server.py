import socket
import threading
import random
import datetime
import time
import config

Thread_Dict = {}
Screen_Dict = {}
Alive_lst = []
Condition = config.IDLE_CON + config.NETWORK_MESSAGE_DIV
Winner = ""
Print_Lock = threading.Lock()
Impost = ""
Special_Coords = [(1690, 310), (1910, 400), (1755, 601), (2355, 670), (2154,635), (1837, 1063), (1527, 1177), (1362, 1063), (1400, 850), (1746, 850), (1248,254), (1158, 692), (1220,787), (1078, 783), (608, 1008), (663, 864), (775, 670), (490, 711)
                    , (571, 607), (700, 338), (608, 491), (1664, 1067)]
Emergency = (1450, 424)
Timer = datetime.datetime.now()
Start_Time = datetime.datetime.now()
Emerge = False
Finish_Time = ""
Running = False

# Restores all vars
def Initialize():
    global Print_Lock, Thread_Dict, Screen_Dict, Alive_lst, Condition, Winner, Impost, Special_Coords, Emerge, Timer, Start_Time, Finish_Time, Running
    Print_Lock.acquire()
    Thread_Dict = {}
    Screen_Dict = {}
    Alive_lst = []
    Condition = config.IDLE_CON + config.NETWORK_MESSAGE_DIV
    Winner = ""
    Impost = ""
    Special_Coords = [(1690, 310), (1910, 400), (1755, 601), (2355, 670), (2154,635), (1837, 1063), (1527, 1177), (1362, 1063), (1400, 850), (1746, 850), (1248,254), (1158, 692), (1220,787), (1078, 783), (608, 1008), (663, 864), (775, 670), (490, 711)
                        , (571, 607), (700, 338), (608, 491), (1664, 1067)]
    Emergency = (1450, 424)
    Timer = datetime.datetime.now()
    Start_Time = datetime.datetime.now()
    Emerge = False
    Finish_Time = ""
    Running = False
    Print_Lock.release()


# Returns if game is over
def IsOver():
    global Print_Lock, Winner
    if not Print_Lock.locked():
        Print_Lock.acquire()
    Result = False
    if Condition == config.FINISH_CON + config.NETWORK_MESSAGE_DIV:
        Result = True
    elif len(Alive_lst) == 1 and Alive_lst[0] == Impost:
        Winner = "Impost"
        Result = True
    elif abs((Start_Time-datetime.datetime.now()).total_seconds())/60 >= 5:
        Winner = "Impost"
        Result = True
    elif len(Alive_lst) >= 1 and (not Impost in Alive_lst):
        Winner = "Crew"
        Result = True
    elif Special_Coords == list() and len(Alive_lst) >= 1:
        Winner = "Crew"
        Result = True
    elif len(Thread_Dict.keys()) > 0:
        if list(filter(lambda x: x.is_alive(), Thread_Dict.keys())) == list():
            Result = True
    else:
        Result = True
    
    if Print_Lock.locked():
        time.sleep(0.1)
        if Print_Lock.locked():
            Print_Lock.release()
    return Result

# Acting according to player's keyboard actions
def act():
    for i in Thread_Dict.keys():
        data = Thread_Dict[i].split(config.NETWORK_FIELD_DIV)
        if len(data) < 6:
            continue
        if data[7] == '2':
            Print_Lock.acquire()
            Screen_Dict[i] = 0
            RemoveTask(i)
            Print_Lock.release()
            return
        if data[5] == '1' and data[7] == '0':
            if data[6] == config.KEY_FUNC:
                SwitchScreen(i)
            elif data[6] == config.KEY_KILL:
                kill(i)
    if Print_Lock.locked():
        time.sleep(0.1)
        if Print_Lock.locked():
            Print_Lock.release()

# Removes a task when completed
def RemoveTask(this):
    global Screen_Dict
    X,Y = int(Thread_Dict[this].split(config.NETWORK_FIELD_DIV)[0]), int(Thread_Dict[this].split(config.NETWORK_FIELD_DIV)[1])
    for i in Special_Coords:
        if CalculateDistance((X, Y), i) <= 115:
            Special_Coords.remove(i)
            break

# Calculate the distance between two points 
def CalculateDistance(PointOne, PointTwo):
    return ((PointTwo[0] - PointOne[0])**2 + (PointTwo[1] - PointOne[1])**2)**0.5

# Switching the player's screen (Mission to main and so)
def SwitchScreen(this):
    global Screen_Dict, Print_Lock, Timer, Emerge
    X,Y = int(Thread_Dict[this].split(config.NETWORK_FIELD_DIV)[0]), int(Thread_Dict[this].split(config.NETWORK_FIELD_DIV)[1])
    if not this in Alive_lst:
        return
        
    for i in Special_Coords:
        if CalculateDistance((X, Y), i) <= 75:
            Print_Lock.acquire()
            Screen_Dict[this] = random.randint(1,8)
            Print_Lock.release()
            break
    else:
        if CalculateDistance((int(Thread_Dict[this].split(config.NETWORK_FIELD_DIV)[0]), int(Thread_Dict[this].split(config.NETWORK_FIELD_DIV)[1])), Emergency) <= 150:
            Print_Lock.acquire()
            for j in Screen_Dict.keys():
                Screen_Dict[j] = 9
            Timer = datetime.datetime.now()
            Emerge = True
            Print_Lock.release()

# Killing a nearby player
def kill(this):
    global Print_Lock
    if Impost != this or not this in Alive_lst:
        return
    temp = Thread_Dict.copy()
    temp.pop(this)
    X,Y = int(Thread_Dict[this].split(config.NETWORK_FIELD_DIV)[0]), int(Thread_Dict[this].split(config.NETWORK_FIELD_DIV)[1])
    
    for i in temp.keys():
        tempX, tempY = int(temp[i].split(config.NETWORK_FIELD_DIV)[0]), int(temp[i].split(config.NETWORK_FIELD_DIV)[1])
        distance = CalculateDistance((X, Y), (tempX, tempY))
        if distance <= 40:
            if not Print_Lock.locked():
                Print_Lock.acquire()
            if i in Alive_lst:
                Alive_lst.remove(i)
                
            Print_Lock.release

# Building a message to a player
def BuiltMessage():
    global Thread_Dict, Condition
    temp = Thread_Dict.copy()
    if threading.current_thread() in temp.keys():
        temp.pop(threading.current_thread())
    a = (Condition + (config.NETWORK_MESSAGE_DIV).join(temp.values())).encode()
    
    if Condition == config.IDLE_CON + config.NETWORK_MESSAGE_DIV:
        for i in temp.keys():
            a+=config.NETWORK_MESSAGE_DIV.encode()
    
    if Condition == config.START_CON + config.NETWORK_MESSAGE_DIV:
        a += (config.NETWORK_MESSAGE_DIV + str(int(Impost == threading.current_thread())) + config.NETWORK_FIELD_DIV + str(int(threading.current_thread() in Alive_lst))).encode()
        a += (config.NETWORK_FIELD_DIV + str(Screen_Dict[threading.current_thread()])).encode()
    
    if Condition == config.FINISH_CON + config.NETWORK_MESSAGE_DIV and Winner != "":
        a = (Condition + Winner).encode()
    
    if Condition == config.FINISH_CON + config.NETWORK_MESSAGE_DIV and Winner == "":
        a = (config.START_CON + config.NETWORK_MESSAGE_DIV + (config.NETWORK_MESSAGE_DIV).join(temp.values())).encode() 
        a += (config.NETWORK_MESSAGE_DIV + str(int(Impost == threading.current_thread())) + config.NETWORK_FIELD_DIV).encode()
        a += (str(int(threading.current_thread() in Alive_lst)) + config.NETWORK_FIELD_DIV + str(Screen_Dict[threading.current_thread()])).encode()
    a += config.NETWORK_EOM.encode()
    return a

# The thread loop
def threaded(c):
    global Print_Lock, Thread_Dict, Emerge
    c.settimeout(0.1)
    if Print_Lock.locked():
        Print_Lock.release()
    while True:
        if Print_Lock.locked():
            Print_Lock.release()
        try:
            c.send(BuiltMessage())
            data = c.recv(1024)
            if data != b'':
                if not Print_Lock.locked():
                    Print_Lock.acquire()
                Thread_Dict[threading.current_thread()] = data[:data.index(config.NETWORK_MESSAGE_DIV.encode())].decode()
                
                # If a meeting is over, kill self if voted off
                if Screen_Dict[threading.current_thread()] == 9 and abs((Timer - datetime.datetime.now()).total_seconds()) > 30:
                    data = data[:data.index(config.NETWORK_MESSAGE_DIV.encode())]
                    Emerge = False
                    Screen_Dict[threading.current_thread()] = 0
                    templst = [int(i.split(config.NETWORK_FIELD_DIV)[8]) for i in Thread_Dict.values()]
                    if int(data.decode().split(config.NETWORK_FIELD_DIV)[8]) == max(templst) and templst.count(int(data.decode().split(config.NETWORK_FIELD_DIV)[8])) == 1:
                        tempd = Alive_lst.copy()
                        tempd.remove(threading.current_thread())
                        Alive_lst.remove(tempd[int(data.decode().split(config.NETWORK_FIELD_DIV)[8])])
                    
            if Print_Lock.locked():
                Print_Lock.release()
            act()
            if Print_Lock.locked():
                Print_Lock.release()
        except socket.timeout as e:
            if Print_Lock.locked():
                Print_Lock.release()
                
        except Exception as e:
            break
    if Print_Lock.locked():
        Print_Lock.release()
    c.close()

# IS-OVER thread
def L():
    global Print_Lock, Thread_Dict, Condition, Impost, Finish_Time, Running
    if Print_Lock.locked():
        Print_Lock.release()
    while True:
        if not Print_Lock.locked():
            Print_Lock.acquire()
        if Condition != config.IDLE_CON + config.NETWORK_MESSAGE_DIV:
            if not IsOver():
                continue
            Condition = config.FINISH_CON + config.NETWORK_MESSAGE_DIV
            if Finish_Time == "":
                Finish_Time = datetime.datetime.now()
            elif abs((Finish_Time-datetime.datetime.now()).total_seconds()) >= 5:
                Running = False
                for t in Thread_Dict.keys():
                    t.join()
                if Print_Lock.locked():
                    time.sleep(0.1)
                    if Print_Lock.locked():
                        Print_Lock.release()
                Initialize()
                if Print_Lock.locked():
                    Print_Lock.release()
                
                break
        
        if not Print_Lock.locked():
            Print_Lock.acquire()
        if Print_Lock.locked():
            time.sleep(0.1)
            if Print_Lock.locked():
                Print_Lock.release()


# Main thread loop
def Main():
    global Print_Lock, Thread_Dict, Condition, Impost, Finish_Time, Running
    host = ""
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("socket is listening")
    s.settimeout(0.1)
    IsOverThread = threading.Thread(target = L)
    IsOverThread.start()
    
    while True:  
        # If a game is over, renew
        if not IsOverThread.is_alive():
            print("GAME OVER")
            IsOverThread.join()
            IsOverThread = threading.Thread(target = L)
            IsOverThread.start()
        if Print_Lock.locked():
            Print_Lock.release()
        # If enough players are in, start
        if len(Thread_Dict.keys()) > 1 and Condition == config.IDLE_CON + config.NETWORK_MESSAGE_DIV:
            Print_Lock.acquire()
            Condition = config.START_CON + config.NETWORK_MESSAGE_DIV
            Impost = random.choice(list(Thread_Dict.keys()))
        # If Impostor logged out, choose a second one
        elif Condition == config.START_CON + config.NETWORK_MESSAGE_DIV and not Impost.is_alive() and len(Thread_Dict.keys()) > 0:
            Print_Lock.acquire()
            Impost = random.choice(list(Thread_Dict.keys()))
        try:
            # Accept loop
            s.listen(1)
            c, addr = s.accept()
            if len(Thread_Dict.keys()) < 9:
                print('Connected to :', addr[0], ':', addr[1])
                if not Print_Lock.locked():
                    Print_Lock.acquire()
                Running = True
                t = threading.Thread(target=threaded, args = (c,))
                t.name = addr
                t.start()
                Alive_lst.append(t)
                Screen_Dict[t] = 0
                Thread_Dict[t] = ""
            if Print_Lock.locked():
                Print_Lock.release()
        except socket.timeout as e:
            if Print_Lock.locked():
                Print_Lock.release()
        
        # Delete non-active threads
        if Print_Lock.locked():
            Print_Lock.release()
        a = []
        for i in Thread_Dict.keys():
            if not i.is_alive():
                i.join()
                a.append(i)
        if Print_Lock.locked():
            Print_Lock.release()
        for j in a:
            if not Print_Lock.locked():
                Print_Lock.acquire()
            if j in Alive_lst:
                Alive_lst.remove(j)
            if j in Screen_Dict.keys():
                Screen_Dict.pop(j)
            if Print_Lock.locked():

                Print_Lock.release()
                    

                
    s.close()


if __name__ == '__main__':
	Main()