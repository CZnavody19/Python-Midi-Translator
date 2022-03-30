import rtmidi as midi
import keyboard
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume, IAudioEndpointVolume
import psutil
from numpy import interp
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

port = 0

main = None
discord = None
chrome = None

def slider(id, value):
    norm_val = interp(value, [0,127], [0,1])
    message = "Set volume of {} to {}%"

    if id == 1 and main !=None:
        app = "Main"
        main.SetMasterVolumeLevelScalar(norm_val, None)
        print(message.format(app, round(norm_val*100)))
    elif id == 2 and discord !=None:
        app = "Discord"
        discord.SetMasterVolume(norm_val, None)
        print(message.format(app, round(norm_val*100)))
    elif id == 3 and chrome !=None:
        app = "Chrome"
        chrome.SetMasterVolume(norm_val, None)
        print(message.format(app, round(norm_val*100)))



def pad_on(id):
    if id == 36:
        key = "F8"
        keyboard.press_and_release(key)
        print("Pressed {}".format(key))

def pad_off(id):
    pass

def prg_swtch(id):
    pass


def findProcessIdByName(processName):
    '''
    Get a list of all the PIDs of a all the running process whose name contains
    the given string processName
    '''
    listOfProcessObjects = []
    #Iterate over the all the running process
    for proc in psutil.process_iter():
       try:
           pinfo = proc.as_dict(attrs=['pid', 'name'])
           # Check if process name contains the given name string.
           if processName.lower() in pinfo['name'].lower() :
               listOfProcessObjects.append(pinfo['pid'])
       except (psutil.NoSuchProcess, psutil.AccessDenied , psutil.ZombieProcess) :
           pass
    return listOfProcessObjects

def get_app_volume_obj(name):
    sessions = AudioUtilities.GetAllSessions()
    processid = findProcessIdByName(name)
    for session in sessions:
        volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        for proc_id in processid:
            if session.ProcessId == proc_id:
                print("Found session with id {}".format(session.ProcessId))
                return volume

def get_master_volume_obj():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    print("Got main volume!")
    return volume

def init_volume():
    global discord
    global chrome
    global main
    chrome = get_app_volume_obj("Chrome")
    discord = get_app_volume_obj("Discord")
    main = get_master_volume_obj()

def main():
    init_volume()

    midi_in = midi.MidiIn()
    try:
        opened_port = midi_in.open_port(port)
        print("Opened port {}".format(port))
    except (midi._rtmidi.SystemError, midi._rtmidi.InvalidPortError, midi._rtmidi.RtMidiError):
        print("Invalid port selected ({})".format(port))
        raise KeyboardInterrupt

    while True:
        message = opened_port.get_message()
        if message != None:
            mode = message[0][0]
            if mode	== 176:
                id = message[0][1]
                value = message[0][2]
                slider(id, value)
            elif mode == 144:
                id = message[0][1]
                pad_on(id)
            elif mode == 128:
                id = message[0][1]
                pad_off(id)
            elif mode == 192:
                id = message[0][1]
                prg_swtch(id)
 
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Shutting down app!")