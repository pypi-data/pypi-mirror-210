
import win32api, win32con
import time

def key_test():
    win32api.keybd_event(0x7C,0,0,0)
    time.sleep(0.05)
    win32api.keybd_event(0x7C,0,win32con.KEYEVENTF_KEYUP,0)
    time.sleep(0.05)

def main():
    key_test()

if __name__ == "__main__":
    main()