import vfdpos
import usb.core
import time

default_screen_time = 2.0

class display:
    def __init__(self, default_message):
        self.wnpos = vfdpos.vfd_pos(0x0200)
        self.default_message = default_message
        self.show_default_message()

    def clear(self):
        self.wnpos.clearscreen()
        self.wnpos.poscur(1, 1)
        self._col = 1
        self._row = 1

    def show_message(self,message):
        self.clear()
        i = message.find('\n')
        if i != -1:
            self._row = 2
            self._col = len(message)-i-1
            self.wnpos.write_msg(message[:i])
            self.wnpos.poscur(2,1)
            self.wnpos.write_msg(message[-(len(message)-i-1):])
        else:
            self._col = len(message) + 1
            self.wnpos.write_msg(message)


        print(str(self._row) + " " + str(self._col))


    def show_default_message(self):
        self.show_message(self.default_message)

    def show_saldo(self, username, saldo):
        self.show_message("Iltaa " + username + "!\r\nSaldo: " + str(saldo))
        time.sleep(default_screen_time)
        self.show_default_message()

    def add_str(self, st):
        self.wnpos.write_msg(st)
        i = st.find('\n')
        if i != -1:
            self._row = 2
            self._col = len(st)
        else:
            self._col += len(st)
        print(str(self._row) + " " + str(self._col))

    def backspace(self):
        self._col -= 1
        self.wnpos.poscur(self._row, self._col)
        self.wnpos.write_msg(' ')
        self.wnpos.poscur(self._row, self._col)

    def indent_line(self):
        self.wnpos.poscur(0, 1)
        self._col = 1

    def show_temp_message(self, err):
        self.show_message(err)
        time.sleep(default_screen_time)
        self.show_default_message()

