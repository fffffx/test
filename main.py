# common import module
import configparser
import os
import socket
import time
import tkinter as tk
# tkinter import module
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
from tkinter.filedialog import askopenfilename

# network import module
import netmiko
import paramiko
from netmiko import ConnectHandler

# Global statements
path_file_ini = "environments_save.ini"
environments_list = []
list_import = "0"
do_not_load_env = "0"
new_env_added = []
username_list = []
user_name = ""
password = ""
secret = ""
cli_file_commands = []

# Launch putty , via test port 22 or 23:  ##########################################################
# For netmiko
cisco_r_ios_15_2 = {
    'device_type': 'cisco_ios',
    'host': '192.168.23.130',
    # 'username': 'admin',
    # 'password': 'admin',
    # 'port' : 8022,          # optional, defaults to 22
    # 'secret': 'secret',     # optional, defaults to ''
}


# Check if device is reachable, else, ignore connexion to the switch

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
            time.sleep(delay)
    return ip_up


def test_port_open(switch_name, port_to_test):
    # global device_is_down
    ip = switch_name
    port = port_to_test
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


def ask_username():
    return simpledialog.askstring("Username", "USERNAME")


def ask_pwd():
    return simpledialog.askstring("Input", "PWD", show="*")


def telnet_launch(devices):
    global user_name
    global password
    if user_name == "":
        user_name = ask_username()

    if password == '':
        password = ask_pwd()

    # Test if SSH enable and telnet after

    for i in [22, 23]:

        try:
            if i == 22:
                # putty admin@192.168.23.129 -ssh
                print("tentative de connexion SSH en cours")
                cisco_r_ios_15_2['host'] = devices
                cisco_r_ios_15_2['username'] = user_name
                cisco_r_ios_15_2['password'] = password
                net_connect = ConnectHandler(**cisco_r_ios_15_2)
                net_connect.disconnect()
                print("connecté en ssh")

                os.system("start putty.exe " + user_name + "@" + devices + " -ssh 22 -pw " + password)

                break
            elif i == 23:
                # putty admin@192.168.23.129 -telnet
                print("tentative de connexion TELNET en cours")
                if test_port_open(devices, i):
                    print("connecté en telnet ")
                    os.system("start putty.exe " + user_name + "@" + devices + " -telnet 23 ")

            print(devices)
        except netmiko.ssh_exception.NetmikoTimeoutException:
            print("   " + devices + " -----> Timeout sur le port SSh 22  ")
        except paramiko.ssh_exception.SSHException:
            print("   " + devices + " -----> Probleme coté serveur SSH  ")


# end of PUTTY ##########################################################

###### SIMPLE ACTION BLOC ##############################

