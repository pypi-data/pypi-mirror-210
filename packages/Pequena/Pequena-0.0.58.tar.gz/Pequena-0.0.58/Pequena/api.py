
import webview
import os
import subprocess
import platform
import sys
import socket
import tempfile


class PequenaApi:
    def getWindowInfo():
        """
        :classmethod:
        Get information about the main window.

        :return: A dictionary containing the window's x, y coordinates, width, and height.
        :rtype: dict
        """
        return {"x": webview.windows[0].x, "y": webview.windows[0].y, "width": webview.windows[0].width, "height": webview.windows[0].height}

    def getScreenInfo():
        """
        :classmethod:
        Get information about the screen.

        :return: A dictionary containing the screen's width and height.
        :rtype: dict
        """
        return {"width": webview.screens[0].width, "height": webview.screens[0].height}

    def minimizeWindow():
        """
        Minimize the main window.
        """
        return webview.windows[0].minimize()

    def unminimizeWindow():
        """
        Restore the main window from a minimized state.
        """
        return webview.windows[0].restore()

    def hideWindow():
        """
        Hide the main window.
        """
        return webview.windows[0].hide()

    def unhideWindow():
        """
        Show the main window if it is hidden.
        """
        return webview.windows[0].show()

    def toggleFullscreen():
        """
        Toggle the main window between fullscreen and normal mode.
        """
        return webview.windows[0].toggle_fullscreen()

    def moveWindow(_x, _y):
        """
        Move the main window to the specified coordinates.

        :param _x: The new x-coordinate of the window.
        :type _x: int
        :param _y: The new y-coordinate of the window.
        :type _y: int
        """
        return webview.windows[0].move(_x, _y)

    def resizeWindow(_width, _height):
        """
        Resize the main window to the specified dimensions.

        :param _width: The new width of the window.
        :type _width: int
        :param _height: The new height of the window.
        :type _height: int
        """
        return webview.windows[0].resize(_width, _height)

    def setWindowName(_name):
        """
        Set the title of the main window.

        :param _name: The new title for the window.
        :type _name: str
        """
        return webview.windows[0].set_title(_name)


