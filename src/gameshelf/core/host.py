import os
import subprocess

class HostRunner:
    def sandboxed(self):
        return "FLATPAK_ID" in os.environ

    def buildCommand(self, argv):
        if self.sandboxed():
            command = ["flatpak-spawn", "--host"] + argv
        else:
            command = argv
        return command

    def run(self, argv):
        command = self.buildCommand(argv)
        subprocess.Popen(command)  

    def output(self, argv):
        command = self.buildCommand(argv)
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