def simple_action(action):
    import threading
    import random
    import time
    import os
    global user_name
    global password
    #global
    import tempfile
    #thread_to_connect_to_devices = threading.Thread(target= print, args =['User', 'pwd','ip', 'command'], kwargs={'sep': ' ---- '})

    #thread_to_connect_to_devices.start()
    # renvoi : User----pwd----ip----command

    list_of_thread = []
    #exemple:
    #liste_switchs = ['sw1', 'sw2', 'sw3', 'sw4']
    for j in range(0, len(dico_environments)):
        if dico_environments[j]['name'] == env_select.get():
            print("         " + str(dico_environments[j]['devices_list']))
            liste_switchs = dico_environments[j]['devices_list']

    #user= "admin"
    #password= "cisco"
    if user_name == "":
        user_name = ask_username()

    if password == '':
        password = ask_pwd()

    #commande = "sh ip int brief"
    commande = action
    cmd_used = commande.replace(' ', '_')



    def connect_ssh(usr,pwd,ip,command):
        file_name="sw_" + str(ip) + ".cfg"
        path= "tempo_extract\\" + file_name
        pp = open(path, "w")
        print ("on se connecte à : " + str(ip))
        time_to_wait= random.randint(1,3)
        time.sleep(time_to_wait)
        #print (ip + " : " + usr +  " : " +  pwd +  " : " +  command)
        pp.write(ip + " : " + usr +  " : " +  pwd +  " : " +  command + '\n')
        #print("#")
        #print("wait time de   : " + str(time_to_wait) + " pour : " + str(ip) )
        pp.write("wait time de   : " + str(time_to_wait) + " pour : " + str(ip))
        print("on a recup la conf de  : " + str(ip))
        pp.close()

    #os.rmdir("tempo_extract")
    #Creer un dossier pour y metrre les command
    #os.mkdir("tempo_extract")

    #with tempfile.TemporaryDirectory() as directory:
        #print('The created temporary directory is %s' % directory)

    path_dir=os.getcwd() + "\\tempo_extract"
    # Vérifie si le repertoire n'existe pas, dans ce cas on le créé.
    try:
        os.makedirs(path_dir, exist_ok=False)
        print("Directory '%s' created successfully" %path_dir)
    except OSError as error:
        print("Directory '%s' can not be created, il existe surement deja")

    for switch in liste_switchs:
        #print(switch)
        #one_thread = threading.Thread(target=connect_ssh, args =( user , password , switch , commande ))
        one_thread = threading.Thread(target=connect_ssh, args=(user_name, password, switch, commande))
        list_of_thread.append(one_thread)
        one_thread.start()

    # wait for all trad to end
    for one_thread  in list_of_thread:
        one_thread.join()

    print("OK passons au traitement")

    #### traitrement ###

    ## VOulez vous sauvegarder en .zip les fichiers récupérés?
    from datetime import datetime
    # datetime object containing current date and time
    now = datetime.now()
    print("now =", now)
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d%m%Y_%H%M%S")
    print("date and time =", dt_string)

    zip_filename=cmd_used +"_" + dt_string + ".zip"
    from zipfile import ZipFile
    import os
    from os.path import basename

    Save_directory=os.getcwd() + "\\Saved_files"
    # Vérifie si le repertoire n'existe pas, dans ce cas on le créé.
    try:
        os.makedirs(Save_directory, exist_ok=False)
        print("Directory '%s' created successfully" %Save_directory)
    except OSError as error:
        print("Directory '%s' can not be created, il existe surement deja")


    # create a ZipFile object
    with ZipFile(Save_directory+"\\" +zip_filename, 'w') as zipObj:
       # Iterate over all the files in directory
       for folderName, subfolders, filenames in os.walk(path_dir):
           for filename in filenames:
               #create complete filepath of file in directory

               filePath = os.path.join(folderName, filename)
               # Add file to zip
               zipObj.write(filePath, basename(filePath))



############ END SIMPLE ACTION BLOC #####################

#####   BLOC - CLI FILE to EXECUTE #####################"

def execute_cli_file():
    global user_name
    global password
    global secret
    path_to_cli_file2=""
    def exec_ssh(device):
        cisco_r_ios_15_2 = {
            'device_type': 'cisco_ios',
            'host': device,
            'username': user_name,
            'password': password,
            'secret': secret,
        }

        try:
            print(device)
            net_connect = ConnectHandler(**cisco_r_ios_15_2)
            net_connect.enable()
            output = net_connect.send_config_set(cli_file_commands)
            output2 = net_connect.send_command("write memory")
            net_connect.disconnect()

            print(output)
            print(output2)

        except netmiko.ssh_exception.NetmikoTimeoutException:
            print("     --> Device injoignable : ")
            # exit()

    def load_cli_file():
        global path_to_cli_file2
        global cli_file_commands
        path_to_cli_file2 = askopenfilename(title='Selectionner le fichier CLI à executer')  # shows dialog box and return the path
        cli_read_file = open(path_to_cli_file2, "r", encoding="utf8")
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

    def executer_les_commandes():
        global user_name
        global password
        global secret

        if path_to_cli_file2 == "":
            load_cli_file()
        if user_name == "":
            user_name = ask_username()

        if password == "":
            password = ask_pwd()

        if secret == "":
            secret = ask_secret()

        #print("execution des commandes pour le gp de devices suivant:")
        #print("-->  " + str(gp_row))
        #print("")
        print("Commandes qui seront éxécutées:")
        print(cli_file_commands)

        # lancer connection ssh et execution des commandes vers:
        print("### Début de l'éxécution ###")
        for row, one_device in enumerate(switchs_list):
            #if one_device['gp_name'] == gp_row:
                #print(one_device['device_name'])

            exec_ssh(one_device)
                #time.sleep(1)

        print("Fin de l'éxécution")
        print("#################")
        print("")

    executer_les_commandes()


