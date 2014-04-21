# Adapted based on sample code by Christian Vogel (vogelchr@vogel.cx) 

import math
import operator
import serial

class AM03127():
    """Runs a AM03127-based signboard (http://www.amplus.com.hk/ aka Maplin N00GA)"""

    special_map = {
        u'\n': ' ',
        u'\r': '',
        u'<': '<UBC>',
        u'>': '<UBE>'
    }

    def __init__ (self, signport=None, baud=None, signid=None):
        default_signport = "/dev/ttyUSB0"
        default_baud = 9600
        default_signid = 1

        if not signport:
            signport = default_signport
        if not baud:
            baud = default_baud
        if not signid:
            signid = 1

        self.signport = signport
        self.baud = baud
        self.signid = signid

    def isAsciiRange (self, c, first, last) :
        if type(c) != str or len(c) != 1 :
            return False
        if ord(c) < ord(first) or ord(c) > ord(last) :
            return False
        return True

    def encodeCharset (self, unicode_str) :
        s = ''
        i = iter(unicode(unicode_str))
        for u in i :
            if u == '\033' :
                s = s + '<' + i.next() + i.next() + '>'
            elif u in self.special_map :
                s = s + self.special_map[u]
            else :
                s = s + u.encode('cp1252')
        return s

    def sendPageMessage (self, line=1, page='A', lead=None, disp='A', wait=5, lag=None, msg='') :
        default_lead_lag = 'E'

        if not lead :
            lead = default_lead_lag
        if not lag  :
            lag  = default_lead_lag

        rmsg = u''.join (map (unicode, msg))
        fmsg = self.encodeCharset(rmsg)

        if line < 1 or line > 8 :
            raise RuntimeError ('Line must be in range 1..8')
        if not self.isAsciiRange (page, 'A', 'Z') :
            raise RuntimeError ('Page must be in range A..Z')
        if not self.isAsciiRange (lead, 'A', 'S') :
            raise RuntimeError ('Lead must be in range A..S')
        if not (disp in 'ABCDEQRSTUabcdeqrstu') :
            raise RuntimeError ('Display must be one of {ABCDEQRSTUabcdeqrstu}')
        if not self.isAsciiRange (wait, 'A', 'Z') :
            raise RuntimeError ('Waittime must be in range A..Z (A=0.5 sec)')
        if not self.isAsciiRange (lag, 'A', 'S') :
            raise RuntimeError ('Lag must be in range A..S')
        return '<L%d><P%c><F%c><M%c><W%c><F%c>'%(line, page, lead, disp, wait, lag) + fmsg

    def setBrightness (self, brightness) :
        default_brightness='D'

        if not brightness :
            brightness = default_brightness

        if not self.isAsciiRange(brightness, 'A', 'D') :
            raise RuntimeError('Brightness must be in range A..D (100%..25%)')
        return '<B%c>'%(brightness)
    
    def displayMessage (self, line=1, page='A', lead=None, disp='A', wait=5, lag=None, msg='', brightness='A') :
        packets = []
        data = self.sendPageMessage (line, page, lead, disp, wait, lag, msg)
        packets.append (self.setBrightness(brightness))
        packets.append (data)
        self.sendPackets (packets)

    def encodeMessage (self, board_id, data) :
        if board_id < 0 or board_id > 255 :
            raise RuntimeError ('Sign ID must be in range 0..255')
        chksum = 0
        for c in data :
            chksum ^= ord(c)
        return '<ID%02X>'%(board_id) + data + '%02X<E>'%(chksum)

    def sendData (self, port, board_id, data) :
        port.setTimeout(1)
        encodedMessage = self.encodeMessage (board_id, data)
        print "TX:[" + encodedMessage + "]"
        port.write(encodedMessage)

        replies = [ 'ACK', 'NACK' ]
        buf = ''

        while True :
            c = port.read(1)
            if c == '' :
                return 'TIMEOUT'
            buf = buf + c

            valid_start = False
            for r in replies :
                if len(buf) > len(r) :
                    continue
                if buf == r[0:len(buf)] :
                    valid_start = True
                if len(buf) == len(r) :
                    return buf

            if not valid_start :
                return buf # invalid

    def sendPackets (self, packets_list):
        tty = serial.Serial(self.signport, self.baud)

        for data in packets_list:
            ret = self.sendData(tty, self.signid, data);
        if ret != 'ACK' :
            # We can't do anything at this point anyway, so pass
            pass
