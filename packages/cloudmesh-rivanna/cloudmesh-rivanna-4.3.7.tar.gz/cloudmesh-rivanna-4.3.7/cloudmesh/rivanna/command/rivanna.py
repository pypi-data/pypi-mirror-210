from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.rivanna.rivanna import Rivanna
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from pprint import pprint
from cloudmesh.common.debug import VERBOSE
from cloudmesh.shell.command import map_parameters
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.variables import Variables
from cloudmesh.common.util import banner

class RivannaCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_rivanna(self, args, arguments):
        """
        ::

          Usage:
                rivanna storage info DIRECTORY [--info]
                rivanna login gpu=GPU [--info]
                rivanna tutorial [KEYWORD]

          This command simplifys access to rivanna.

          Arguments:
              DIRECTORY  a location of a directory on rivanna

          Options:
              -f      specify the file

          Description:

            rivanna storage info DIRECTORY [--info]
                A command that can be executed remotely and obtains information about the storage associated
                with a directory on rivanna

            rivanna login gpu=GPU [--info]
                A command that logs into from your current computer into an interactive node on rivanna
                with a given GPU. Values for GPU are

                a100 or a100-80 -- uses a A100 with 80GB
                a100 or a100-40 -- uses a A100 with 80GB
                a100-localscratch  -- uses a A100 with 80GB and access to localscratch

                others to be added from rivannas hardware description

            rivanna tutorial singularity
                shows the rivanna singularity information on infomall.org

            rivanna tutorial hpc
                shows the general rivanna hpc information on infomall.org

            rivanna tutorial pod
                shows the general rivanna pod information on infomall.org

            rivanna tutorial globue
                shows the general rivanna globus information on infomall.org

            rivanna tutorial rclone
                shows the general rivanna rclone information on infomall.org

          Installation:

            pip install cloudmesh-rivana
            cms help

        """


        # arguments.FILE = arguments['--file'] or None

        # switch debug on

        variables = Variables()
        variables["debug"] = True

        map_parameters(arguments, "gpu")

        # VERBOSE(arguments)

        rivanna = Rivanna()

        if arguments.storage:

            Console.error("not implemented")

        elif arguments.login:

            content = rivanna.login(gpu=arguments.GPU)
            print(content)
            Console.error("not implemented")

        elif arguments.tutorial:

            keyword = arguments.KEYWORD

            if keyword in ["pod"]:
                rivanna.browser("https://infomall.org/uva/docs/tutorial/rivanna-superpod/")

            elif keyword in ["rclone"]:
                rivanna.browser("https://infomall.org/uva/docs/tutorial/rclone/")

            elif keyword in ["globus"]:
                rivanna.browser("https://infomall.org/uva/docs/tutorial/globus/")

            elif keyword in ["singularity"]:
                rivanna.browser("https://infomall.org/uva/docs/tutorial/singularity/")

            elif keyword in ["training"]:
                rivanna.browser("https://infomall.org/uva/docs/tutorial/cybertraining/")

            elif keyword in ["hpc", "system"]:
                rivanna.browser("https://infomall.org/uva/docs/tutorial/rivanna/")



            else:
                rivanna.browser("https://infomall.org/uva/docs/tutorial/")

        return ""
