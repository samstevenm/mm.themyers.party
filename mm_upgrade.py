import sys
import logging
import time

logging.basicConfig( format = '%(asctime)s  %(levelname)-10s %(processName)s  %(name)s %(message)s', datefmt =  "%Y-%m-%d-%H-%M-%S", filename = time.strftime("mmupgrade-%Y-%m-%d.log"), level=logging.DEBUG)

logging.debug("debug")
logging.info("info")
logging.warning("warning")
logging.error("error")
logging.critical("critical")

def wait_for_enter():
    raw_input("Press Enter to continue.")

class ExplainStep(object):
    def run(self, context):
        print('''
**Upgrading Mattermost**
This is a "Do-nothing script" [0] to aid in the process of upgrading Mattermost.
You can and should also read the guide [1](RTFM). Maybe this tool is useful.

[0] https://blog.danslimmon.com/2019/07/15/do-nothing-scripting-the-key-to-gradual-automation/?utm_source=pocket_mylist
[1] https://docs.mattermost.com/administration/upgrade.html
        ''')
        wait_for_enter()

class SSHtoMMServerStep(object):
    def run(self, context):
        print('''
**SSH into Mattermost Server (Ubuntu)**
        ''')
        print("Run:")
        print("   ssh <USER>@<SERVER>")
        wait_for_enter()

class PrepUbuntuStep(object):
    def run(self, context):
        print('''
**Completely update Mattermost Server (Ubuntu)**
        ''')
        print("Run:")
        print("   sudo apt update && sudo apt upgrade -y")
        wait_for_enter()
        print('''
**Remove unnecessary stuff from Mattermost Server (Ubuntu)**
        ''')
        print("Run:")
        print("   sudo apt-get autoremove --purge -y")
        wait_for_enter()
        print('''
**Free up space by vacuuming the logs (Ubuntu)**
        ''')
        print("Run:")
        print("   sudo journalctl --vacuum-time=3d")
        wait_for_enter()
        print('''
**Make a note of disk usage (Ubuntu)**
        ''')
        print("Run:")
        print("   df -h")
        context["remainingspace"] = raw_input("Enter the remaining space %: ")
        print("**Remaining space is %{0}**".format(context["remainingspace"]))
        logging.info("Remaining space is %{0}".format(context["remainingspace"]))
        wait_for_enter()

class DumpMMSQLStep(object):
    def run(self, context):
        print('''
Dump the mattermost database to a SQL file
        ''')
        print("Run:")
        print('''
mysqldump -u root -p mattermost > mattermost_backup$(date +"%Y-%m-%d_%H-%M-%S").sql
''')
        wait_for_enter()

class WhereisMMStep(object):
    def run(self, context):
        print('''
**Find Mattermost binary**
If you do not know where Mattermost Server is installed,
use the `whereis mattermost` command. The output should be similar to
/opt/mattermost or /bin/mattermost.
The install directory is everything before the first occurrence
of the string /mattermost for example /opt or /bin.
        ''')
        print("Run:")
        print("   whereis mattermost")
        context["mmlocation"] = raw_input("Enter the location (i.e. /opt): ")
        print("**Mattermost is installed at {0}**".format(context["mmlocation"]))
        logging.info("Mattermost is installed at {0}".format(context["mmlocation"]))
        wait_for_enter()

class ChangeDirStep(object):
    def run(self, context):
        print('''
In a terminal window on the server that hosts Mattermost,
change to your home directory. Delete any files and directories that might still
 exist from a previous download.
        ''')
        print("Run:")
        print("   cd /tmp")
        wait_for_enter()

class ConfirmDirEmpty(object):
    def run(self, context):
        print('''
Confirm no other Mattermost zip folders exist in
your /tmp directory. If other versions or files exist,
delete or rename them.
              ''')
        print("Run:")
        print("   ls -- mattermost*.gz")
        wait_for_enter()

