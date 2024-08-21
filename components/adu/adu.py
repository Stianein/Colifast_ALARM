##### MODULE NAME: ADU208 #####
##### Author: Stian Ingebrigtsen

import threading
import queue
import logging
import ctypes
from concurrent.futures import Future
from ctypes import wintypes
from components.adu.ontrak import aduhid
import settings

# Load the Windows kernel32.dll library
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

# Define necessary types and functions
DWORD = wintypes.DWORD
LPWSTR = wintypes.LPWSTR

# Define FormatMessage function signature
FormatMessageW = kernel32.FormatMessageW
FormatMessageW.argtypes = [
    DWORD,    # dwFlags
    ctypes.c_void_p,    # lpSource
    DWORD,    # dwMessageId
    DWORD,    # dwLanguageId
    LPWSTR,    # lpBuffer
    DWORD,    # nSize
    ctypes.c_void_p,    # Arguments
]
FormatMessageW.restype = DWORD

# Constants for FormatMessage flags
FORMAT_MESSAGE_FROM_SYSTEM = 0x00001000
FORMAT_MESSAGE_IGNORE_INSERTS = 0x00000200

# Logging errors to logfile
log = logging.getLogger("method_logger")

# Singleton class for limiting access to the adu device to a single entry point
class ADUCommunication:
    _instance = None
    _lock = threading.Lock()
    # SINGLETON function
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ADUCommunication, cls).__new__(cls, *args, **kwargs)
                    cls._instance._initialize_connection()
                    cls._instance._initialize_queue()
        return cls._instance
    
    # Queue initialization handled in seperate thread
    def _initialize_queue(self):
        self.queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._process_queue)
        self.worker_thread.daemon = True  # Makes the thread exit when the main thread exits
        self.worker_thread.start()
    
    # Outside this class call function to reinitialize the connection 
    # - loading adu in case of a lost connection
    def initialize(self):
        self._initialize_connection()
        return self.initialized
    
    # Initialization of device
    def _initialize_connection(self):
        PRODUCT_ID = 208
        global device_handle
        device_handle = aduhid.open_device_by_product_id(PRODUCT_ID, 100)

        if device_handle is None:
            log.error('Error opening the ADU. Ensure that it is connected with the green light')
            self.initialized = False
        else:
            log.info("Device found and connected")
            self.initialized = True

    # Function for handling the queue
    def _process_queue(self):
        while True:
            print("Waiting for task...")
            item = self.queue.get()
            # print(f"Dequeued item: {item}")
            if item is None:
                break
            if isinstance(item, tuple) and len(item) == 2:
                task, future = item
                try:
                    result = task()
                    future.set_result(result)
                    print(f"Task completed with result: {result}")
                except Exception as e:
                    future.set_exception(e)
                    print(f"Task failed with exception: {e}")
            else:
                log.info(f"ADU Queue process, unexpected item structure: {item}")

    # Function for handling queue of commands comming in for the device from different threads
    def _enqueue_command(self, function, *args, **kwargs):
        # print(f"Enqueuing command: {function.__name__}, args: {args}, kwargs: {kwargs}")
        future = Future()
        self.queue.put((lambda: function(*args, **kwargs), future))
        return future
    
    # Validate connection - this is only controlled by a variable, self.initialized, 
    # which has nothing to do with the actual connection, so I am a bit unsure of the usfullness of this.
    def _validate_connection(self):
        if not self.initialized:
            self._initialize_connection()
        return self.initialized

    # Functions for reading the adu device
    def read(self, command):
        future = self._enqueue_command(self._read, command)
        return future.result()
    def _read(self, command):
        with self._lock:
            if not self._validate_connection():
                return "Could not validate connection, please load ADU"
            if settings.getstopSignal():
                raise SystemExit("Stopping program adu read")
            stat = aduhid.write_device(device_handle, command, 300)
            print(f"Command: {command}, Stat: {stat} ")
            log.info(f"Command: {command}, Stat: {stat} ")
            if stat != 0:
                result, value = aduhid.read_device(device_handle, 300)
                print(f"Command: {command}, Result: {result} , Value: {value}")
                log.info(f"Command: {command}, Result: {result} , Value: {value}")
                if result != 0: 
                    return int(value)
                else:
                    error_message = self._get_last_error_message()
                    log.error(f"Unsuccessful read, command {command} " + error_message)
                    return error_message
            else:
                error_message = self._get_last_error_message()
                log.error(f"Unsuccessful read, command {command} " + error_message)
                return error_message

    # Functions for writing to the adu device
    def write(self, command):
        future = self._enqueue_command(self._write, command)
        return future.result()
    def _write(self, command):
        with self._lock:
            if not self._validate_connection():
                return "Could not validate connection, please load ADU"
            if settings.getstopSignal():
                raise SystemExit("Stopping program adu write")
            stat_write = aduhid.write_device(device_handle, command, 300)
            if stat_write != 0:
                return "Write successful"
            else:
                error_message = self._get_last_error_message()
                log.error("Unsuccessful write, port A0 " + error_message)
                return error_message

    # Function for turning on a relay
    def on(self, relay):
        if relay < 0 or relay > 7:
            log.error(f"The channel, {relay} is not a valid relay")
            return "Invalid relay channel"
        command = 'SK{}'.format(relay)
        result = self.write(command)
        return result

    # Function for turning off a relay
    def off(self, relay):
        if relay < 0 or relay > 7:
            log.error(f"The channel, {relay} is not a valid relay")
            return "Invalid relay channel"
        command = 'RK{}'.format(relay)
        result = self.write(command)
        return result

    # Reset all ports
    def reset(self):
        self.write('MK0')

    # Function for fetching error from device
    def _get_last_error_message(self):
        try:
            error_code = kernel32.GetLastError()
            buf_size = 256
            buf = ctypes.create_unicode_buffer(buf_size)
            flags = FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS
            FormatMessageW(flags, None, error_code, 0, buf, buf_size, None)
            return buf.value.strip()
        except Exception as e:
            log.error(f"Error fetching last error message: {e}")
            return "Unknown error"
        
    # Function for closing down connection     
    def close(self):
        aduhid.close_device(device_handle)
        self.queue.put(None)
        self.worker_thread.join()

# Automatically create a singleton instance
adu = ADUCommunication()