############ END - BLOC - CLI FILE to EXECUTE #####################


def scripts_launch(choice):
    print("scripts_launch : " + str(choice))
    if choice == "CLI_config":
        execute_cli_file()
    else:
        simple_action(choice)


def display_radio_button_for_scripts():
    R1 = Radiobutton(ctr_left, text="wr mem", variable=radiobutton_for_script, value="wr mem")
    R1.grid(row=1, column=0, sticky="nsew")
    R2 = Radiobutton(ctr_left, text="sh runn", variable=radiobutton_for_script, value="sh runn")
    R2.grid(row=2, column=0, sticky="nsew")
    R3 = Radiobutton(ctr_left, text="sh ip int brief", variable=radiobutton_for_script, value = "sh ip int brief")
    R3.grid(row=3, column=0, sticky="nsew")
    R4 = Radiobutton(ctr_left, text="CLI_config_file", variable=radiobutton_for_script, value="CLI_config")
    R4.grid(row=4, column=0, sticky="nsew")
    button_validate = Button(ctr_left, text='Lancer le script', command=lambda radiobutton_for_script=radiobutton_for_script: scripts_launch(radiobutton_for_script.get()))
    button_validate.grid(row=7, column=0, sticky="nsew")


# when you click "d'ajout d'environnement" button
def add_environment():
    global do_not_load_env
    name = simpledialog.askstring("Input", "Indiquer le nom du nouvel environnement", parent=top_frame)

    # ask if you want to change environment
    msg_box_continue = tk.messagebox.askquestion("Attention! ",
                                                 "Voulez vous charger cet environnement " + name.upper() + " ?",
                                                 icon='warning')
    # a debug to avoid change content if INI do not exist if callback is call with this modification
    if msg_box_continue == 'yes':
        new_env.set(name.upper())
    else:
        do_not_load_env = "1"
        new_env.set(name.upper())


def add_username():
    new_user.set(simpledialog.askstring("Input", "Indiquer le nom d'utilisateur'", parent=top_frame))


def clear_frame():
    # destroy all widgets from frame
    for widget in ctr_mid.winfo_children():
        widget.destroy()


def process_switch_list():
    global switchs_list
    # switchs_list = switchs_list.replace(' ', '')
    try:
        switchs_list = switchs_list.replace(' ', '')
        switchs_list = switchs_list.replace('\'', '')
        switchs_list = switchs_list.replace('[', '')
        switchs_list = switchs_list.replace(']', '')
        switchs_list = switchs_list.split(",")
    except:
        switchs_list = switchs_list

    # switchs_list.split(",")
    # print("         la liste de devices chargée depuis le fichier INI :" + str(switchs_list))
    # return devices_list