class DownloadLatestVersionStep(object):
    dir_url = "https://mattermost.com/download/"
    def run(self, context):
        print("Go to {0}".format(self.dir_url))
        context["downloadlink"] = raw_input("Paste the download link and press enter: ")
        print("Run:")
        print("   wget {0}".format(context["downloadlink"]))
        wait_for_enter()

class ExtractMMServerFilesStep(object):
    def run(self, context):
        print("Run:")
        print('''
   tar -xf mattermost*.gz --transform='s,^[^/]\+,\0-upgrade,'
              ''')
        wait_for_enter()

class StopMMServerStep(object):
    def run(self, context):
        print("Run:")
        print("   sudo systemctl stop mattermost")
        wait_for_enter()

class BackupMMServerStep(object):
    def run(self, context):
        print("Run:")
        print("   cd {0}".format(context["mmlocation"]))
        print("   sudo cp -ra mattermost/ mattermost-back-$(date +'%F-%H-%M')/")
        wait_for_enter()

class CleanOldMMVersionStep(object):
    def run(self, context):
        print('''
**Remove all files except data and custom directories from within the current mattermost directory.**
''')
        print("Run:")
        print('''
   sudo find mattermost/ mattermost/client/ -mindepth 1 -maxdepth 1 \! \( -type d \( -path mattermost/client -o -path mattermost/client/plugins -o -path mattermost/config -o -path mattermost/logs -o -path mattermost/plugins -o -path mattermost/data \) -prune \) | sort | xargs echo rm -r)
    ''')
        wait_for_enter()

class ChangeOwnerNewMMStep(object):
    def run(self, context):
        print('''
**Change ownership of the new files before copying them.**
''')
        print("Run:")
        print('''
   sudo chown -hR mattermost:mattermost /tmp/mattermost-upgrade/
    ''')
        wait_for_enter()

class CopyCleanStep(object):
    def run(self, context):
        print('''
**Copy the new files to your install directory and remove the temporary files.**
''')
        print("Run:")
        print('''
   sudo cp -an /tmp/mattermost-upgrade/. mattermost/
   sudo rm -r /tmp/mattermost-upgrade/
   sudo rm -i /tmp/mattermost*.gz
''')
        wait_for_enter()

class NetCapStep(object):
    def run(self, context):
        print('''
**Port Binding**
If you want to use port 80 to serve your server, or if you have TLS set up on
your Mattermost server, you must activate the CAP_NET_BIND_SERVICE capability to
 allow the new Mattermost binary to bind to low ports.
 ''')
        print("Run:")
        print('''
   cd {0}/mattermost
   sudo setcap cap_net_bind_service=+ep ./bin/mattermost
'''.format(context["mmlocation"]))
        wait_for_enter()

class StartMMServerStep(object):
    def run(self, context):
        print("Run:")
        print("   sudo systemctl start mattermost")
        wait_for_enter()

if __name__ == "__main__":
    #Upgrader is the person running the script
    context = {"upgrader": sys.argv[1]}
    print("Upgrader is {0}".format(context["upgrader"]))
    logging.info("Upgrader is {0}".format(context["upgrader"]))
    procedure = [
        ExplainStep(),
        SSHtoMMServerStep(),
        PrepUbuntuStep(),
        DumpMMSQLStep(),
        WhereisMMStep(),
        ChangeDirStep(),
        ConfirmDirEmpty(),
        DownloadLatestVersionStep(),
        ExtractMMServerFilesStep(),
        StopMMServerStep(),
        BackupMMServerStep(),
        CleanOldMMVersionStep(),
        ChangeOwnerNewMMStep(),
        CopyCleanStep(),
        NetCapStep(),
        StartMMServerStep(),
    ]
    for step in procedure:
        step.run(context)
        logging.info("Class {0} completed".format(step.__class__.__name__))
    print("Done! Hopefully, you've upgraded Mattermost without breaking it.")
