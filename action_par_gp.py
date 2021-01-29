from tkinter import *
import time
from tkinter.filedialog import askopenfilename
from tkinter import simpledialog
import re
import netmiko
from netmiko import ConnectHandler

groups_name = []
device_inventory = []
path_to_cli_file = ""
cli_file_commands = []
username = ""
password = ""
secret = ""


def is_open(ip, port, timeout):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((ip, int(port)))
        return True
    except:
        return False
    finally:
        s.close()


def check_host(ip, port, retry, delay, timeout):
    ip_up = False
    for i in range(retry):
        if is_open(ip, port, timeout):
            ip_up = True
            break
        else:
            print("tentative " + str(i + 1) + "/2 KO ")
            # time.sleep(delay)
    return ip_up


def test_port_open(switch_name, port_to_test):
    # global device_is_down
    ip = switch_name
    port = 22
    retry = 2
    delay = 2
    timeout = 2
    if check_host(ip, port, retry, delay, timeout):
        # print (ip + " is UP")
        return True
    else:
        print("    ---->  " + ip + " iS DOWN sur le port " + str(port))
        print(" ")
        return False


def exec_ssh(device):
    cisco_r_ios_15_2 = {
        'device_type': 'cisco_ios',
        'host': device,
        'username': username,
        'password': password,
        'secret': secret,
    }

    try:
        # print(secret)
        net_connect = ConnectHandler(**cisco_r_ios_15_2)
        net_connect.enable()
        output = net_connect.send_config_set(cli_file_commands)
        output2 = net_connect.send_command("write memory")
        net_connect.disconnect()

        print(output)
        print(output2)

    except netmiko.ssh_exception.NetmikoTimeoutException:
        print("     --> Device injoignable : ")
        #exit()


def load_cli_file():
    global path_to_cli_file
    global cli_file_commands
    path_to_cli_file = askopenfilename(title='Select fichier')  # shows dialog box and return the path
    cli_read_file = open(path_to_cli_file, "r", encoding="utf8")
    cli_file_commands_tmp = cli_read_file.readlines()
    cli_read_file.close()
    for i in cli_file_commands_tmp:
        cli_file_commands.append(i.replace('\n', ''))


def ask_pwd():
    return simpledialog.askstring("Input", "PWD", show="*")


def ask_username():
    return simpledialog.askstring("Username", "USERNAME")


def ask_secret():
    return simpledialog.askstring("ENable", "ENABLE")


def executer_les_commandes(gp_row):
    global username
    global password
    global secret

    if path_to_cli_file == "":
        load_cli_file()
    if username == "":
        username = ask_username()

    if password == "":
        password = ask_pwd()

    if secret == "":
        secret = ask_secret()

    print("execution des commandes pour le gp de devices suivant:")
    print("-->  " + str(gp_row))
    print("")
    print("Commandes qui seront éxécutées:")
    print(cli_file_commands)

    # lancer connection ssh et execution des commandes vers:
    print("### Début de l'éxécution ###")
    for row, one_device in enumerate(device_inventory):
        if one_device['gp_name'] == gp_row:
            print(one_device['device_name'])

            exec_ssh(one_device['device_name'])
            time.sleep(1)

    print("Fin de l'éxécution")
    print("#################")
    print("")


def launch_script():
    from tkinter.filedialog import askopenfilename

    def open_file():
        name = askopenfilename()
        print(name)
        return name

    path_to_cli_file = open_file()
    cli_read_file = open(path_to_cli_file, "r", encoding="utf8")
    # cli_read_file = open("C:/Users/Florent/Desktop/liste_sw2", "r", encoding="utf8")
    lines = cli_read_file.readlines()

    for line in lines:
        # line.split(',')
        # print(line)
        device_name, sep, gp_name = line.partition(',')
        gp_name = gp_name.replace('\n', '')
        one_device = {'device_name': device_name, 'gp_name': gp_name}
        device_inventory.append(one_device)
        if gp_name not in groups_name:
            groups_name.append(gp_name)
        # print(gp_name)
        # switchs_list.append(line.strip())

    print(device_inventory)
    print(groups_name)

    # def affichee_gp():
    # affichage des groupes
    for gp in groups_name:
        print("###      " + gp)
        for row, one_device in enumerate(device_inventory):
            if one_device['gp_name'] == gp:
                print(str(row) + " " + str(one_device))


# switchs_list = sorted(list(set(switchs_list)))
# print(switchs_list)


########################################


root = Tk()
# create all of the main containers
top_frame = Frame(root, bg='lavender', width=450, height=50, pady=3)
center = Frame(root, bg='lavender', width=50, height=40, padx=3, pady=3)
btm_frame = Frame(root, bg='lavender', width=450, height=45, pady=3)
btm_frame2 = Frame(root, bg='lavender', width=450, height=60, pady=3)

# layout all of the main containers
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

top_frame.grid(row=0, sticky="ew")
center.grid(row=1, sticky="nsew")

# create the widgets for the top frame
model_label = Label(top_frame, text='Les groupes existants et leurs équipements:')
# width_label = Label(top_frame, text='Width:')
# length_label = Label(top_frame, text='Length:')


# layout the widgets in the top frame
model_label.grid(row=0, columnspan=3)

launch_script()

# create the center widgets
center.grid_rowconfigure(0, weight=1)
center.grid_columnconfigure(1, weight=1)

# Creer les frames selons les groupes

list_of_devices = ""
for row, gp_name in enumerate(groups_name):
    list_of_devices = ""
    print(row)
    ctr_mid = Frame(center, bg='lavender', width=250, height=190, padx=3, pady=3)
    ctr_mid.grid(row=0, column=row, sticky="nsew")
    model_label_ctr = Label(ctr_mid, text=gp_name)
    model_label_ctr.grid(row=0, columnspan=3)

    for row, one_device in enumerate(device_inventory):
        if one_device['gp_name'] == gp_name:
            list_of_devices = list_of_devices + "\n" + one_device['device_name']

    model_label_ctr2 = Label(ctr_mid, text=list_of_devices)
    model_label_ctr2.grid(row=1, columnspan=3)
    button_action = Button(ctr_mid, text='Exécuter', command=lambda gp_name=gp_name: executer_les_commandes(gp_name))
    button_action.grid(row=2, columnspan=3)
root.mainloop()