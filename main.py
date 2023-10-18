from utime import sleep
import OLED
import _thread
    
def main():
    
    new_thread = _thread.start_new_thread(OLED.display_task, (0, "timer"))
    
    sgn2 = machine.ADC(26)
 
    counter = 0
    while True:
        reading = sgn2.read_u16()
        print("ADC: ", str(counter))
        counter +=1
    
if __name__ == '__main__':
    main()
