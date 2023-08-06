from cloudmesh.common.Shell import Shell

class Rivanna:

    def __init__(self):
        pass

    def login(self, gpu=None, memory=None):
        """
        ssh on rivanna by executing an interactive job command

        :param gpu:
        :type gpu:
        :param memory:
        :type memory:
        :return:
        :rtype:
        """
        raise NotImplementedError
        print("implement me")
        # ssh on rivanna by executing an interactive job command
        # please remember we also have cloudmesh-vpn to access vpn from commandline
        job_id = "TBD" # get this
        return job_id


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