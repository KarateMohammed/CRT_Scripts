# $language = "python"
# $interface = "1.0"

import os, sys, re

def main():
                
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
        
        # If the current tab is not connected
        if tab.Session.Connected == False:

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


    # Ask the user to type the device name or device IP address
    device = crt.Dialog.Prompt("Please Enter The Device Name or Device IP Address:", "Device Name", "")

    #If the device field is empty or pressed cancel, stop the script
    if device == '':
        return
    
    while True:
        
        # Ask the user to Manual or pre-defined standard SNMP parameters 
        mode_check = crt.Dialog.Prompt('''Please Select mode:\n\n 1) Automatic mode\n
 2) Manual mode\n\n 3) Help''', "Mode Selection", "")

       # checks
        if  mode_check.strip() == '':
            return
        
        elif not re.match ("^[1-3]$", mode_check.strip()):
            crt.Dialog.MessageBox ('\nInvalid input!\n\nPlease enter a number from 1 to 3\n')

        elif re.match ("^3$", mode_check.strip()):
            crt.Dialog.MessageBox('''#############################################\n
1) Manual mode means that you will need to enter the SNMPv3 parameters manually.\n
SNMPv3 format:
snmp-server user <User_Name> <Group_Name> v3 auth <Auth_Protocol> <Auth_Password> priv <Privacy_Protocol> 128 <Privacy_Password> access <ACL>\n
2) Automatic mode means that the script will use the standard pre-defined SNMPv3 parameters\n
#############################################
 ''')
            
        elif re.match ("^[1-2]$", mode_check.strip()):
            break
 

    while True:
        
       #Ask the user to enter the configuration filename that is saved on the TFTP server
        conf_file = crt.Dialog.Prompt('''###################### IMPORTANT NOTES ######################\n
The filename must matches the created file, also add the file extension ".txt", if it's included.
\nThis config file should be uploaded on IPWAS04 IPtoolbox at the directory (/tftpboot/outbox/)
by WINSCP, SecureCRT FX, or Linux CLI commands.\n\nType help for how to create file by Linux CLI commands.
\n#########################################################
\nPlease Enter Filename:\n\nEg: SNMPv3_config_test.txt''', "Configuration Filename", "")
        
        # If it's empty or pressed cancel, stop the script
        if conf_file == '':
            return
        if re.match("^help$", conf_file.strip(),re.IGNORECASE):
            crt.Dialog.MessageBox('''############################################\n
First of all, you have to connect to IPWAS04 and follow the below steps:

ashehata@ipwas04 # cd /tftpboot/outbox/
ashehata@ipwas04 # cat > conf_SNMP_test.txt
conf t
do show run | redirect tftp://57.7.40.193/showruntest.txt
end
^C (Use CTRL+C when you done to close the file)

############################################

Verification commands:

ashehata@ipwas04 # find conf_SNMP_test.txt
conf_SNMP_test.txt
ashehata@ipwas04 # more conf_SNMP_test.txt
conf t
do show run | redirect tftp://57.7.40.193/showruntest.txt
end
ashehata@ipwas04 #

############################################
Notes:

1 ) To use show commands, you have to do it from configuration mode by using "do" keyword.\n
2 ) To send the output to IPtoolbox use "redirect" keyword "do <show_command> | redirect tftp://57.7.40.193/<file_name>"\n
3 ) The uploaded file could be found on IPWAS IPtoolbox on "cd /tftpboot/inbox/"
''')
        else:
            break





    # Manual mode               
    if mode_check.strip() == '2':
        
        user = crt.Dialog.Prompt("Please enter username of the SNMP community", "Communtiy Username", "")
        if  user == '':
            return

        # Enter the Security level
        while True:
            security_level = crt.Dialog.Prompt('''Please enter The secuirty level:\n\n1) noAuthNoPriv
    \n2) authNoPriv \n\n3) authPriv\n\n4) Help''', "Security Level", "")
            if  security_level == '':
                return
            elif not re.match("^[1-4]$", security_level.strip()):
                crt.Dialog.MessageBox("Invalid input!\n\nPlease enter a number from 1 to 4.")
            elif re.match("^4$", security_level.strip()):
                crt.Dialog.MessageBox('''#############################################\n
noAuthNoPriv: the configured SNMPv3 doesn't use neither authentication nor privacy.
\nauthNoPriv: the configured SNMPv3 only uses authentication.\n\nauthPriv: the configured SNMPv3 uses both authentication and privacy.\n
#############################################''')
            if re.match("^[1-3]$", security_level.strip()):
                if security_level.strip() == '1':
                    security_level = "noAuthNoPriv"
                elif security_level.strip() == '2':
                    security_level = "authNoPriv"
                elif security_level.strip() == '3':
                    security_level = "authPriv"     
                break

            
        
        if security_level == "authNoPriv"  or security_level == "authPriv":
            
            # Enter the authentication protocol
            auth_prot = crt.Dialog.Prompt('''Please enter the authentication protocol:\n\n1) md5\n\n2) sha''', "Authentication Protocol", "")
            
            if auth_prot == '':
               return
            elif auth_prot == '1':
                auth_prot = "md5"
            elif auth_prot == '2':
                auth_prot = "sha"

             # Enter the authentication password
            auth_pass = crt.Dialog.Prompt('''Please enter the authentication password:''', "Authentication Password", "")

            if auth_pass == '':
                return
            

            
        if security_level == "authPriv":
            # Enter the privacy protocol
            privacy_prot = crt.Dialog.Prompt('''Please enter the privacy protocol:\n\n1) 3des\n\n2) aes\n\n3) des''', "Privacy Protocol", "")
            if privacy_prot == '':
               return
            elif privacy_prot == '1':
                privacy_prot = "3des"
            elif privacy_prot == '2':
                privacy_prot = "aes"
            elif privacy_prot == '3':
                privacy_prot = "des"

            # Enter the privacy password
            privacy_pass = crt.Dialog.Prompt('''Please enter the privacy password:''', "Privacy Password", "")

            if privacy_pass == '':
             return




    if tab.Session.Connected == False:
        # SSH2 to IPRNS04
        tab.Session.ConnectInTab('/ssh2 /L '+ username +  ' /PASSWORD ' + password + ' 10.57.129.100', False)

        
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
            
            tab.Session.ConnectInTab('/ssh2 /L '+ username +  ' /PASSWORD ' + password + ' 10.57.129.100', False)
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
            
        # Tab's Name
        tab.Caption = "SNMP Script"
         
        # Accessing a device 
        tab.Screen.WaitForString("Nmstel password: ")
        tab.Screen.Send( password + '\n')

    else:
        tab.Screen.Send('\n')

        
    # wait for string "#", and then send a newline   
    tab.Screen.WaitForString("#")
    tab.Screen.Send('\n')
    
    # Get prompt which the curosr is standing on.
    prompt = GetPrompt()

    # Check if the user is connected to a device rather than IPRNS/IPWAS, prompt a warning message, and then exist the script. 
    if not re.match ("\w*@\w*", prompt):
        crt.Dialog.MessageBox("You are connected to a device!\n\n Please connect to IPRNS or IPWAS, and then run the script again.")
        return
    
    # Check if the user entered a device name or an IP address, if the user entered a device name, nslookup to get the IP address.
    if not re.match ("(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", device.strip()):
        # Wait for the prompt, send nslookup <devicename>, and capture the output to get the IP address. 
        tab.Screen.WaitForString(prompt)
        tab.Screen.Send( "nslookup " + device.strip() + ' | grep "Address: "' + '\n')
        # Capture the output of nslookup
        nslookup_output = tab.Screen.ReadString(prompt)

        # Fetch the IP address from the output.
        IP = re.search (r'(?:Address:\s)((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))', nslookup_output)
        try:
            device_IP = IP.group(1)
            
        # Display an error if the device name is not resolvable by the DNS server and exist the script.   
        except AttributeError:
            crt.Dialog.MessageBox("Device Name hasn't been resolved by DNS Server, you could try to use the IP address instead.")
            return
    # If user entered the IP address.      
    else:
        device_IP = device
        

    # Send a newline and wait for prompt and then send "stty -echo" to stop echoing the sending commands.
    tab.Screen.Send('\n')
    tab.Screen.WaitForString(prompt)
    tab.Screen.Send( "stty -echo" + '\n')
    tab.Screen.WaitForString("stty -echo")

    # Automatic mode
    if mode_check.strip() == '1':
        
        # send snmpset commands for the first standard community
        auth_pass = "2e0f1165b9@f44dacef021A8b625"
        privacy_pass = "2e0f1165@2nb9f44dacef021A8b625"
        snmp_commands = snmp_commands_template("authPriv","ORCHSNMPV3RW","sha",auth_pass,"AES",privacy_pass,device_IP,conf_file,"57.7.40.193")
    
        for x in snmp_commands:
            tab.Screen.WaitForString(prompt)
            tab.Screen.Send( x + '\n')
            command_output = tab.Screen.ReadString(prompt)

            tab.Screen.Send('\n')
            
            
            # Check if there is an error, display the error message and exist the loop.
            if ("Unknown user name" in command_output) or ("Authentication failure" in command_output) or ("Timeout: No Response" in command_output) or ("Unsupported security level" in command_output) or ("authorizationError" in command_output):
                SNMP_status = "Failed"
                break

                
            if ("Timeout" in command_output):
                crt.Dialog.MessageBox(command_output[:-2] + "\n\nThe device seems unreachable from controlnet")
                tab.Screen.Send( "stty echo" + '\n\n')
                return

            SNMP_status= "Success"
        

        #in case, the first SNMP community failed, Try the second SNMP community
        if SNMP_status == "Failed":
            auth_pass = "e47fd8679e@87f8101eb31F21f1"
            privacy_pass = "e47fd867@2n9e87f8101eb31f21F1c"
            snmp_commands = snmp_commands_template("authPriv","WASACSNMPV3RW","sha",auth_pass,"AES",privacy_pass,device_IP,conf_file,"57.7.40.193")
            
            for y in snmp_commands:  
                tab.Screen.WaitForString(prompt)
                tab.Screen.Send( y + '\n\n')
                command_output = tab.Screen.ReadString(prompt)
                
                if ("Unknown user name" in command_output) or ("Authentication failure" in command_output) or ("Timeout: No Response" in command_output) or ("Unsupported security level" in command_output) or ("authorizationError" in command_output):
                    crt.Dialog.MessageBox(command_output[:-2])
                    tab.Screen.Send( "stty echo" + '\n\n')
                    return

    # Manual mode             
    if mode_check.strip() == '2':
        
        # Frist case noAuthNoPriv
        if security_level == "noAuthNoPriv":
            snmp_commands = snmp_commands_template(security_level,user," "," "," "," ",device_IP,conf_file,"57.7.40.193")    

         # Second case "authNoPriv"
        elif security_level == "authNoPriv":
            snmp_commands = snmp_commands_template(security_level,user,auth_prot,auth_pass,"","",device_IP,conf_file,"57.7.40.193")
            
        # Third case "authPriv"
        elif security_level == "authPriv":
           snmp_commands = snmp_commands_template(security_level,user,auth_prot,auth_pass,privacy_prot,privacy_pass,device_IP,conf_file,"57.7.40.193")

        
        for x in snmp_commands:
            tab.Screen.WaitForString(prompt)
            tab.Screen.Send( x + '\n')
            command_output = tab.Screen.ReadString(prompt)

            tab.Screen.Send('\n')
            
            
            # Check if there is an error, display the error message and exist the loop.
            if ("Unknown user name" in command_output) or ("Authentication failure" in command_output) or ("Timeout" in command_output) or ("Unsupported security level" in command_output) or ("authorizationError" in command_output):
                    crt.Dialog.MessageBox(command_output[:-2] + "\n\nThe device seems unreachable from controlnet")
                    tab.Screen.Send( "stty echo" + '\n\n')
                    return
        
            
    tab.Screen.Send( "stty echo" + '\n\n\n##############Done##############\n')