class NodeApi:
    class fs:
        def readFile(path: str, encoding: str = 'utf-8') -> str:
            """
            Reads the content of a file.

            :param path: The path to the file.
            :type path: str
            :param encoding: (Optional) The encoding of the file. Defaults to 'utf-8'.
            :type encoding: str, optional
            :return: The content of the file.
            :rtype: str
            """
            with open(path, 'r', encoding=encoding) as file:
                return file.read()

        def writeFile(path: str, content: str) -> None:
            """
            Writes content to a file.

            :param path: The path to the file.
            :type path: str
            :param content: The content to write.
            :type content: str
            :return: None
            :rtype: None
            """
            with open(path, 'w') as file:
                file.write(content)

        def mkdir(path: str) -> None:
            """
            Creates a directory.

            :param path: The path of the directory to create.
            :type path: str
            :return: None
            :rtype: None
            """
            os.mkdir(path)

        def readdir(path: str) -> list[str]:
            """
            Reads the contents of a directory.

            :param path: The path to the directory.
            :type path: str
            :return: A list of file names in the directory.
            :rtype: list[str]
            """
            return os.listdir(path)

        def pathExists(path: str) -> bool:
            """
            Checks if a path exists.

            :param path: The path to check.
            :type path: str
            :return: True if the path exists, False otherwise.
            :rtype: bool
            """
            return os.path.exists(path)

        def isfile(path: str) -> bool:
            """
            Checks if a path is a file.

            :param path: The path to check.
            :type path: str
            :return: True if the path is a file, False otherwise.
            :rtype: bool
            """
            return os.path.isfile(path)

        def isdir(path: str) -> bool:
            """
            Checks if a path is a directory.

            :param path: The path to check.
            :type path: str
            :return: True if the path is a directory, False otherwise.
            :rtype: bool
            """
            return os.path.isdir(path)

    class path:
        def basename(path: str) -> str:
            """
            Returns the last portion of a path.

            :param path: The path.
            :type path: str
            :return: The last portion of the path.
            :rtype: str
            """
            return os.path.basename(path)

        def dirname(path: str) -> str:
            """
            Returns the directory name of a path.

            :param path: The path.
            :type path: str
            :return: The directory name.
            :rtype: str
            """
            return os.path.dirname(path)

        def extname(path: str) -> str:
            """
            Returns the extension of a path.

            :param path: The path.
            :type path: str
            :return: The extension of the path.
            :rtype: str
            """
            return os.path.splitext(path)[1]

        def isAbsolute(path: str) -> bool:
            """
            Determines if a path is an absolute path.

            :param path: The path.
            :type path: str
            :return: True if the path is absolute, False otherwise.
            :rtype: bool
            """
            return os.path.isabs(path)

        def join(*paths: str) -> str:
            """
            Joins multiple path segments into a single path.

            :param paths: The path segments.
            :type paths: Tuple[str]
            :return: The joined path.
            :rtype: str
            """
            return os.path.join(*paths)

        def resolve(*paths: str) -> str:
            """
            Resolves the absolute path from multiple path segments.

            :param paths: The path segments.
            :type paths: Tuple[str]
            :return: The resolved absolute path.
            :rtype: str
            """
            return os.path.abspath(os.path.join(*paths))

    class child_process:

        def exec(command: str, options: dict = {}) -> bool:
            """
            Executes a command and waits for it to complete.

            :param command: The command to execute.
            :type command: str
            :param options: Additional options, defaults to {}.
            :type options: dict, optional
            :return: A subprocess.CompletedProcess object representing the completed process.
            :rtype: subprocess.CompletedProcess
            """
            subprocess.run(command, **options, shell=True, capture_output=True)
            return True

        def execSync(command: str, options: dict = {}) -> bool:
            """
            Executes a command synchronously and returns the result.

            :param command: The command to execute.
            :type command: str
            :param options: Additional options, defaults to {}.
            :type options: dict, optional
            :return: A subprocess.CompletedProcess object representing the completed process.
            :rtype: subprocess.CompletedProcess
            """
            subprocess.run(command, **options, shell=True,
                           capture_output=True, check=True)
            return True

    class os:

        def arch() -> str:
            """
            Returns the operating system CPU architecture.

            :return: The CPU architecture.
            :rtype: str
            """
            return platform.machine()

        def constants() -> dict:
            """
            Returns an object containing the operating system's constants for process signals, error codes, etc.

            :return: An object containing the OS constants.
            :rtype: dict
            """
            return os.__dict__

        def cpus() -> list[dict]:
            """
            Returns an array containing information about the computer's CPUs.

            :return: An array containing CPU information.
            :rtype: list[dict]
            """
            cpus = []
            with open('/proc/cpuinfo', 'r') as f:
                lines = f.read().strip().split('\n\n')
                for info in lines:
                    cpu_info = {}
                    for line in info.split('\n'):
                        key, value = line.split(':')
                        cpu_info[key.strip()] = value.strip()
                    cpus.append(cpu_info)
            return cpus

        def endianness() -> str:
            """
            Returns the endianness of the CPU.

            :return: The endianness of the CPU ("LE" for little-endian or "BE" for big-endian).
            :rtype: str
            """
            if sys.byteorder == "little":
                return "LE"
            else:
                return "BE"

        def EOL() -> str:
            """
            Returns the end-of-line marker for the current operating system.

            :return: The end-of-line marker.
            :rtype: str
            """
            return os.linesep

        def freemem() -> int:
            """
            Returns the number of free memory of the system, in bytes.

            :return: The free memory in bytes.
            :rtype: int
            """
            return os.sysconf(os.sysconf_names['SC_AVPHYS_PAGES']) * os.sysconf(os.sysconf_names['SC_PAGESIZE'])

        def hostname() -> str:
            """
            Returns the hostname of the operating system.

            :return: The hostname.
            :rtype: str
            """
            return socket.gethostname()

        def loadavg() -> list[float]:
            """
            Returns an array containing the load averages (1, 5, and 15 minutes) of the system.

            :return: An array containing the load averages.
            :rtype: list[float]
            """
            with open('/proc/loadavg', 'r') as f:
                loadavg = f.read().strip().split()[:3]
                return [float(avg) for avg in loadavg]

        def networkInterfaces() -> dict:
            """
            Returns the network interfaces that have a network address.

            :return: A dictionary of network interfaces.
            :rtype: dict
            """
            interfaces = {}
            for interface, addresses in socket.if_nameindex():
                ifaddresses = socket.getaddrinfo(interface, None)
                interface_addresses = []
                for addr in ifaddresses:
                    if addr[0] == socket.AF_INET or addr[0] == socket.AF_INET6:
                        interface_addresses.append({
                            "address": addr[4][0],
                            "netmask": addr[4][1],
                            "family": socket.AddressFamily(addr[0]).name.lower(),
                            "mac": None,
                        })
                if interface_addresses:
                    interfaces[interface] = interface_addresses
            return interfaces

        def platform() -> str:
            """
            Returns information about the operating system's platform.

            :return: The platform information.
            :rtype: str
            """
            return platform.platform()

        def release() -> str:
            """
            Returns information about the operating system's release.

            :return: The release information.
            :rtype: str
            """
            return platform.release()

        def tmpdir() -> str:
            """
            Returns the operating system's default directory for temporary files.

            :return: The temporary directory path.
            :rtype: str
            """
            return tempfile.gettempdir()

        def totalmem() -> int:
            """
            Returns the number of total memory of the system, in bytes.

            :return: The total memory in bytes.
            :rtype: int
            """
            return os.sysconf(os.sysconf_names['SC_PHYS_PAGES']) * os.sysconf(os.sysconf_names['SC_PAGESIZE'])

        def type() -> str:
            """
            Returns the name of the operating system.

            :return: The operating system name.
            :rtype: str
            """
            return platform.system()

        def uptime() -> float:
            """
            Returns the uptime of the operating system, in seconds.

            :return: The system uptime in seconds.
            :rtype: float
            """
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.read().split()[0])
                return uptime_seconds

        def userInfo() -> dict:
            """
            Returns information about the current user.

            :return: A dictionary with user information.
            :rtype: dict
            """
            user_info = {}
            user_info["username"] = os.getlogin()
            user_info["uid"] = os.getuid()
            user_info["gid"] = os.getgid()
            user_info["homedir"] = os.path.expanduser("~")
            return user_info
