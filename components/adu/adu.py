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
    _lock = threading.RLock()
    # SINGLETON function
    def __new__(cls, *args, **kwargs):
        log.debug("\t\tAttempting to create or retrieve singleton instance")
        if not cls._instance:
            log.debug("\t\tNo instance found, attempting to create one")
            with cls._lock:
                if not cls._instance:
                    log.debug("\t\tCreating new instance of ADUCommunication")
                    cls._instance = super(ADUCommunication, cls).__new__(cls, *args, **kwargs)
                    cls._instance._initialize_connection()
                    cls._instance._initialize_queue()
        log.debug("\t\tReturning singleton instance of ADUCommunication")
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
        log.debug("\t\tInitializing connection to ADU")
        with self._lock:
            log.debug("\t\tLock acquired for initializing connection")
            PRODUCT_ID = 208
            global device_handle
            device_handle = aduhid.open_device_by_product_id(PRODUCT_ID, 100)

            if device_handle is None:
                log.error('Error opening the ADU. Ensure that it is connected with the green light')
                self.initialized = False
            else:
                log.debug("Device found and connected")
                self.initialized = True
            log.debug(f"\t\tConnection {'initialized' if self.initialized else 'failed to initialize'}")
    
    # Function for handling the queue
    def _process_queue(self):
        while True:
            log.debug("\t\tWaiting for task in queue")
            item = self.queue.get()
            log.debug(f"\t\tDequeued item: {item}")
            if item is None:
                log.debug("\t\tExiting queue processing")
                break
            log.debug(f"\t\tProcessing task: {item[0]}")
            if isinstance(item, tuple) and len(item) == 2:
                task, future = item
                try:
                    result = task()
                    future.set_result(result)
                    print(f"Task completed with result: {result}")
                except Exception as e:
                    future.set_exception(e)  # Set exception on the future
                    log.error(f"Task failed with exception: {e}")  # Log the error
            else:
                log.debug(f"ADU Queue process, unexpected item structure: {item}")
            log.debug("\t\tTask processed successfully")

    # Function for handling queue of commands comming in for the device from different threads
    def _enqueue_command(self, function, *args, **kwargs):
        log.debug(f"\t\tEnqueuing command: {function.__name__}, args: {args}, kwargs: {kwargs}")
        future = Future()
        self.queue.put((lambda: function(*args, **kwargs), future))
        log.debug(f"\t\tCommand enqueued: {function.__name__}")
        return future
    
    # Validate connection - this is only controlled by a variable, self.initialized, 
    # which has nothing to do with the actual connection, so I am a bit unsure of the usfullness of this.
    def _validate_connection(self):
        log.debug("\t\tValidating ADU connection")
        with self._lock:  # Ensure connection validation is thread-safe
            log.debug("\t\tLock acquired for validating connection")
            if not self.initialized:
                log.debug("\t\tConnection not initialized, attempting to initialize")
                self._initialize_connection()
            return self.initialized

    # Functions for reading the adu device
    def read(self, command):
        future = self._enqueue_command(self._read, command)
        try:
            result = future.result()  # This will raise the RuntimeError if one was set
        except RuntimeError as e:
            log.error(f"An error occured when readuing from ADU. Command: {command}")
            # Optionally, re-raise or handle the error further
            raise RuntimeError(f"Lost connection to ADU. Failed with the command: {command}")
        return result  # Return the successful result if applicable

    def _read(self, command):
        log.debug("\t\tThread attempting to acquire lock in _read")
        with self._lock:
            log.debug("\t\tLock acquired in _read")
            if not self._validate_connection():
                return "Could not validate connection, please load ADU"
            if settings.getstopSignal():
                raise SystemExit("Stopping program adu read")
            stat = aduhid.write_device(device_handle, command, 300)
            print(f"Command: {command}, Stat: {stat} ")
            log.debug(f"Command: {command}, Stat: {stat} ")
            if stat != 0:
                result, value = aduhid.read_device(device_handle, 300)
                print(f"Command: {command}, Result: {result} , Value: {value}")
                log.debug(f"Command: {command}, Result: {result} , Value: {value}")
                if result != 0: 
                    return int(value)
                else:
                    error_message = self._get_last_error_message()
                    log.error(f"Unsuccessful read, command {command} " + error_message)
                    raise
            else:
                error_message = self._get_last_error_message()
                log.error(f"Unsuccessful read, command {command} " + error_message)
                # return error_message
                raise
            log.debug("\t\tReleasing lock in _read")

    def write(self, command):
        future = self._enqueue_command(self._write, command)
        try:
            result = future.result()  # This will raise the RuntimeError if one was set
        except RuntimeError as e:
            log.error(f"An error occured when writing to ADU. Command: {command}")
            # Optionally, re-raise or handle the error further
            raise RuntimeError(f"Lost connection to ADU. Failed with the command: {command}")
        return result  # Return the successful result if applicable

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
                raise


    # Function for turning on a relay
    def on(self, relay):
        if relay < 0 or relay > 7:
            log.error(f"The channel, {relay} is not a valid relay")
            return "Invalid relay channel"
        command = 'SK{}'.format(relay)
        print("TEST")
        self.write(command)

    # Function for turning off a relay
    def off(self, relay):
        if relay < 0 or relay > 7:
            log.error(f"The channel, {relay} is not a valid relay")
            return "Invalid relay channel"
        command = 'RK{}'.format(relay)
        self.write(command)


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