# ok pour TEST = 1
def env_display_devices(test):
    global list_import
    global new_env_added
    global do_not_load_env
    print("     env_display_devices")
    # print("     Test: " + str(Test))
    global switchs_list
    # Clear displays curruently devices
    if do_not_load_env == "0":
        clear_frame()
    print(
        "Test: " + test + " env_select: " + env_select.get() +
        "  new_env:" + new_env.get() + "   list_import:" + list_import +
        " do_not_load_env: " + do_not_load_env)
    # if Test == "1" and env_select.get() != new_env.get():
    # 1=    et 2= import d'une liste de devices
    if test == "1" or test == "3":
        # try:

        # on lit le fichier .INI
        # config = configparser.ConfigParser()
        # config.read('environments_save.ini')
        # switchs_list= config.get(env_select.get(),"switchs_list")
        # traite_liste_ini()

        if test == "3":
            # rien à faire la liste de switch est deja récupérée car c'est un import de liste manuel
            print("         cas 3 rien a faire")
            pass
        elif test == "1" and env_select.get() in new_env_added and list_import != "1":
            # on sort de cette fonction il n'y a rien à afficher

            return
        elif test == "1":
            print("     env added  " + str(new_env_added))
            print("     " + str(dico_environments))

            # on récupere , selon l'environnement, dans le bon dico la liste des switchs:
            for j in range(0, len(dico_environments)):
                if dico_environments[j]['name'] == env_select.get():
                    print("         " + str(dico_environments[j]['devices_list']))
                    switchs_list = dico_environments[j]['devices_list']
            if switchs_list == "[]":
                switchs_list = ""
            else:
                process_switch_list()
            # Ensuite on affiche les devices dans le FRAME
            longueur_liste_sw = len(switchs_list)
            print("nb de devices: " + str(longueur_liste_sw))
            print("#")
            # permet l'affichage correcte de tous les buttons en autorisant le resize
            root.grid_propagate(True)

        # on creer et affiche les boutons qui vont bien
        for row, devices in enumerate(switchs_list):
            widget = Button(ctr_mid, text=devices)
            if row == 0:
                widget.grid(row=row, column=0, sticky="ew")
                widget["command"] = lambda devices=devices: telnet_launch(devices)
            else:
                widget.grid(row=row % 10, column=(row // 10), sticky="ew")
                widget["command"] = lambda devices=devices: telnet_launch(devices)
        display_radio_button_for_scripts()
        # except:
        # print("ENV non trouvé dans le .INI")

    # quand on a modifié NEW_ENV (ajout d'un nouvel ENV)
    elif test == "2":
        new_env_added.append(new_env.get().upper())
        # si le nouvel ENV est CHARGé
        if do_not_load_env == "0":
            print("     test = 2")
            switchs_list = []
            list_import = "0"
            env_select.set(new_env.get().upper())
            env_display_menu("NEW")
        # SI le nouvel ENV n'est pas chargé, alots on va juste ajouter le nom de l'ENV dans le menu déroulant
        else:
            do_not_load_env = "0"
            env_display_menu("NEW")
    print("#")


# n'est plus utilisé####################################
def env_recovery_list():
    print("on va pouvoir charger la liste des environnements du .ini")
    config = configparser.ConfigParser()
    # ligne si dessous nécéssaire pour lire enuite le contenu, section, etc...
    config.read('environments_save.ini')
    # liste des environnements
    print("les environnements trouvés dans le .ini sont: " + str(config.sections()))

    # renvoi la liste des environnements
    return config.sections()


###########################################################################

# testé Ok pour  DEFAULT et TRUE
def env_display_menu(test):
    print("     env_display_menu:")
    print("     Test:" + str(test))
    global environments_list

    if test == "DEFAULT":
        button_env = Button(top_frame, text=test)
        button_env.grid(row=0, column=1)
    elif test is True:
        for j in range(0, len(dico_environments)):
            print("         " + str(dico_environments[j]['name']))
            environments_list.append(dico_environments[j]['name'])
        # creation du menu avec les éléments
        option_list = environments_list
        menu_deroul_env = tk.OptionMenu(top_frame, env_select, *option_list)
        menu_deroul_env.grid(row=0, column=1)
    elif test == "NEW":
        environments_list.append(new_env.get())
        option_list = environments_list
        menu_deroul_env = tk.OptionMenu(top_frame, env_select, *option_list)
        menu_deroul_env.grid(row=0, column=1)
        # On ajoute l'environnement au DICO
        # on rassemble le dictionnaire
        env_unitaire = {'name': new_env.get(), 'devices_list': []}
        # on l'ajoute à l aliste
        dico_environments.append(env_unitaire)


def process_username_list():
    global username_list
    try:
        username_list = username_list.replace(' ', '')
        username_list = username_list.replace('\'', '')
        username_list = username_list.replace('\'', '')
        username_list = username_list.replace('[', '')
        username_list = username_list.replace(']', '')
        username_list = username_list.split(",")
    except:
        username_list = username_list
    # reste à supprimer un objet qui est vide '' dans la liste
    # switchs_list.split(",")
    print("         la liste de user chargée depuis le le dico :" + str(username_list))
    if len(username_list) == 1 and username_list[0] == "":
        del username_list[0]

    # return devices_list


def username_display_menu(test):

    print("     username_display_menu:")
    print("     Test:" + str(test))
    global username_list
    username_scroll_menu = tk.OptionMenu(top_frame, user_select, "")
    username_scroll_menu.destroy()

    if test == "DEFAULT":
        button_env = Button(top_frame, text="EMPTY")
        button_env.grid(row=1, column=1)
    elif test is True:

        try:

            for j in range(0, len(dico_environments)):
                print("         " + str(dico_environments[j]['name']))
                print("         " + str(dico_environments[j]['liste_user']))
                if dico_environments[j]['name'] == env_select.get():
                    username_list = dico_environments[j]['liste_user']
                    print(username_list)
                    process_username_list()
                    break

            print("longueur: " + str(len(username_list)))

        except KeyError:
            print("la liste des utilisateur doit etre vide car il y a une erreur --- keyerror pour liste_user dans dico_environments----" )

        if len(username_list) == 0:
            option_list2 = "X"
            username_scroll_menu = tk.OptionMenu(top_frame, user_select, *option_list2)
            username_scroll_menu.grid(row=1, column=1)
        else:

            option_list2 = username_list
            username_scroll_menu = tk.OptionMenu(top_frame, user_select, *option_list2)
            username_scroll_menu.grid(row=1, column=1)
    elif test == "NEW":
        username_list.append(new_user.get())
        print(username_list)

        option_list2 = username_list
        username_scroll_menu = tk.OptionMenu(top_frame, user_select, *option_list2)
        username_scroll_menu.grid(row=1, column=1)
        # + mettre à jour dico en ajoutant une valeur dans la liste
        for j in range(0, len(dico_environments)):
            if dico_environments[j]['name'] == env_select.get():
                print("toto")
                dico_environments[j]['liste_user'] = username_list
        print(dico_environments)


# OK
def process_list_ini():
    global devices_list

    devices_list = devices_list.replace(' ', '')
    devices_list = devices_list.replace('\'', '')
    devices_list = devices_list.replace('[', '')
    devices_list = devices_list.replace(']', '')
    devices_list = devices_list.split(",")
    # switchs_list.split(",")
    print("         la liste de devices chargée depuis le fichier INI :" + str(devices_list))
    # return devices_list


# Fichier .ini est chargé dans une liste de dictionnaire
# fonctionnement OK
dico_environments = []


def load_ini_data_to_dico():
    global devices_list
    print("     " + "load_ini_data_to_dico:")
    # on lit le fichier .INI
    config = configparser.ConfigParser()
    config.read('environments_save.ini')
    # environments_list = config.get(env_select.get(), "switchs_list")
    environments_list = config.sections()
    for row, env_name in enumerate(environments_list):
        # print(str(row) + " " + str(env_name))
        # on extrait la liste des devices pour chaque ENV
        devices_list = config.get(env_name, "switchs_list")
        # On traite un peu le fichier pour retirer les caractères
        process_list_ini()
        # on rassemble le dictionnaire : NOM, LISTE de USER, liste de DEVICES)
        env_unitaire = {'name': env_name, 'liste_user': config.get(env_name, "username_list"),
                        'devices_list': config.get(env_name, "switchs_list")}
        # on l'ajoute à l aliste
        dico_environments.append(env_unitaire)

    print("     " + str(dico_environments))


# Creer la liste des environnements
def env_load(state):
    if state is True:
        env_select.set("SELECTIONNER")
        # Fonction pour récuperer le contenu du .ini dans un dictionnaire
        load_ini_data_to_dico()
        # envoi l'argument True
        env_display_menu(state)
        username_display_menu(state)
    if state is False:
        print("env_select before assignement " + env_select.get())
        env_select.set("DEFAULT")
        print("env_select after assignement " + env_select.get())
        # On va afficher le nom de l'environnement DEFAULT
        env_display_menu("DEFAULT")
        username_display_menu("DEFAULT")


# Indique si un fichier existe dans le path directory actuel
def is_file_exist(file1):
    if os.path.exists(file1):
        return True
    else:
        return False


# Cherche à charger le .ini s'il existe --> fonctionnement OK
# sert ensuite à selectionner l'environnement de depart suivant True/false
def start_env():
    if is_file_exist(path_file_ini) is True:
        print(".INI existe")
        env_load(True)
    else:
        print(".INI existe pas")
        print("--> On se place donc dans un environnement par défaut.")
        env_load(False)


def open_file():
    name = askopenfilename()
    print(name)
    return name

# SAUVEGARDE ENV #######################################################################################


def save_env():
    if os.path.exists(path_file_ini):
        print("on va sauvegarder dans le fichier .ini existant")
    else:
        print(" ERROR:   fichier .ini non existant, on va le creer pour la sauvegarde")
        # fichier = open("eenvironments_save.ini", "w")
        # fichier.close()
    config = configparser.RawConfigParser()  # On créé un nouvel objet "config"
    # config.read('environments_save.ini')  # On lit le fichier de paramètres
    for j in range(0, len(dico_environments)):
        # dico_environments[j]['devices_list']=switchs_list

        if 'liste_user' in dico_environments[j]:
            config[dico_environments[j]['name']] = {'switchs_list': dico_environments[j]['devices_list'],
                                                  'username_list': dico_environments[j]['liste_user']}
        else:
            config[dico_environments[j]['name']] = {'switchs_list': dico_environments[j]['devices_list'],
                                                  'username_list': "[]"}



    # print(env_select.get().upper())
    # nom_env = env_select.get().upper()
    # print(switchs_list)
    # config[nom_env] = {'switchs_list': switchs_list}
    fichier = open("environments_save.ini", "w")
    config.write(fichier)
    fichier.close()
    # test


# CHARGER LISTE DEVICES  ##################################################################

def load_device_list():
    global switchs_list
    global list_import

    if switchs_list != "":

        msg_box_continue = tk.messagebox.askquestion("Attention! ",
                                                     "Voulez vous AJOUTER les devices à la liste existante ?",
                                                     icon='warning')
        if msg_box_continue == 'yes':
            pass
        else:
            msg_box_continue = tk.messagebox.askquestion("Attention! ",
                                                         "Voulez vous REMPLACER les devices de la liste existante ?",
                                                         icon='warning')
            if msg_box_continue == 'yes':
                switchs_list = []
            else:
                print("ajout annulé, car AJOUT ou REMPLACEMENT REFUSé par le USER")
                return
    else:
        switchs_list = []

    path_to_cli_file = open_file()
    cli_read_file = open(path_to_cli_file, "r", encoding="utf8")
    lines = cli_read_file.readlines()

    for line in lines:
        switchs_list.append(line.strip())

    switchs_list = sorted(list(set(switchs_list)))
    print(switchs_list)

    cli_read_file.close()

    # On ajoute au DICO sous l'env actuel
    for j in range(0, len(dico_environments)):
        if dico_environments[j]['name'] == env_select.get():
            dico_environments[j]['devices_list'] = switchs_list

    print("     " + str(dico_environments))
    list_import = "1"
    env_display_devices("3")


def about():
    pass


# Fonctions de CALLBACK ###############################################################################################
def callback_change_env(*args):
    global user_name
    global password
    global username_list
    global secret

    print("callback_change_env : la VARIABLE env_select a été modifiée :" + env_select.get())
    # On reset le username/pwd
    user_name = ""
    password = ""
    secret = ""

    # si c'est un nouvel environnement créé on ne fait rien non plus

    # sinon on recharge la liste de switchs pour l'environnement existant
    # on recharge donc la liste de devices
    env_display_devices("1")
    username_list = []
    user_select.set("")
    username_display_menu(True)


def callback_new_env(*args):
    print("callback_new_env : la VARIABLE new_env a été modifiée :" + new_env.get())
    # si c'est un nouvel environnement créé on ne fait rien non plus
    # sinon on recharge la liste de switchs pour l'environnement existant
    # on recharge donc la liste de devices
    env_display_devices("2")


def callback_new_user(*args):
    print("callback_new_user : la VARIABLE new_user a été modifiée :" + new_user.get())
    username_display_menu("NEW")


def callback_change_user(*args):
    global user_name
    global password
    print("callback_change_user : la VARIABLE user_select a été modifiée :" + user_select.get())
    # on va donc affecter la variable username avec cette valeur et reset du password
    user_name = user_select.get()
    password = ""


def callback_radio_for_script_change(*args):
    print("callback_radio_for_script_change : la VARIABLE radiobutton_for_script a été modifiée :" +
          radiobutton_for_script.get())

##################################################################################
#  debut de la main frame ###########################
##################################################################################


root = Tk()
root.title("MON SCRIPT GRAPHIQUE !!")
# Déclaration des variables de la fenetre principale
env_select = tk.StringVar(root)
env_select.set("")
new_env = tk.StringVar(root)
new_env.set("")
user_select = tk.StringVar(root)
user_select.set("")
new_user = tk.StringVar(root)
new_user.set("")
radiobutton_for_script = tk.StringVar(root)
radiobutton_for_script.set("50")
switchs_list = []

# creation de la fenetre graphique
# create all of the main containers
top_frame = Frame(root, bg='lavender', width=450, height=50, pady=3)
center = Frame(root, bg='gray2', width=50, height=40, padx=3, pady=3)
btm_frame = Frame(root, bg='lavender', width=450, height=60, pady=3)
# layout all of the main containers
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
# affichage des 3 Frames
top_frame.grid(row=0, sticky="ew")
center.grid(row=1, sticky="nsew")
btm_frame.grid(row=4, sticky="ew")

# create the widgets for the top frame
model_label = Label(top_frame, text='Environnement')
left_label = Label(top_frame, text='Username:')
length_label = Label(top_frame, text='NOT USED:')
entry_W = Entry(top_frame, background="orange")
entry_L = Entry(top_frame, background="orange")
# bouton simple
button_add_env = Button(top_frame, text='Ajouter', command=add_environment)
button_add_username = Button(top_frame, text='Ajouter', command=add_username)

# layout the widgets in the top frame
model_label.grid(row=0, column=0)
left_label.grid(row=1, column=0)
# length_label.grid(row=1, column=2)
# entry_W.grid(row=1, column=1)
# entry_L.grid(row=1, column=3)
button_add_env.grid(row=0, column=2)
button_add_username.grid(row=1, column=2)

ctr_left = Frame(center, bg='orange', width=100, height=190, padx=3, pady=3)
ctr_mid = Frame(center, bg='lavender', width=250, height=190, padx=3, pady=3)
ctr_right = Frame(center, bg='lavender', width=100, height=190, padx=3, pady=3)

ctr_left.grid(row=0, column=0, sticky="ns")
ctr_mid.grid(row=0, column=1, sticky="nsew")
ctr_right.grid(row=0, column=2, sticky="ns")

# Affichage dans la fenetre Centre Gauche:
nom_label_script = Label(ctr_left, text='Actions sur tous les devices :')
nom_label_script.grid(row=0, column=0)


# fonction de depart pour determiner l'environnement à charger
start_env()

# Les boutons de menu
menu = Menu(root)
root.config(menu=menu)
filemenu = Menu(menu, tearoff=0)
scriptmenu = Menu(menu, tearoff=0)
helpmenu = Menu(menu, tearoff=0)
menu.add_cascade(label="File", menu=filemenu)
menu.add_cascade(label="Extensions", menu=scriptmenu)
menu.add_cascade(label="Help", menu=helpmenu)

# filemenu.add_command(label="New", command=NewFile)
filemenu.add_command(label="Open...", command=open_file)
filemenu.add_command(label="Save Env...", command=save_env)
filemenu.add_command(label="Importer une liste de devices dans l'environnement", command=load_device_list)
filemenu.add_separator()
filemenu.add_command(label="Paramètres")
filemenu.add_command(label="Exit", command=root.quit)

# 2e menu avec les scripts
#scriptmenu.add_command(label="Traitement par lots via fichier de commandes CLI")
# scriptmenu.add_command(label="Show interface status for a VLAN")
# scriptmenu.add_command(label="Configure vlan on TRUNK")
# scriptmenu.add_command(label="Configure vlan ACCESS")
# scriptmenu.add_command(label="Write memory")
# scriptmenu.add_command(label="Exécuter un fichier de commandes CLI")
# scriptmenu.add_command(label="802.1X sur port acces")

helpmenu.add_command(label="About...", command=about)

# tracking des modifications des variables en temps reel
env_select.trace("w", callback_change_env)
user_select.trace("w", callback_change_user)
new_env.trace("w", callback_new_env)
new_user.trace("w", callback_new_user)
radiobutton_for_script.trace("w", callback_radio_for_script_change)

# affiche la fenetre principale
mainloop()