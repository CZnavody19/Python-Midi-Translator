import rtmidi as midi
import keyboard
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume, IAudioEndpointVolume
import psutil
from numpy import interp
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import yaml

port = None

volumes = {}

pot = {}
pad = {}

def slider(id, value):
    norm_val = interp(value, [0,127], [0,1])
    message = "Set volume of {} to {}%"

    try:
        if pot[id] == "main":
            volumes[id].SetMasterVolumeLevelScalar(norm_val, None)
            print(message.format(pot[id], round(norm_val*100)))
        else:
            volumes[id].SetMasterVolume(norm_val, None)
            print(message.format(pot[id], round(norm_val*100)))
    
    except KeyError:
        pass

def pad_on(id):
    try:
        key = pad[id]
        keyboard.press_and_release(key)
        print("Pressed {}".format(key))

    except KeyError:
        pass

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
    global volumes

    for vol in pot:
        vol_name = pot[vol]
        if vol_name == "main":
            volumes[vol] = get_master_volume_obj()
        else:
            volumes[vol] = get_app_volume_obj(vol_name)

def get_config():
    global port
    global pad
    global pot

    config = None

    with open("config.yml", "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError:
            print("Could not read config file!")

    port = config["setup"]["port"]
    pad = config["PAD"]
    pot = config["POT"]


def main():
    get_config()

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
                slider(message[0][1], message[0][2])
            elif mode == 144:
                pad_on(message[0][1])
            elif mode == 128:
                pad_off(message[0][1])
            elif mode == 192:
                prg_swtch(message[0][1])
 
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Shutting down app!")