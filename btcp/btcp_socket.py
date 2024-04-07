import struct
import logging
from enum import IntEnum
import time
from btcp.constants import *


logger = logging.getLogger(__name__)


class BTCPStates(IntEnum):
    """Enum of BTCP states
    """
    CLOSED      = 0
    ACCEPTING   = 1
    SYN_SENT    = 2
    SYN_RCVD    = 3
    ESTABLISHED = 4 # There's an obvious state that goes here. Give it a name.
    FIN_SENT    = 5
    CLOSING     = 6
    __          = 7 # If you need more states, extend the Enum like this.


class BTCPSignals(IntEnum):
    """Enum class that you can use to signal from the Application thread
    to the Network thread.

    For example, rather than explicitly change state in the Application thread,
    you could put one of these in a variable that the network thread reads the
    next time it ticks, and handles the state change in the network thread.
    """
    ACCEPT = 1
    CONNECT = 2
    SHUTDOWN = 3


class BTCPSocket:
    """Base class for bTCP client and server sockets. Contains static helper
    methods that will definitely be useful for both sending and receiving side.
    """
    def __init__(self, window, timeout):
        logger.debug("__init__ called")
        self._window = window
        self._timeout = timeout
        self._state = BTCPStates.CLOSED
        logger.debug("Socket initialized with window %i and timeout %i",
                     self._window, self._timeout)
        self._timer = None


    @staticmethod
    def in_cksum(segment):
        """TODO: Compute the internet checksum of the segment given as argument.
        Consult lecture 3 for details.

        Our bTCP implementation always has an even number of bytes in a segment.

        Remember that, when computing the checksum value before *sending* the
        segment, the checksum field in the header should be set to 0x0000, and
        then the resulting checksum should be put in its place.
        """
        logger.debug("in_cksum() called")
        raise NotImplementedError("No implementation of in_cksum present. Read the comments & code of btcp_socket.py.")


    @staticmethod
    def verify_checksum(segment):
        """TODO: Verify that the checksum indicates is an uncorrupted segment.

        Mind that you change *what* signals that to the correct value(s).
        """
        logger.debug("verify_cksum() called")
        raise NotImplementedError("No implementation of in_cksum present. Read the comments & code of btcp_socket.py.")
        return BTCPSocket.in_cksum(segment) == 0xABCD


    @staticmethod
    def build_segment_header(seqnum, acknum,
                             syn_set=False, ack_set=False, fin_set=False,
                             window=0x01, length=0, checksum=0):
        """Pack the method arguments into a valid bTCP header using struct.pack
        """
        logger.debug("build_segment_header() called")
        flag_byte = syn_set << 2 | ack_set << 1 | fin_set
        logger.debug("build_segment_header() done")
        return struct.pack("!HHBBHH",
                           seqnum, acknum, flag_byte, window, length, checksum)
    
    @staticmethod
    def build_segment(header, data=b''):
        """Turn a header and data into a segment including padding.

        An empty bytestring is used by default when no data is included.
        """
        padding = b'\x00' * (PAYLOAD_SIZE - len(data))
        segment = header + data + padding
        return segment


    @staticmethod
    def unpack_segment_header(header):
        """Unpack the individual bTCP header field values from the header.

        Remember that Python supports multiple return values through automatic
        tupling, so it's easy to simply return all of them in one go rather
        than make a separate method for every individual field.
        """
        logger.debug("unpack_segment_header() called")
        seqnum, acknum, flag_byte, window, length, checksum = struct.unpack("!HHBBHH", header)
        flags = "{0:b}".format(flag_byte)

        # the size of the string of bits depends on what is the first set flag
        flagsize = len(flags)
        if flagsize == 3:
            synflag = flags[0]
            ackflag = flags[1]
            finflag = flags[2]
        elif flagsize ==2:
            synflag = 0
            ackflag = flags[0]
            finflag = flags[1]
        elif flagsize ==1:
            synflag = 0
            ackflag = 0
            finflag = int(flags)
        
        logger.debug("unpack_segment_header() done")
        return seqnum, acknum, (synflag, ackflag, finflag), window, length, checksum
        
    @staticmethod
    def _start_timer(self):
        if not self._timer:
            # logger.debug("Starting example timer.")
            # Time in *nano*seconds, not milli- or microseconds.
            # Using a monotonic clock ensures independence of weird stuff
            # like leap seconds and timezone changes.
            self._timer = time.monotonic_ns()
        else:
            pass
            # logger.debug("Example timer already running.")


    def _expire_timers(self):
        curtime = time.monotonic_ns()
        if not self._timer:
            # logger.debug("Example timer not running.")
            pass
        elif curtime - self._timer > self._timeout * 1_000_000:
            # logger.debug("Example timer elapsed.")
            self._timer = None
        else:
            # logger.debug("Example timer not yet elapsed.")
            pass