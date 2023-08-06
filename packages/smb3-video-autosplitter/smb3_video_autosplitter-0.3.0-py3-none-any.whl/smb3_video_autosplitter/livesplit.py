import win32file, win32pipe


class LivesplitConnectFailedException(Exception):
    pass


class LivesplitReadFailedException(Exception):
    pass


class Livesplit:
    def __init__(self):
        self.initialize_client()

    def send(self, command_name: str):
        win32file.WriteFile(self.handle, command_name.encode() + b"\r\n")

    def recv(self, auto_decode=True, buf_size=65536):
        result, data = win32file.ReadFile(self.handle, buf_size)
        if result == 0:
            return data.decode("utf-8") if auto_decode else data
        else:
            raise LivesplitReadFailedException(f"Failed with result code {result}")

    def initialize_client(self):
        try:
            self.handle = win32file.CreateFile(
                r"\\.\pipe\LiveSplit",
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0,
                None,
                win32file.OPEN_EXISTING,
                win32file.FILE_ATTRIBUTE_NORMAL,
                None,
            )
        except:
            raise LivesplitConnectFailedException()
        res = win32pipe.SetNamedPipeHandleState(
            self.handle, win32pipe.PIPE_READMODE_BYTE, None, None
        )
        if res == 0:
            print(f"SetNamedPipeHandleState return code: {res}")

    def terminate(self):
        self.handle.close()
