from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
import os

class Rivanna:

    def __init__(self):
        pass

    def login(self,
              host="rivanna",
              cores="1",
              allocation="bii_dsc_community",
              gres="gpu:v100:1",
              time="30:00",
              partition="gpu",
              constraint=None,
              reservation=None,
              account=None,
              debug=False

    ):
        """
        ssh on rivanna by executing an interactive job command

        :param gpu:
        :type gpu:
        :param memory:
        :type memory:
        :return:
        :rtype:
        """
        if account is None:
            account = ""
        else:
            account = f"--account={account}"
        if partition is None:
            partition = ""
        else:
            partition = f"--partition={partition}"
        if constraint is None:
            constraint = ""
        else:
            constraint = f"--constraint={constraint}"
        if reservation is None:
            reservation = ""
        else:
            reservation = f"--reservation={reservation}"
        command = f'ssh -tt {host} "/opt/rci/bin/ijob {reservation} {constraint} {account} -c {cores} {partition} --gres={gres} --time={time}"'

        Console.msg(command)
        if not debug:
            os.system(command)
        return ""


    def cancel(self, job_id):
        """
        cancels the job with the given id

        :param job_id:
        :type job_id:
        :return:
        :rtype:
        """
        raise NotImplementedError

    def storage(self, directory=None):
        """
        get info about the directory

        :param directory:
        :type directory:
        :return:
        :rtype:
        """
        raise NotImplementedError

    def edit(self, filename=None, editor="emacs"):
        """
        start the commandline editor of choice on the file on rivanna in the current terminal

        :param filename:
        :type filename:
        :return:
        :rtype:
        """

    def browser(self, url):
        Shell.browser(filename=url)