import select
import tty
import termios
import os
import sys

class Key_Stroke():
    """
    linux KeyStroke implementation for foreground process'
    """

    def __init__(self):
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

    def __del__(self):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    @classmethod
    def kbhit(cls):
        """
        check if a key was pressed and return it

        Return:
            Bool:   True if a character was pressed, False if not
        """
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

    @classmethod
    def getch(cls):
        """
        Get the pressed character. Check first with kbHit if a key was
        pressed.

        Return:
            char:   The pressed character
        """
        c = sys.stdin.read(1)
        return c
    
    # def get_key(self):
    #     if self.kbhit():
    #         c = self.getch()
    #         if ord(c)==27: #arrow key is pressed
    #             arrow_key = ord(sys.stdin.read(2)[1]) # read two more bytes from character queu 
    #             if arrow_key==65:
    #                 c='up'
    #             elif arrow_key==66:
    #                 c='down'
    #             elif arrow_key==67:
    #                 c='right'
    #             elif arrow_key==68:
    #                 c='left'
    #         return c
    #     else:
    #         return False
    
    def get_key(self):
        b = os.read(sys.stdin.fileno(), 3).decode()
        if len(b) == 3:
            k = ord(b[2])
        elif len(b) == 1:
            k = ord(b)
        key_mapping = {
            127: 'backspace',
            10: 'return',
            32: 'space',
            9: 'tab',
            27: 'esc',
            65: 'up',
            66: 'down',
            67: 'right',
            68: 'left'
        }
        return key_mapping.get(k, chr(k))
    
    
if __name__=="__main__":
    print( os.getpgrp() == os.tcgetpgrp(sys.stdout.fileno()))

    kb = Key_Stroke()
    
    print("First method:")
    done = False
    while not done:
        if kb.kbhit():
            c = kb.getch()
            print('you pressed: ' + c + " , " + str(ord(c)))
            if c =='q':
                done = True
    
    print('\nNext method:')
    done = False
    while not done:
        c = kb.get_key()
        if c:
            print('you pressed: '+ c)
            if c == 'q':
                done = True
