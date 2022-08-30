import os,sys, subprocess


def main():

    # Intial Value
    Credential_file_updated =""

    try:
            
        import Credential
        script_path = os.path.abspath( __file__ )

        crt.Dialog.MessageBox("script_path:\n{}".format(script_path))

        directory = os.getcwd()
        crt.Dialog.MessageBox("directory:\n{}".format(directory))

        # User Credential
        username = Credential.user ["Username"]
        password = Credential.user ["Password"]
        crt.Dialog.MessageBox("username:\t{}\npassword:\t{}".format(username,password))
        
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
        crt.Dialog.MessageBox("credential_file_path:\n{}".format(credential_file_path))

        f = open(credential_file_path, 'w')
        f.write(data)
        f.close()
    

    outputRNS = subprocess.Popen("cmd /k curl -k -u " + username + ":" + password +" https://authrns.rns.apps.ocn.infra.ftgroup/login.php?timeout=36000", stdin = subprocess.PIPE,stdout=subprocess.PIPE, shell=True)
    outputauthiad2 = subprocess.Popen("cmd /k curl -k -u " + username + ":" + password + " https://authiad2.apps.ocn.infra.ftgroup/login.php?timeout=36000", stdin = subprocess.PIPE,stdout=subprocess.PIPE, shell=True)
    outputauthiad3 = subprocess.Popen("cmd /k curl -k -u " + username + ":" + password + " https://authiad3.apps.ocn.infra.ftgroup/login.php?timeout=36000" , stdin = subprocess.PIPE,stdout=subprocess.PIPE, shell=True)
    outputauthuro1 = subprocess.Popen("cmd /k curl -k -u " + username + ":" + password + " https://authuro1.apps.ocn.infra.ftgroup/login.php?timeout=36000", stdin = subprocess.PIPE,stdout=subprocess.PIPE, shell=True)

    
    if  "Failed"  in str (outputRNS.communicate()) and  "Failed" in str (outputauthiad2.communicate()):

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

        outputRNS = subprocess.Popen("cmd /k curl -k -u " + username + ":" + password +" https://authrns.rns.apps.ocn.infra.ftgroup/login.php?timeout=36000", stdin = subprocess.PIPE,stdout=subprocess.PIPE, shell=True)
        outputauthiad2 = subprocess.Popen("cmd /k curl -k -u " + username + ":" + password + " https://authiad2.apps.ocn.infra.ftgroup/login.php?timeout=36000", stdin = subprocess.PIPE,stdout=subprocess.PIPE, shell=True)
        outputauthiad3 = subprocess.Popen("cmd /k curl -k -u " + username + ":" + password + " https://authiad3.apps.ocn.infra.ftgroup/login.php?timeout=36000" , stdin = subprocess.PIPE,stdout=subprocess.PIPE, shell=True)
        outputauthuro1 = subprocess.Popen("cmd /k curl -k -u " + username + ":" + password + " https://authuro1.apps.ocn.infra.ftgroup/login.php?timeout=36000", stdin = subprocess.PIPE,stdout=subprocess.PIPE, shell=True)

        if "Authorization Failed" in str (outputRNS.communicate()) and  "Authorization Failed" in str (outputauthiad2.communicate()):
            crt.Dialog.MessageBox("Authorization Failed!")

        else:
            crt.Dialog.MessageBox("Authenticated!\n\nNote: Wait few seconds before connecting to OCN servers.")
            # crt.Dialog.MessageBox("{}\t{}\nAuthenticated!\n\nNote: Wait few seconds before connecting to OCN servers.".format(username,password))

    else:
        crt.Dialog.MessageBox("Authenticated!\n\nNote: Wait few seconds before connecting to OCN servers.")
        # crt.Dialog.MessageBox("{}\t{}\nAuthenticated!\n\nNote: Wait few seconds before connecting to OCN servers.".format(username,password))

main ()


                 ################################################################################################################
                 #              Copyright @2021 Ahmed Shehata, Senior Technical Enginner, Orange Business Services.             #
                 #     If you have any issues or inquires with the script, thanks to email me at ahmad.shehata@orange.com       #
                 ################################################################################################################