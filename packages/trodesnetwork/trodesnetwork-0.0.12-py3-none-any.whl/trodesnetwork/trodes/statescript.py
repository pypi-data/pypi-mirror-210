import threading
import time
import zmq
from ..socket import SourceSubscriber 
from ..socket import ServiceConsumer

'''
Allows you to communicate with the StateScript module over the network.
'''

class StateScriptMessage:
    def __init__(self,lt,st,m):
        #localTimestamp is the sample number of the data stream
        #systemTimestamp is the linux time in ns
        self.localtime = lt
        self.systemtime = st
        self.message = m
        
    def printMessage(self):
        #current_time = time.strftime("%H:%M:%S", self.localtime)
        print(str(self.systemtime), " ",str(self.localtime), "\n",self.message)
        
        
        
        
class StateScriptClient():
    def __init__(self, server_address):
        self.scriptservice = ServiceConsumer('statescript.service', server_address=server_address)
        self.statescriptOutput = []
        self.errorMessages = []
        self.outputMessages = []
        self.debugMessages = []       
        self._listening = False

    def send(self, s):
        req = {'command': 'send','string': s}
        self.scriptservice.request(req)
        
    def connect(self, s):
        req = {'command': 'connect','string': s}
        self.scriptservice.request(req)
        
    def disconnect(self, s):
        req = {'command': 'disconnect','string': s}
        self.scriptservice.request(req)
        
    #Starts a thread that subscribes to console_output 
    def open(self):
        if not self._listening:
            self.listen_thread = threading.Thread(target=self._receive_statescript_message_thread)  # Insert into a thread
            self.listen_thread.start()
            time.sleep(.25) #give the thread time to initialize before returning
            
        else:
            print('Error: listen thread already running')
        
        
    #Closes the thread that subscibed to console_output
    def close(self):
        self._listening = False

    
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
    	
    #Copy statescript messages to a returned array and clear the local one	
    def getStateScriptMessages(self):
    	rArray = self.statescriptOutput.copy()
    	self.statescriptOutput.clear()
    	return rArray

    #----Private----
    
    #Thread to poll the console_output channel  
    def _receive_statescript_message_thread(self):
        
        con_sub = SourceSubscriber('statescript.output',server_address="tcp://127.0.0.1:49152")
        self._listening = True

        while self._listening:
            try:
                res = con_sub.receive(noblock = True)               
                if res['channel'] == 'output':
                    self.outputMessages.append(StateScriptMessage(res['localTimestamp'],res['systemTimestamp'],res['message']))                   
                elif res['channel'] == 'error':
                    self.errorMessages.append(StateScriptMessage(res['localTimestamp'],res['systemTimestamp'],res['message']))               
                elif res['channel'] == 'debug':
                    self.debugMessages.append(StateScriptMessage(res['localTimestamp'],res['systemTimestamp'],res['message']))
                elif res['channel'] == 'statescript':
                    self.statescriptOutput.append(StateScriptMessage(res['localTimestamp'],res['systemTimestamp'],res['message']))
                pass
            except zmq.ZMQError as e:           
                time.sleep(.1) #determines how often we check for new messages
                pass  
                
    
    
    




