import threading
import time
import zmq
from ..socket import SourceSubscriber 
from ..socket import ServiceConsumer

'''
Allows you to send console commands over the network. Also listens to console outputs.
'''
class ConsoleMessage:
    def __init__(self,t,m):
        self.time = t
        self.message = m
        
    def printMessage(self):
        current_time = time.strftime("%H:%M:%S", self.time)
        print(current_time, "\n",self.message)
        
#-------------------------------------------------------------

class ConsoleCommandClient():
    def __init__(self, server_address):       
        self.service = ServiceConsumer('trodes.console.service', server_address=server_address)
        self.errorMessages = []
        self.outputMessages = []
        self.debugMessages = []
        
        self._listening = False
        
        
    #Starts a thread that subscribes to console_output 
    def open(self):
        if not self._listening:
            self.console_thread = threading.Thread(target=self._receive_console_message_thread)  # Insert into a thread
            self.console_thread.start()
            time.sleep(.25) #give the thread time to initialize before returning
            
        else:
            print('Error: listen thread already running')
        
        
    #Closes the thread that subscibed to console_output
    def close(self):
        self._listening = False
        
    #Send a command to the console input
    def send(self, comm):
        req = {'command': comm}
        self.service.request(req)
        
    #Returns true if listening to console_output
    def opened(self):
        return self._listening 
        
    #Copy error messages to a returned array and clear the local one
    def getErrors(self):
    	rArray = self.errorMessages.copy()
    	self.errorMessages.clear()
    	return rArray
    
    #Copy output messages to a returned array and clear the local one
    def getOutputs(self):
    	rArray = self.outputMessages.copy()
    	self.outputMessages.clear()
    	return rArray
    
    #Copy debug messages to a returned array and clear the local one	
    def getDebugs(self):
    	rArray = self.debugMessages.copy()
    	self.debugMessages.clear()
    	return rArray
    	

    #----Private----
    
    #Thread to poll the console_output channel  
    def _receive_console_message_thread(self):
        
        con_sub = SourceSubscriber('trodes.console_output',server_address="tcp://127.0.0.1:49152")
        self._listening = True

        while self._listening:
            try:
                res = con_sub.receive(noblock = True)
                if res['channel'] == 'output':
                    self.outputMessages.append(ConsoleMessage(time.localtime(),res['message']))                   
                elif res['channel'] == 'error':
                    self.errorMessages.append(ConsoleMessage(time.localtime(),res['message']))               
                elif res['channel'] == 'debug':
                    self.debugMessages.append(ConsoleMessage(time.localtime(),res['message']))
                pass
            except zmq.ZMQError as e:           
                time.sleep(.1) #determines how often we check for new messages
                pass  
                
            
            
        


