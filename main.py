import rtmidi

def main():
    midiin = rtmidi.MidiIn(name="Midi Translator")

    get_ports_out = get_ports(midiin)
    if get_ports_out == False:
        print("No ports found!")
        raise KeyboardInterrupt
    else:
        print(get_ports_out)

    while True:
        try:
            port_num = int(input("Port to open: "))
            midiin.open_port(port_num)
            print("Opened port {}.".format(port_num))
            break
        except (ValueError, rtmidi._rtmidi.InvalidPortError, rtmidi._rtmidi.RtMidiError):
            print("Enter valid port number!")

    while True:
        message = midiin.get_message()
        if message != None:
            message = message[0]

            #sort messages             add yaml parser




def get_ports(midiin):
    ports = midiin.get_ports()
    msg = ""
    if len(ports) == 0:
        return False
    else:
        for port in ports:
            splitted = port.split(" ")
            msg += "Port {} with name {} found!\n".format(splitted[1], splitted[0])
        return msg


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Shutting down program!")