#RingbufQueue

import _thread
from utime import sleep_ms

class RingbufQueue:
    def __init__(self, buf, event_type):
        self._q = [event_type for _ in range(buf)] if isinstance(buf, int) else buf
        self._size = len(self._q) #buffer size
        self._wi = 0 #write index
        self._ri = 0 #read index
        self._max_q_size = 200 #biggest buffer size that can be allocated at once
        self._complete = False #tell the reader that we are done measuring

    def full(self): #no empty space to write
        return ((self._wi + 1) % self._size) == self._ri

    def empty(self): #there is nothing to read
        return self._ri == self._wi

    def qsize(self): #number of unread items
        return (self._wi - self._ri) % self._size

    '''def get_nowait(self):  # Remove and return an item from the queue.
        # Return an item if one is immediately available, else raise QueueEmpty.
        if self.empty():
            print("reading from empty buffer")
            raise IndexError
        r = self._q[self._ri]
        self._ri = (self._ri + 1) % self._size
        #self._evget.set()  # Schedule all tasks waiting on ._evget
        #self._evget.clear()
        return r'''

    def peek(self):  # Return oldest item from the queue without removing it.
        # Return an item if one is immediately available, else raise QueueEmpty.
        if self.empty():
            print("peeking on empty buffer")
            raise IndexError
        return self._q[self._ri]

    '''def put_nowait(self, v):
        self._q[self._wi] = v
        #self._evput.set()  # Schedule any tasks waiting on get
        #self._evput.clear()
        self._wi = (self._wi + 1) % self._size
        #if self._wi == self._ri:  # Would indicate empty
        while self._wi == self._ri:
            sleep_ms(1000)
            v[-1] += 1000 # Increase dead time
            print("core 0 sleeping for 1s because empty")
            self._ri = (self._ri + 1) % self._size  # Discard a message
            #raise IndexError  # Caller can ignore if overwrites are OK
        return v[-1]'''

    def put(self, val): #put an item in the buffer
        full = 0
        if self.full(): # check if the buffer is full
            full = 1
            while not self.empty(): # Wait until buffer is empty
                print("core 0 sleeping for 1s because full")
                sleep_ms(1000)
                val[-1] += 1000 # Increase dead time
            
        if full: print("I was full, buffer emptied")
        '''dead_t = self.put_nowait(val)'''
        self._q[self._wi] = val
        self._wi = (self._wi + 1) % self._size
        return val[-1]

    def get(self, wait_routine=None, args=None): #read available events
        r = None
        
        while self.empty():
            if wait_routine: #use the wait routine
                #print("Hello:",args)
                args[0], args[1] = wait_routine(*args)
            elif not self._complete: #check if the measurement is complete
                #print("empty buffer, waiting")
                sleep_ms(10) #give the reader some time to acquire events
            elif self._complete:
                return [[None]] #stop saving
        
        t_wi = self._wi
        #r = self._q[self._ri]
        q_size = self.qsize()
        
        if q_size > self._max_q_size:
            t_wi = (self._ri+self._max_q_size) % self._size
            print("big buffer "+str(q_size))
        else:
            t_wi = self._wi
        
        if t_wi > self._ri:
            r = self._q[self._ri:t_wi]
        else: # circle around de ring
            r = self._q[self._ri:]+self._q[:t_wi]
        #self._ri = (self._ri + 1) % self._size
        self._ri = t_wi

        if wait_routine:
            wait_r_results = wait_routine(*args)
            return r, wait_r_results
        else:
            return r