# To get prompt that is used for WaitForString function.
def GetPrompt():
    prompt = crt.Screen.Get(crt.Screen.CurrentRow, 1, crt.Screen.CurrentRow, 80)
    prompt = prompt.strip()
    return prompt

def snmp_commands_template(security_level, user, auth_prot, auth_pass,privacy_prot,privacy_pass,device_IP,conf_filename,TFTP_server):
    snmp_commands = []
    oids = ["1.3.6.1.4.1.9.9.96.1.1.1.1.14.777 i 6", "1.3.6.1.4.1.9.9.96.1.1.1.1.2.777  i 1", "1.3.6.1.4.1.9.9.96.1.1.1.1.3.777  i 1",
"1.3.6.1.4.1.9.9.96.1.1.1.1.4.777  i 4", "1.3.6.1.4.1.9.9.96.1.1.1.1.5.777  a "+TFTP_server, "1.3.6.1.4.1.9.9.96.1.1.1.1.6.777  s outbox/" + conf_filename, 
"1.3.6.1.4.1.9.9.96.1.1.1.1.14.777 i 1"]

    for oid in oids:
        
        if security_level == "noAuthNoPriv":         
            command ="snmpset -v3 -l "+security_level+" -u "+user+" "+device_IP+" "+ oid
            snmp_commands.append(command)
            
        elif security_level == "authNoPriv":
            command ="snmpset -v3 -l "+security_level+" -u "+user+" -a "+auth_prot+" -A "+auth_pass+" "+device_IP+" "+ oid
            snmp_commands.append(command)
            
        elif security_level == "authPriv":
            command ="snmpset -v3 -l "+security_level+" -u "+user+" -a "+auth_prot+" -A "+auth_pass+" -x "+ privacy_prot+" -X "+privacy_pass+" "+device_IP+" "+ oid
            snmp_commands.append(command)
            
    return snmp_commands

main()    



                 ################################################################################################################
                 #              Copyright @2020 Ahmed Shehata, VPO, Orange Business Services.                                   #
                 #     If you have any issues or inquires with the script, thanks to email me at ahmad.shehata@orange.com       #
                 ################################################################################################################
