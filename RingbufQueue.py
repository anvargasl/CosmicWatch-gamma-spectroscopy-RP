import _thread
from utime import sleep_ms

class RingbufQueue:
    def __init__(self, buf):
        self._q = [0 for _ in range(buf)] if isinstance(buf, int) else buf
        self._size = len(self._q) #buffer size
        self._wi = 0 #write index
        self._ri = 0 #read index
        self._max_q_size = 100 #biggest buffer size that can be allocated at once
        #self._evput = asyncio.Event()  # Triggered by put, tested by get
        #self._evget = asyncio.Event()  # Triggered by get, tested by put

    def full(self): #check if we are overwriting the buffer
        return ((self._wi + 1) % self._size) == self._ri

    def empty(self): #last item read = last saved
        return self._ri == self._wi

    def qsize(self): #number of unread items
        return (self._wi - self._ri) % self._size

    def get_nowait(self):  # Remove and return an item from the queue.
        # Return an item if one is immediately available, else raise QueueEmpty.
        if self.empty():
            raise IndexError
        r = self._q[self._ri]
        self._ri = (self._ri + 1) % self._size
        #self._evget.set()  # Schedule all tasks waiting on ._evget
        #self._evget.clear()
        return r

    def peek(self):  # Return oldest item from the queue without removing it.
        # Return an item if one is immediately available, else raise QueueEmpty.
        if self.empty():
            raise IndexError
        return self._q[self._ri]

    def put_nowait(self, v):
        self._q[self._wi] = v
        #self._evput.set()  # Schedule any tasks waiting on get
        #self._evput.clear()
        self._wi = (self._wi + 1) % self._size
        #if self._wi == self._ri:  # Would indicate empty
        while self._wi == self._ri:
            sleep_ms(1000)
            v[-1] += 1000 #dead time
            print("core 0 sleeping for 1s because empty")
            #self._ri = (self._ri + 1) % self._size  # Discard a message
            #raise IndexError  # Caller can ignore if overwrites are OK
        return v[-1]

    #async def put(self, val):  # Usage: await queue.put(item)
    def put(self, val):
        while self.full():  # Queue full
            print("core 0 sleeping for 1s because full")
            sleep_ms(1000)
            val[-1] += 1000 #dead time
            #await self._evget.wait()  # May be >1 task waiting on ._evget
            # Task(s) waiting to get from queue, schedule first Task
        dead_t = self.put_nowait(val)
        return dead_t

    def __aiter__(self):
        return self

    #async def __anext__(self):
    #    return await self.get()

    #async def get(self, wait_routine, args):
    def get(self, wait_routine, args):
        while self.empty():  # Empty. May be more than one task waiting on ._evput
            #await self._evput.wait()
            args = wait_routine(*args)
            #print("waiting")
        t_wi = self._wi
        #r = self._q[self._ri]
        q_size = self.qsize()
        
        if q_size > self._max_q_size:
            t_wi = (self._ri+self._max_q_size) % self._size
            print("big buffer "+str(q_size))
        else:
            t_wi = self._wi
        
        r = None
        if t_wi > self._ri:
            r = self._q[self._ri:t_wi]
            #print("case 1")
            #print(r)
        else:
            r = self._q[self._ri:]+self._q[:t_wi]
            #print("case 2", t_wi, self._ri)
            #print(r)
        #self._ri = (self._ri + 1) % self._size
        self._ri = t_wi
        #self._evget.set()  # Schedule all tasks waiting on ._evget
        #self._evget.clear()
        wait_r_results = wait_routine(*args)
        return r, wait_r_results