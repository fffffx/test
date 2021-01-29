import threading
import random
import time
import os
import tempfile
thread_to_connect_to_devices = threading.Thread(target= print, args =['User', 'pwd','ip', 'command'], kwargs={'sep': ' ---- '})

#thread_to_connect_to_devices.start()
# renvoi : User----pwd----ip----command

list_of_thread = []
#exemple:
liste_switchs = ['sw1', 'sw2', 'sw3', 'sw4']

user= "admin"
password= "cisco"
commande = "sh ip int brief"
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
    one_thread = threading.Thread(target=connect_ssh, args =( user , password , switch , commande ))
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

