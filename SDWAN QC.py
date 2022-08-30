
# $language = "python"
# $interface = "1.0"
# Version 1.2


import time, os, sys,csv,re

def main():

    vManage = "10.217.0.28"
    vEdge_Local_Password1 = "obs4pmisdwan"
    vEdge_Local_Password2 = "admin"
    Local_Username1 = "admin"

    global Device_name
    global Device
    global regex_IP
    global vEdge_IP

    # Logging folder path, if you want to change the folder path. Example, Log_path = "Your path".. Log_path = "D:\\Work\\Logs"..
    #Note: It's recommeded to double each backslash in the path to be \\ instead of \

    CurrentDay = time.strftime("%d-%m-%Y")
    Log_path = os.path.expanduser('~\\Desktop\\LOGS')

    CurrentDay = time.strftime("%d-%m-%Y")

    if not os.path.exists(Log_path):
            os.makedirs(os.path.join(Log_path, CurrentDay))

    # Tab Synchronization
    tab = crt.GetScriptTab()
    tab.Activate()
    tab.Screen.Synchronous = True
        

    # open the session tab config file
    tabConfig = tab.Session.Config
    
    # Get the values of the default settings
    Auth_Prompt_Option_Check = int (tabConfig.GetOption("Auth Prompts in Window"))
    SSH2_Authentication_V2_Check = str (tabConfig.GetOption ("SSH2 Authentications V2"))
                           

    # Check the values of the default settings, and set them if they are not exist
    if (not (Auth_Prompt_Option_Check == 1)):
        tabConfig.SetOption("Auth Prompts in Window", True)
        tabConfig.Save()
    
    if (not (SSH2_Authentication_V2_Check == "password,publickey,keyboard-interactive,gssapi")):
        tabConfig.SetOption("SSH2 Authentications V2", "password,publickey,keyboard-interactive,gssapi")
        tabConfig.Save() 


    # Intial Value
    Credential_file_updated =""

    try:
            
        import Credential

        # User Credential
        username = Credential.user ["Username"]
        password = Credential.user ["Password"]
        
    except ImportError:
        
        # prompt message for the user that credential file is not exist
        crt.Dialog.MessageBox('''#############################################
\nThe Credential file is not exist in the SecureCRT folder.\n\nPlease click Okay to proceed to enter Username and password
manually, and then the credential file will be created in SecureCRT folder('''+ sys.path[0]+''')\n
\nIt will be automatically used the next time you use the script without the need of entering it manually once again.\n
#############################################''')

        # Fallback to manual method to enter the NUAR username and password
        username = crt.Dialog.Prompt("Please Enter Your Nuar Username", "Username", "")

        if username == '':
            return

        password = crt.Dialog.Prompt("Please Enter Your Nuar Password", "Password", "", True)

        if password == '':
            return

        #Create the credentail file and saved in the SecureCRT folder...
        data = '''user = {
    "Username": "''' +username+'''",  #Write your username between " " 
    "Password": "''' +password+ '''"  #Write your password between " "
        }'''

        credential_file_path = os.path.join(sys.path[0], "Credential.py")
        f = open(credential_file_path, 'w')
        f.write(data)
        f.close()


 

    Device = crt.Dialog.Prompt("Please Enter The vEdge Hostname or System-ip:", "Quick Connect Menu", "")


    if Device  == '':
        return

    # SSH2 to IPRNS04
    tab = crt.Session.ConnectInTab('/ssh2 /L '+ username +  ' /PASSWORD ' + password + ' ' +vManage, False)

        
    login_check = tab.Screen.WaitForStrings(["Please verify that the username and password are correct.", "#"])

    
        
    while login_check == 1:
        
        tab.Session.Disconnect()
        # Fallback to manual method to enter the NUAR username and password
        username = crt.Dialog.Prompt("Please Enter Your Nuar Username", "Username", "")

        if username == '':
            return

        password = crt.Dialog.Prompt("Please Enter Your Nuar Password", "Password", "", True)

        if password == '':
            return

        # Update the credentail file with the correct username and password...
        data = '''user = {
    "Username": "''' +username+'''",  #Write your username between " " 
    "Password": "''' +password+ '''"  #Write your password between " "
        }'''

        credential_file_path = os.path.join(sys.path[0], "Credential.py")
        f = open(credential_file_path, 'w')
        f.write(data)
        f.close()

        # Set the credential file to True if it was recently updated.
        Credential_file_updated = "True"

        tab = crt.Session.ConnectInTab('/ssh2 /L '+ username +  ' /PASSWORD ' + password + ' ' +vManage, False)
        login_check = tab.Screen.WaitForStrings(["Please verify that the username and password are correct.", "#"])
   

    # Ask the user to restart secureCRT in order to take effect.
    if Credential_file_updated == "True":
        crt.Dialog.MessageBox('''#############################################\n
The credential file has been updated with the new username and password.\n\nYou must restart SecureCRT for the credential file change to take effect.\n
#############################################''')
    

    regex_IP = "^((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))*\s{0,}$"
    if re.match (regex_IP, Device.strip()):
        # Accessing a device
        vEdge_IP = Device.strip()
        tab.Screen.Send("vshell\n")

        #Check reachability
        tab.Screen.WaitForString(":~$")
        tab.Screen.Send("ping " + vEdge_IP +" -c 2 -W 1\n")
        ping_output = tab.Screen.ReadString(":~$")
        ping_output_check = re.findall("(\d)(?:\sreceived)", ping_output)
        if ping_output_check[0] == '0':
            crt.Dialog.MessageBox ("vEdge is unreacahble from vManage")
            return
        
        tab.Screen.Send("\n") 
        tab.Screen.WaitForString(":~$")
        tab.Screen.Send("ssh " + username +"@" + vEdge_IP  + '\n')
        SSH_Check_Result = tab.Screen.WaitForStrings(["assword:", "Are you sure you want to continue connecting (yes/no)?","Host key verification failed."])
       
        if SSH_Check_Result == 1:
            tab.Screen.Send(password + "\n")
        elif SSH_Check_Result == 2:
            tab.Screen.Send("yes\n")
            tab.Screen.WaitForString("assword:")
            tab.Screen.Send(password + "\n")
        elif SSH_Check_Result == 3:
            tab.Screen.Send('\n')
            tab.Screen.WaitForString(":~$")
            tab.Screen.Send("ssh-keygen -R " + vEdge_IP + "\n")
            tab.Screen.WaitForString(":~$")
            tab.Screen.Send("rm /home/basic/.ssh/known_hosts.old\n")
            tab.Screen.WaitForString(":~$")
            tab.Screen.Send("ssh -o 'StrictHostKeyChecking no' " + username +"@" + vEdge_IP  + '\n')
            tab.Screen.WaitForString("assword:")
            tab.Screen.Send(password + "\n")

        # Incase of Tacacs not working, vEdge_Hostname_Check and try local passwords
        read_screen = tab.Screen.ReadString(["word", "please try again.", "connected from","authorization failed"])

        if ("Permission denied" in read_screen) or ("ass" in read_screen) or ("User Authorization failure" in read_screen):
            # Send special character (CTRL+C)   
            tab.Screen.Send(chr(3))
            tab.Screen.WaitForString(":~$")
            tab.Screen.Send("ssh " + Local_Username1 +"@"  + vEdge_IP  + '\n')
            tab.Screen.WaitForString("assword:")
            tab.Screen.Send(vEdge_Local_Password1 + "\n")
            result = tab.Screen.WaitForStrings(["Permission denied", "assword", "#"])
            if result == 1 or result == 2:
                tab.Screen.Send(vEdge_Local_Password2 + "\n")

       # To get the name of the device
        for x in range (1,3):
            tab.Screen.Send('\n')
            tab.Screen.WaitForString("#")
            

        tab.Screen.Send('\n')
        prompt = tab.Screen.ReadString("#")
        Device_name = prompt.strip()
       
        Device_name=Device_name.upper()
        
        # Set the tab name
        tab.Caption = Device_name
        
        # Check the hostname if it is exist on the csv file or not
        vEdge_name_check()
        
        if vEdge_Hostname_Check == "Notfound":

            # Map the vEdge hostname to IP and saved in the CSV file
            with open(file_path, mode='ab') as vedges_mapping_file:
                SDWAN_Vedges = csv.writer(vedges_mapping_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                SDWAN_Vedges.writerow([Device_name.strip().upper(), vEdge_IP.strip()])




    # if the user used a device name
    else:
        Device_name = Device.strip() 
        # Check if it's in the mapping CSV file or not
        vEdge_IP = vEdge_name_check()
        # if the vEdge name is exist
        if vEdge_Hostname_Check == "Found":
            # Accessing a device 
            tab.Screen.Send("vshell\n")
            
            #Check reachability
            tab.Screen.WaitForString(":~$")
            tab.Screen.Send("ping " + vEdge_IP +" -c 2 -W 1\n")
            ping_output = tab.Screen.ReadString(":~$")
            ping_output_check = re.findall("(\d)(?:\sreceived)", ping_output)
            if ping_output_check[0] == '0':
                crt.Dialog.MessageBox ("vEdge is unreacahble from vManage")
                return
            
            tab.Screen.Send("\n") 
            tab.Screen.WaitForString(":~$")
            tab.Screen.Send("ssh " + username +"@" + vEdge_IP  + '\n')

            SSH_Check_Result = tab.Screen.WaitForStrings(["assword:", "Are you sure you want to continue connecting (yes/no)?","Host key verification failed."])
        
            if SSH_Check_Result == 1:
                tab.Screen.Send(password + "\n")
            elif SSH_Check_Result == 2:
                tab.Screen.Send("yes\n")
                tab.Screen.WaitForString("assword:")
                tab.Screen.Send(password + "\n")
            elif SSH_Check_Result == 3:
                tab.Screen.Send('\n')
                tab.Screen.WaitForString(":~$")
                tab.Screen.Send("ssh-keygen -R " + vEdge_IP + "\n")
                tab.Screen.WaitForString(":~$")
                tab.Screen.Send("rm /home/basic/.ssh/known_hosts.old\n")
                tab.Screen.WaitForString(":~$")
                tab.Screen.Send("ssh -o 'StrictHostKeyChecking no' " + username +"@" + vEdge_IP  + '\n')
                tab.Screen.WaitForString("assword:")
                tab.Screen.Send(password + "\n")
                
            # Incase of Tacacs not working, vEdge_Hostname_Check and try local passwords
            read_screen = tab.Screen.ReadString(["word:",", please try again.", "connected from","authorization failed"])

            if ("Permission denied" in read_screen) or ("ass" in read_screen) or ("User Authorization failure" in read_screen):
                # Send special character (CTRL+C)
                tab.Screen.Send(chr(3))
                tab.Screen.WaitForString(":~$")
                tab.Screen.Send("ssh " + Local_Username1 +"@"  + vEdge_IP  + '\n')
                tab.Screen.WaitForString("assword:")
                tab.Screen.Send(vEdge_Local_Password1 + "\n")
                result = tab.Screen.WaitForStrings(["Permission denied", "assword", "connected from"])
                if result == 1 or result == 2:
                    tab.Screen.Send(vEdge_Local_Password2 + "\n")
    


            # To get the name of the device
            for x in range (1,3):
                tab.Screen.Send('\n')
                tab.Screen.WaitForString("#")

            tab.Screen.Send('\n')
            prompt = tab.Screen.ReadString("#")
            Device_name = prompt.strip()

            Device=Device.upper()
            
            # Set the tab name
            tab.Caption = Device.strip()



        # If the user used a device name but the name is not exist in the mapping file  
        else:

            vEdge_IP = crt.Dialog.Prompt(Device.strip() + ''' Not Found!\n\nPlease Enter the system-ip of the vEdge:
\nNote: The vEdge hostname will be saved upon successful login''', "Quick Connect Menu", "")

            if vEdge_IP == '':
                return

            tab.Screen.Send("vshell\n")

            #Check reachability
            tab.Screen.WaitForString(":~$")
            tab.Screen.Send("ping " + vEdge_IP +" -c 2 -W 1\n")
            ping_output = tab.Screen.ReadString(":~$")
            ping_output_check = re.findall("(\d)(?:\sreceived)", ping_output)
            if ping_output_check[0] == '0':
                crt.Dialog.MessageBox ("vEdge is unreacahble from vManage")
                return
            
            tab.Screen.Send("\n") 
            tab.Screen.WaitForString(":~$")
            tab.Screen.Send("ssh " + username +"@" + vEdge_IP  + '\n')

            SSH_Check_Result = tab.Screen.WaitForStrings(["assword:", "Are you sure you want to continue connecting (yes/no)?","Host key verification failed."])
        
            if SSH_Check_Result == 1:
                tab.Screen.Send(password + "\n")
            elif SSH_Check_Result == 2:
                tab.Screen.Send("yes\n")
                tab.Screen.WaitForString("assword:")
                tab.Screen.Send(password + "\n")
            elif SSH_Check_Result == 3:
                tab.Screen.Send('\n')
                tab.Screen.WaitForString(":~$")
                tab.Screen.Send("ssh-keygen -R " + vEdge_IP + "\n")
                tab.Screen.WaitForString(":~$")
                tab.Screen.Send("rm /home/basic/.ssh/known_hosts.old\n")
                tab.Screen.WaitForString(":~$")
                tab.Screen.Send("ssh -o 'StrictHostKeyChecking no' " + username +"@" + vEdge_IP  + '\n')
                tab.Screen.WaitForString("assword:")
                tab.Screen.Send(password + "\n")

            # Incase of Tacacs not working, vEdge_Hostname_Check and try local passwords
            read_screen = tab.Screen.ReadString(["word:", "please try again.", "connected from","authorization failed"])

            if ("Permission denied" in read_screen) or ("ass" in read_screen) or ("User Authorization failure" in read_screen):
                # Send special character (CTRL+C)
                tab.Screen.Send(chr(3))
                tab.Screen.WaitForString(":~$")
                tab.Screen.Send("ssh " + Local_Username1 +"@"  + vEdge_IP  + '\n')
                tab.Screen.WaitForString("assword:")
                tab.Screen.Send(vEdge_Local_Password1 + "\n")
                result = tab.Screen.WaitForStrings(["Permission denied","assword", "#"])
               
                if result == 1 or result ==2:
                    tab.Screen.Send(vEdge_Local_Password2 + "\n")
            
            # To get the name of the device
            for x in range (1,3):
                tab.Screen.Send('\n')
                tab.Screen.WaitForString("#")

            tab.Screen.Send('\n')
            prompt = tab.Screen.ReadString("#")
            Device_name = prompt.strip()

            Device_name=Device_name.upper()
            
            # Set the tab name
            tab.Caption = Device_name
           
            vEdge_name_check()
           
            if vEdge_Hostname_Check == "Notfound":
            # Map the vEdge hostname to IP and saved in the CSV file
                with open(file_path, mode='ab') as vedges_mapping_file:
                    SDWAN_Vedges = csv.writer(vedges_mapping_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    SDWAN_Vedges.writerow([Device_name.strip().upper(), vEdge_IP.strip()])


   
    # Change String to Upper Case
    Device_name=Device_name.upper()

    # log the session and saved it in the logs folder
    file_name = Device_name + ".txt"
    
    # Loop to Check Existence of file if exist then creat another one incremneted by next integer
    x=1
    while os.path.exists(os.path.join(os.path.join(Log_path, CurrentDay), file_name)) :        
        file_name = Device_name+"_" +str(x)+ ".txt"
        x=x+1

    # log the session and saved it in the logs folder
    tab.Session.LogFileName = os.path.join(os.path.join(Log_path, CurrentDay), file_name)
    tab.Session.Log(False)
    tab.Screen.SendSpecial("MENU_LOG_SESSION")

        
                    
                                          

def vEdge_name_check():
    
    global vEdge_Hostname_Check
    global file_path
    global row
    
    #intial values
    row_count = 0
    Sys_IPs = []
    # vEdge_IP = "intial"
    
    abspath = os.path.abspath(__file__)
    dir_name = os.path.dirname(abspath)
    file_path = os.path.join(dir_name, 'SDWAN_Vedges_Mapping.csv')

    # Check if the file is exist, if not create a SDWAN Vedges mapping file to map the name to the System IP address of vedges
    if not os.path.exists(file_path):
        with open(file_path, mode='ab') as vedges_mapping_file:
            SDWAN_Vedges = csv.writer(vedges_mapping_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            SDWAN_Vedges.writerow(['Hostname', 'System IP'])


    #read the file and vEdge_Hostname_Check if the device is exist or not.
    with open (file_path) as vedges_mapping_file:
        SDWAN_Vedges = csv.reader(vedges_mapping_file, delimiter=',',quotechar='"')
        
        #loop through the csv list
        for row in SDWAN_Vedges:
            row_count = row_count + 1
            Sys_IPs.append(row[1])
            #if current rows 2nd value is equal to input, print that row
            if  not (row[0].upper() == Device_name.strip().upper()):
                vEdge_Hostname_Check = "Notfound"
                vEdge_IP = "intial"
                continue
            else:
                vEdge_Hostname_Check ="Found"
                break
            

    if vEdge_Hostname_Check == "Found":                    
       if not re.match (regex_IP, Device.strip().upper()):
           vEdge_IP = Sys_IPs[row_count-1]
        

    return vEdge_IP.strip()

   
main ()



                 ################################################################################################################
                 #              Copyright @2020 Ahmed Shehata, Senior Technical Enginner, Orange Business Services.             #
                 #     If you have any issues or inquires with the script, thanks to email me at ahmad.shehata@orange.com       #
                 ################################################################################################################
