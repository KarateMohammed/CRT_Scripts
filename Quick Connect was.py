
# $language = "python"
# $interface = "1.0"
# Version 3.0


import time, os, sys

def main():


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


    # Get the value of the "Auth prompts in Window" option, this is used to prevent the failure authentication prompt messages in order to detect the failure
    Auth_Prompt_Option_Check = int (tabConfig.GetOption("Auth Prompts in Window"))
    SSH2_Authentication_V2_Check = str (tabConfig.GetOption ("SSH2 Authentications V2"))
    
    # If "Auth_Prompt_Option_Check" and "SSH2_Authentication_V2_Check" are disabled, and then enable them
    if (not (Auth_Prompt_Option_Check == 1 and  SSH2_Authentication_V2_Check == "password,publickey,keyboard-interactive,gssapi")):
        tabConfig.SetOption("Auth Prompts in Window", True)
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


 

    Device_name = crt.Dialog.Prompt("Please Enter The Device Name:", "Quick Connect Menu", "")
    
    # Change String to Upper Case
    Device_name=Device_name.upper()

    if Device_name  == '':
        return

    # SSH2 to IPRNS04
    tab = crt.Session.ConnectInTab('/ssh2 /L '+ username +  ' /PASSWORD ' + password + ' 10.57.164.20', False)

    read_screen = tab.Screen.ReadString(["Please verify that the username and password are correct.", "TACACS"])
        
    while "Password authentication failed." in read_screen:
        
        
        tab.Session.Disconnect()
        # Fallback to manual method to enter the NUAR username and password
        username = crt.Dialog.Prompt("Please Enter Your Nuar Username", "Username", "")

        if username == '':
            return

        password = crt.Dialog.Prompt("Please Enter Your Nuar Password", "Password", "", True)

        if password == '':
            return
        
        tab.Session.ConnectInTab('/ssh2 /L '+ username +  ' /PASSWORD ' + password + ' 10.57.164.20', False)
        read_screen = tab.Screen.ReadString(["Please verify that the username and password are correct.", "TACACS"])

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


    # Ask the user to restart secureCRT in order to take effect.
    if Credential_file_updated == "True":
        crt.Dialog.MessageBox('''#############################################\n
The credential file was updated with the new username and password.\n\nYou must restart SecureCRT for the credential file change to take effect.\n
#############################################''')


    # Set the tab name
    tab.Caption = Device_name


    file_name = Device_name + ".txt"
    
    # Loop to Check Existence of file if exist then creat another one incremneted by next integer
    x=1
    while os.path.exists(os.path.join(os.path.join(Log_path, CurrentDay), file_name)) :        
        file_name = Device_name+"_" +str(x)+ ".txt"
        x=x+1
        
    tab.Session.LogFileName = os.path.join(os.path.join(Log_path, CurrentDay), file_name)
    tab.Session.Log(False)
    tab.Screen.SendSpecial("MENU_LOG_SESSION")


               
    try:
      
        # Accessing a device 
        tab.Screen.WaitForString("Nmstel password: ")
        tab.Screen.Send( password + '\n')
        tab.Screen.WaitForString("#")
        tab.Screen.Send("l" + ' ' + Device_name  + '\n')
      
    except ScriptError:
        # SSH2 to IPWAS04
        tab = crt.Session.ConnectInTab('/ssh2 /L '+ username +  ' /PASSWORD ' + password + ' 10.57.164.20', False)


        #Tab Synchronization
        tab.Activate()
        tab.Screen.Synchronous = True

        # Set the tab name
        tab.Caption = Device_name

        file_name = Device_name + ".txt"
 
    # Loop to Check Existence of file if exist then creat another one incremneted by next integer 
        x=1
        while os.path.exists(os.path.join(os.path.join(Log_path, CurrentDay), file_name)) :
            file_name = Device_name+"_" +str(x)+ ".txt"
            x=x+1

        tab.Session.LogFileName = os.path.join(os.path.join(Log_path, CurrentDay), file_name)
        tab.Session.Log(False)
        tab.Screen.SendSpecial("MENU_LOG_SESSION")

        # Accessing a device 
        tab.Screen.WaitForString("Nmstel password: ")
        tab.Screen.Send( password + '\n')
        tab.Screen.WaitForString("#")
        tab.Screen.Send("l" + ' ' + Device_name  + '\n')

main ()



                 ################################################################################################################
                 #              Copyright @2018 Ahmed Shehata, VPO, Orange Business Services.                                   #
                 #     If you have any issues or inquires with the script, thanks to email me at ahmad.shehata@orange.com       #
                 ################################################################################################################
