from utime import sleep
import OLED
import _thread
    
def main():
    
    new_thread = _thread.start_new_thread(OLED.display_task, (1, "timer"))
    OLED.display_task(Id=0, task="timer")
    
if __name__ == '__main__':
    main()
