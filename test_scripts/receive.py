#!/usr/bin/python3  
import sys, time
#import matplotlib.pyplot as plt

class ReadLine:
    def __init__(self, s):
        self.buf = bytearray()
        self.s = s
    
    def readline(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[:i+1]
            self.buf = self.buf[i+1:]
            return r
        while True:
            i = max(1, min(2048, self.s.in_waiting))
            data = self.s.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[:i+1]
                self.buf[0:] = data[i+1:]
                return r
            else:
                self.buf.extend(data)

#port = serial.Serial('COM3', baudrate=9600)
reader = ReadLine(port)

readings = 2000
#took_times = [0]*readings
took_times_reader = [0]*readings

c = 0
while c < readings:
    """
    t0=time.time()
    raw = port.read(10000)
    t1= time.time()
    tooktime = t1-t0
    print(f'{c:5d} receiving 10 kB now took', tooktime )
    took_times[c] = tooktime
    """
    t0= time.time()
    raw_reader = reader.readline()
    t1= time.time()
    tooktime = t1-t0
    print(f'{c:5d} receiving 10 kB now took', tooktime )
    took_times_reader[c] = tooktime    
    
    c+=1

#avrg = sum(took_times)/readings
avrg_reader = sum(took_times_reader)/readings

x = range(readings)
#plt.plot(x, took_times_reader)
#plt.hlines(y=avrg, xmin=0, xmax=2000, label=f"avrg time {avrg} s", color="orange")
#plt.hlines(y=avrg_reader, xmin=0, xmax=2000, label=f"avrg time reader {avrg_reader} s", color="orange")

#plt.legend()
#plt.show()