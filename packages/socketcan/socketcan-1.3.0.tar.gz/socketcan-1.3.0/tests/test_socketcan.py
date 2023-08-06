""" Test_socketcan

    Collection of tests for socketcan module to be run with pytest / tox / coverage
    @author: Patrick Menschel (menschel.p@posteo.de)
    @license: GPL v3
"""

from typing import Optional

import pytest

from queue import Queue, Empty

from socketcan import CanFrame, CanFlags, CanFdFlags, CanFdFrame, BCMFlags, BcmMsg, BcmOpCodes, CanRawSocket, \
    CanIsoTpSocket, CanBcmSocket, CanJ1939Socket

from socketcan.socketcan import split_can_id_and_flags, IsoTpOpts, CAN_ISOTP_TX_PADDING, CAN_ISOTP_RX_PADDING, \
    IsoTpFcOpts, CanFilter, IsoTpLLOpts

from subprocess import CalledProcessError, check_output

from threading import Thread

import time

import platform

from tests.mocks import MockSocket

import logging

LOGGER = logging.getLogger()


def is_can_available() -> Optional[list]:
    """
    get available can interfaces via ip link
    :return: A list of interface names that are family link/can
    """
    try:
        return [line.split(":")[1].strip() for line in
                check_output("ip -o link show | grep link/can", shell=True).decode().splitlines()]
    except CalledProcessError:
        pass
    return


@pytest.fixture
def can_interface() -> Optional[str]:
    """
    PyTest fixture to be used in socket based tests.
    It basically retrieves the network interface
    names for can and then selects the first one.
    :return:
    """
    interface_names = is_can_available()
    if interface_names:
        return interface_names[0]


def mcp0_and_mcp1_available() -> bool:
    """
    Determine if mcp0 and mcp1 are available,
    assuming both are directly connected for real transfer.
    :return: True if both available.
    """
    ret = False
    available_can_interfaces = is_can_available()
    if available_can_interfaces is not None and all(
            interface in available_can_interfaces for interface in ["mcp0", "mcp1"]):
        q = Queue()
        p = Thread(target=receive_from_can_raw_socket, args=("mcp1", q,))
        p.daemon = True
        p.start()
        frame1 = CanFrame(can_id=0x12345678, data=bytes(8))
        s = CanRawSocket("mcp0")
        s.send(frame1)
        try:
            frame2 = q.get(timeout=1)
        except Empty:
            pass
        else:
            if frame2.can_id == frame1.can_id \
                    and frame2.data == frame1.data:
                ret = True
    return ret


def vcan0_available() -> bool:
    """
    Determine if vcan0 is available.
    :return: True if both available.
    """
    ret = False
    available_can_interfaces = is_can_available()
    if available_can_interfaces is not None and "vcan0" in available_can_interfaces:
        ret = True
    return ret


def is_isotp_available() -> bool:
    """
    A helper function to determine if isotp
    is available on the system.
    :return: True if the driver module file is found.
    """
    try:
        if check_output("ls /lib/modules/$(uname -r)/kernel/net/can/can-isotp.ko", shell=True).strip():
            return True
    except CalledProcessError:
        pass
    return False


def is_j1939_available() -> bool:
    """
    A helper function to determine if isotp
    is available on the system.
    :return: True if the driver module file is found.
    """
    try:
        if check_output("ls /lib/modules/$(uname -r)/kernel/net/can/j1939/can-j1939.ko", shell=True).strip():
            return True
    except CalledProcessError:
        pass
    return False


def receive_from_can_isotp_socket(interface, rx_addr, tx_addr, bufsize, use_padding, listen_only, fc_stmin, use_canfd,
                                  q):
    """
    A helper function to receive something via isotp and verify the contents in a test.
    This is intended to be run in a thread parallel to the test.
    :param interface: The interface name.
    :param rx_addr: The rx can id.
    :param tx_addr: The tx can id.
    :param bufsize: The buffer size to be used.
    :param use_padding: The padding option flag.
    :param listen_only: The listen_only_option_flag
    :param fc_stmin: The frame in between consecutive frames.
    :param use_canfd: Option to use canfd via LL Opts
    :param q: The queue where to put the received data into.
    :return: None.
    """
    s = CanIsoTpSocket(interface=interface, rx_addr=rx_addr, tx_addr=tx_addr,
                       use_padding=use_padding, listen_only=listen_only, fc_stmin=fc_stmin,
                       use_canfd=use_canfd)
    q.put(s.recv(bufsize=bufsize))


def receive_from_can_raw_socket(interface, q):
    """
    A helper function to receive a can frame from raw socket.
    :param interface: The interface name.
    :param q: The queue where to put the received data into.
    :return: None.
    """
    s = CanRawSocket(interface=interface)
    q.put(s.recv())


def receive_from_can_raw_socket_with_timestamp(interface, q):
    """
    A helper function to receive a can frame from raw socket.
    :param interface: The interface name.
    :param q: The queue where to put the received data into.
    :return: None.
    """
    s = CanRawSocket(interface=interface)
    q.put(s.recvmsg())


def receive_from_can_raw_socket_with_filter(interface, can_filter, q):
    """
    A helper function to receive a can frame from raw socket.
    :param interface: The interface name.
    :param can_filter: The CanFilter object.
    :param q: The queue where to put the received data into.
    :return: None.
    """
    s = CanRawSocket(interface=interface, can_filters=(can_filter,))
    q.put(s.recv())


def receive_from_bcm_socket(interface, can_id, interval, q):
    """
    A helper function to receive a can frame from bcm socket.
    :param interface: The interface name.
    :param can_id: The can id to be received.
    :param interval: The expected interval or rather the timeout.
    :param q: The queue where to put the received data into.
    :return: None.
    """
    s = CanBcmSocket(interface=interface)
    data = bytes.fromhex("FF FF FF FF FF FF FF FF")
    frame = CanFrame(can_id=can_id,
                     data=data)

    s.setup_receive_filter(frame=frame, timeout=interval * 2)
    q.put(s.recv())


def receive_from_j1939_socket(interface, q):
    """
    A helper function to receive a can frame from j1939 socket.
    :param interface: The interface name.
    :param q: The queue where to put the received data into.
    :return: None.
    """
    s = CanJ1939Socket(interface=interface)
    q.put(s.recvfrom())


class TestObjectCreation:
    """
    A collection of tests for concat / parse objects.
    """

    def test_unequal_frames(self):
        can_id1 = 0x123
        data1 = bytes(range(0, 0x88, 0x11))
        frame1 = CanFrame(can_id=can_id1,
                          data=data1)

        can_id2 = 0x12345678
        data2 = bytes(range(0, 0x44, 0x11))
        frame2 = CanFrame(can_id=can_id2,
                          data=data2)

        assert frame1 != frame2

    def test_can_frame_creation_with_short_id(self):
        can_id = 0x123
        data = bytes(range(0, 0x88, 0x11))
        frame1 = CanFrame(can_id=can_id,
                          data=data)
        flags = frame1.flags
        assert not (flags & CanFlags.CAN_EFF_FLAG)
        assert not (flags & CanFlags.CAN_RTR_FLAG)
        assert not (flags & CanFlags.CAN_ERR_FLAG)
        frame_as_bytes = frame1.to_bytes()

        assert len(frame_as_bytes) == CanFrame.get_size()

        frame2 = CanFrame.from_bytes(frame_as_bytes)
        assert frame1 == frame2

    def test_can_frame_creation_with_short_id_and_short_data(self):
        can_id = 0x123
        data = bytes(range(0, 0x44, 0x11))
        frame1 = CanFrame(can_id=can_id,
                          data=data)
        flags = frame1.flags
        assert not (flags & CanFlags.CAN_EFF_FLAG)
        assert not (flags & CanFlags.CAN_RTR_FLAG)
        assert not (flags & CanFlags.CAN_ERR_FLAG)
        frame_as_bytes = frame1.to_bytes()

        assert len(frame_as_bytes) == CanFrame.get_size()

        frame2 = CanFrame.from_bytes(frame_as_bytes)
        assert frame1 == frame2

    def test_can_frame_creation_with_short_id_and_rtr_flag(self):
        can_id = 0x123
        flags = CanFlags.CAN_RTR_FLAG
        data = bytes(range(0, 0x88, 0x11))
        frame1 = CanFrame(can_id=can_id,
                          flags=flags,
                          data=data)
        flags = frame1.flags
        assert not (flags & CanFlags.CAN_EFF_FLAG)
        assert (flags & CanFlags.CAN_RTR_FLAG)
        assert not (flags & CanFlags.CAN_ERR_FLAG)
        frame_as_bytes = frame1.to_bytes()

        assert len(frame_as_bytes) == CanFrame.get_size()

        frame2 = CanFrame.from_bytes(frame_as_bytes)
        assert frame1 == frame2

    def test_can_frame_creation_with_short_id_and_err_flag(self):
        can_id = 0x123
        flags = CanFlags.CAN_ERR_FLAG
        data = bytes(range(0, 0x88, 0x11))
        frame1 = CanFrame(can_id=can_id,
                          flags=flags,
                          data=data)
        flags = frame1.flags
        assert not (flags & CanFlags.CAN_EFF_FLAG)
        assert not (flags & CanFlags.CAN_RTR_FLAG)
        assert (flags & CanFlags.CAN_ERR_FLAG)
        frame_as_bytes = frame1.to_bytes()

        assert len(frame_as_bytes) == CanFrame.get_size()

        frame2 = CanFrame.from_bytes(frame_as_bytes)
        assert frame1 == frame2

    def test_can_frame_creation_with_long_id_and_no_eff_flag(self):
        can_id = 0x12345678
        data = bytes(range(0, 0x88, 0x11))
        frame1 = CanFrame(can_id=can_id,
                          data=data)
        flags = frame1.flags
        assert (flags & CanFlags.CAN_EFF_FLAG)
        assert not (flags & CanFlags.CAN_RTR_FLAG)
        assert not (flags & CanFlags.CAN_ERR_FLAG)
        frame_as_bytes = frame1.to_bytes()

        assert len(frame_as_bytes) == CanFrame.get_size()

        frame2 = CanFrame.from_bytes(frame_as_bytes)
        assert frame1 == frame2

    def test_can_frame_creation_with_long_id_and_eff_flag(self):
        can_id = 0x12345678
        flags = CanFlags.CAN_EFF_FLAG
        data = bytes(range(0, 0x88, 0x11))
        frame1 = CanFrame(can_id=can_id,
                          flags=flags,
                          data=data)
        flags = frame1.flags
        assert (flags & CanFlags.CAN_EFF_FLAG)
        assert not (flags & CanFlags.CAN_RTR_FLAG)
        assert not (flags & CanFlags.CAN_ERR_FLAG)
        frame_as_bytes = frame1.to_bytes()

        assert len(frame_as_bytes) == CanFrame.get_size()

        frame2 = CanFrame.from_bytes(frame_as_bytes)
        assert frame1 == frame2

    def test_can_frame_creation_with_long_id_and_short_data(self):
        can_id = 0x12345678
        data = bytes(range(0, 0x44, 0x11))
        frame1 = CanFrame(can_id=can_id,
                          data=data)
        flags = frame1.flags
        assert (flags & CanFlags.CAN_EFF_FLAG)
        assert not (flags & CanFlags.CAN_RTR_FLAG)
        assert not (flags & CanFlags.CAN_ERR_FLAG)
        frame_as_bytes = frame1.to_bytes()

        assert len(frame_as_bytes) == CanFrame.get_size()

        frame2 = CanFrame.from_bytes(frame_as_bytes)
        assert frame1 == frame2

    def test_can_fd_frame_creation(self):
        can_id = 0x12345678
        data = bytes(range(64))
        frame1 = CanFdFrame(can_id=can_id,
                            data=data)
        frame_as_bytes = frame1.to_bytes()

        assert len(frame_as_bytes) == CanFdFrame.get_size()

        frame2 = CanFdFrame.from_bytes(frame_as_bytes)
        assert frame1 == frame2

    def test_can_fd_frame_unequal(self):
        can_id = 0x12345678
        data = bytes(range(64))
        frame1 = CanFdFrame(can_id=can_id,
                            data=data)
        can_id = 0x123
        data = bytes(range(64))
        frame2 = CanFdFrame(can_id=can_id,
                            data=data)
        assert frame1 != frame2

    def test_bcm_msg_creation(self):
        can_id = 0x123
        data = bytes(range(0, 0x88, 0x11))

        frame1 = CanFrame(can_id=can_id,
                          data=data)
        opcode = BcmOpCodes.TX_SETUP
        flags = BCMFlags(BCMFlags.SETTIMER | BCMFlags.STARTTIMER)
        frames = [frame1, ]
        interval = 0.1
        bcm1 = BcmMsg(opcode=opcode,
                      flags=flags,
                      count=0,
                      interval1=0,
                      interval2=interval,
                      can_id=can_id,
                      frames=frames,
                      )
        bcm_as_bytes = bcm1.to_bytes()
        assert len(bcm_as_bytes) == BcmMsg.get_size() + (CanFrame.get_size() * len(frames))

        bcm2 = BcmMsg.from_bytes(bcm_as_bytes)
        assert bcm1 == bcm2

    def test_unequal_bcm_msgs(self):
        can_id = 0x123
        data = bytes(range(0, 0x88, 0x11))

        frame1 = CanFrame(can_id=can_id,
                          data=data)
        opcode = BcmOpCodes.TX_SETUP
        flags = BCMFlags(BCMFlags.SETTIMER | BCMFlags.STARTTIMER)
        frames = [frame1, ]
        interval = 0.1
        bcm1 = BcmMsg(opcode=opcode,
                      flags=flags,
                      count=0,
                      interval1=0,
                      interval2=interval,
                      can_id=can_id,
                      frames=frames,
                      )
        bcm_as_bytes = bcm1.to_bytes()
        assert len(bcm_as_bytes) == BcmMsg.get_size() + (CanFrame.get_size() * len(frames))

        interval2 = 1
        bcm2 = BcmMsg(opcode=opcode,
                      flags=flags,
                      count=0,
                      interval1=0,
                      interval2=interval2,
                      can_id=can_id,
                      frames=frames,
                      )

        assert bcm1 != bcm2

    def test_bcm_msg_creation_with_2_frames(self):
        can_id = 0x123
        data = bytes(range(0, 0x88, 0x11))

        frame1 = CanFrame(can_id=can_id,
                          data=data)
        can_id2 = 0x456
        data2 = bytes(range(0, 0x88, 0x11))
        frame2 = CanFrame(can_id=can_id2,
                          data=data2)

        opcode = BcmOpCodes.TX_SETUP
        flags = BCMFlags(BCMFlags.SETTIMER | BCMFlags.STARTTIMER)
        frames = [frame1,
                  frame2,
                  ]
        interval = 0.1
        bcm1 = BcmMsg(opcode=opcode,
                      flags=flags,
                      count=0,
                      interval1=0,
                      interval2=interval,
                      can_id=can_id,
                      frames=frames,
                      )
        bcm_as_bytes = bcm1.to_bytes()
        assert len(bcm_as_bytes) == BcmMsg.get_size() + (CanFrame.get_size() * len(frames))

        bcm2 = BcmMsg.from_bytes(bcm_as_bytes)
        assert bcm1 == bcm2

    def test_bcm_msg_creation_with_2_extended_frames_and_different_sizes(self):
        can_id = 0x12345678
        data = bytes(range(0, 0x88, 0x11))

        frame1 = CanFrame(can_id=can_id,
                          data=data)
        can_id2 = 0x1FFFF456
        data2 = bytes(range(0, 0x44, 0x11))
        frame2 = CanFrame(can_id=can_id2,
                          data=data2)

        opcode = BcmOpCodes.TX_SETUP
        flags = BCMFlags(BCMFlags.SETTIMER | BCMFlags.STARTTIMER)
        frames = [frame1,
                  frame2,
                  ]
        interval = 0.1
        bcm1 = BcmMsg(opcode=opcode,
                      flags=flags,
                      count=0,
                      interval1=0,
                      interval2=interval,
                      can_id=can_id,
                      frames=frames,
                      )
        bcm_as_bytes = bcm1.to_bytes()
        assert len(bcm_as_bytes) == BcmMsg.get_size() + (CanFrame.get_size() * len(frames))

        bcm2 = BcmMsg.from_bytes(bcm_as_bytes)
        assert bcm1 == bcm2

    def test_bcm_msg_creation_with_2_extended_frames_and_ival1(self):
        can_id = 0x12345678
        data = bytes(range(0, 0x88, 0x11))

        frame1 = CanFrame(can_id=can_id,
                          data=data)
        can_id2 = 0x1FFFF456
        data2 = bytes(range(0, 0x44, 0x11))
        frame2 = CanFrame(can_id=can_id2,
                          data=data2)

        opcode = BcmOpCodes.TX_SETUP
        flags = BCMFlags(BCMFlags.SETTIMER | BCMFlags.STARTTIMER)
        frames = [frame1,
                  frame2,
                  ]
        interval1 = 0.1
        interval2 = 5
        bcm1 = BcmMsg(opcode=opcode,
                      flags=flags,
                      count=0,
                      interval1=interval1,
                      interval2=interval2,
                      can_id=can_id,
                      frames=frames,
                      )
        bcm_as_bytes = bcm1.to_bytes()
        assert len(bcm_as_bytes) == BcmMsg.get_size() + (CanFrame.get_size() * len(frames))

        bcm2 = BcmMsg.from_bytes(bcm_as_bytes)
        assert bcm1 == bcm2

    def test_bcm_msg_creation_with_canfd_frame(self):
        can_id = 0x12345678
        data = bytes(range(0, 0x88, 0x11))

        frame1 = CanFdFrame(can_id=can_id,
                            data=data)
        opcode = BcmOpCodes.TX_SETUP
        flags = BCMFlags(BCMFlags.SETTIMER | BCMFlags.STARTTIMER)
        frames = [frame1,
                  ]
        bcm1 = BcmMsg(opcode=opcode,
                      flags=flags,
                      count=0,
                      interval1=0,
                      interval2=1,
                      can_id=can_id,
                      frames=frames,
                      )
        bcm_as_bytes = bcm1.to_bytes()
        assert len(bcm_as_bytes) == BcmMsg.get_size() + (CanFdFrame.get_size() * len(frames))


    def test_isotp_opts(self):
        opts = IsoTpOpts(flags=CAN_ISOTP_TX_PADDING | CAN_ISOTP_RX_PADDING,
                         frame_txtime=100,
                         ext_address=0xF1,
                         txpadding=0xAA,
                         rxpadding=0xAA,
                         rx_ext_address=0xFA
                         )
        data = opts.to_bytes()
        opts2 = IsoTpOpts.from_bytes(data)
        assert opts == opts2
        assert not opts != opts2

    @pytest.mark.xfail
    def test_isotp_opts_should_fail(self):
        opts = IsoTpOpts(flags=CAN_ISOTP_TX_PADDING | CAN_ISOTP_RX_PADDING,
                         frame_txtime=100,
                         ext_address=0xF1,
                         txpadding=0xAA,
                         rxpadding=0xAA,
                         rx_ext_address=0xFA
                         )
        data = opts.to_bytes()
        opts.ext_address = 0
        opts2 = IsoTpOpts.from_bytes(data)
        assert opts == opts2

    def test_isotp_fc_opts(self):
        opts = IsoTpFcOpts(bs=0xF,
                           stmin=5,
                           wftmax=1,
                           )
        data = opts.to_bytes()
        opts2 = IsoTpFcOpts.from_bytes(data)
        assert opts == opts2
        assert not opts != opts2

    @pytest.mark.xfail
    def test_isotp_fc_opts_should_fail(self):
        opts = IsoTpFcOpts(bs=0xF,
                           stmin=5,
                           wftmax=1,
                           )
        data = opts.to_bytes()
        opts.bs = 0
        opts2 = IsoTpFcOpts.from_bytes(data)
        assert opts == opts2

    def test_isotp_ll_opts(self):
        opts = IsoTpLLOpts()
        data = opts.to_bytes()
        opts2 = IsoTpLLOpts.from_bytes(data)
        assert opts == opts2
        assert not opts != opts2

    @pytest.mark.xfail
    def test_isotp_ll_opts_should_fail(self):
        opts = IsoTpLLOpts()
        data = opts.to_bytes()
        opts2 = IsoTpLLOpts.from_bytes(data)
        opts.mtu = 0
        assert opts == opts2

    def test_can_filter_creation(self):
        can_id = 0x12345678
        rfilter = CanFilter(can_id=can_id, can_mask=0x1FFFFFFF)
        assert rfilter


@pytest.mark.skipif(not is_can_available(), reason="this test requires a can interface to be set up")
class TestCanRawSocket:
    """
    A collection of tests for the raw socket.
    """

    def test_can_raw_socket(self, can_interface):
        s = CanRawSocket(interface=can_interface)
        fileno = s.fileno()
        assert fileno
        can_id = 0x12345678
        data = bytes(range(0, 0x88, 0x11))
        frame1 = CanFrame(can_id=can_id,
                          data=data)

        q = Queue()
        p = Thread(target=receive_from_can_raw_socket, args=(can_interface, q,))
        p.daemon = True
        p.start()
        time.sleep(1)
        s.send(frame1)
        frame2 = q.get(timeout=10)
        p.join()

        assert frame1 == frame2

        assert not frame1 != frame2  # this is stupid but what do we do for 100% coverage ;-)

    def test_can_raw_socket_w_can_fd(self, can_interface):
        s = CanRawSocket(interface=can_interface)
        can_id = 0x12345678
        data = bytes(range(64))
        frame1 = CanFdFrame(can_id=can_id,
                            data=data)

        q = Queue()
        p = Thread(target=receive_from_can_raw_socket, args=(can_interface, q,))
        p.daemon = True
        p.start()
        time.sleep(1)
        s.send(frame1)
        frame2 = q.get(timeout=10)
        p.join()
        print(frame2.can_id)
        print(frame2.data)
        assert frame1 == frame2

    @pytest.mark.skipif(not vcan0_available(),
                        reason="this test requires vcan0")
    def test_can_type_after_vcan_transfer(self):
        s = CanRawSocket(interface="vcan0")
        can_id = 0x12345678
        data = bytes(range(8))  # this frame could be a normal can frame
        frame1 = CanFdFrame(can_id=can_id,
                            data=data,
                            fd_flags=CanFdFlags(0))

        q = Queue()
        p = Thread(target=receive_from_can_raw_socket, args=("vcan0", q,))
        p.daemon = True
        p.start()
        time.sleep(1)
        s.send(frame1)
        frame2 = q.get(timeout=10)
        p.join()
        print(frame2.can_id)
        print(frame2.data)
        assert frame1 == frame2

    @pytest.mark.skipif(not mcp0_and_mcp1_available(),
                        reason="this test requires two connected interfaces, mcp0 and mcp1")
    def test_can_type_after_real_transfer(self):
        s = CanRawSocket(interface="mcp0")
        can_id = 0x12345678
        data = bytes(range(8))  # this frame could be a normal can frame
        frame1 = CanFdFrame(can_id=can_id,
                            data=data,
                            fd_flags=CanFdFlags(0))

        q = Queue()
        p = Thread(target=receive_from_can_raw_socket, args=("mcp1", q,))
        p.daemon = True
        p.start()
        time.sleep(1)
        s.send(frame1)
        frame2 = q.get(timeout=10)
        p.join()
        print(frame2.can_id)
        print(frame2.data)
        assert frame1 == frame2

    @pytest.mark.skipif(not vcan0_available(),
                        reason="this test requires vcan0")
    def test_raw_message_with_timestamp(self):
        s = CanRawSocket(interface="vcan0")
        can_id = 0x12345678
        data = bytes(range(8))  # this frame could be a normal can frame
        frame1 = CanFdFrame(can_id=can_id,
                            data=data,
                            fd_flags=CanFdFlags(0))

        q = Queue()
        p = Thread(target=receive_from_can_raw_socket_with_timestamp, args=("vcan0", q,))
        p.daemon = True
        p.start()
        time.sleep(1)
        s.send(frame1)
        timestamp, frame2 = q.get(timeout=10)
        print("received frame at timestamp {0}".format(timestamp))
        p.join()

        assert frame1 == frame2

    @pytest.mark.skipif(not vcan0_available(),
                        reason="this test requires vcan0")
    def test_raw_socket_with_filter(self):
        s = CanRawSocket(interface="vcan0")
        can_id = 0x11223344
        data = bytes(range(8))  # this frame could be a normal can frame
        frame1 = CanFrame(can_id=can_id,
                          data=data,
                          )

        can_id = 0x12345678
        data = bytes(range(8))  # this frame could be a normal can frame
        frame2 = CanFrame(can_id=can_id,
                          data=data,
                          )

        q = Queue()
        rfilter = CanFilter(can_id=can_id, can_mask=0x1FFFFFFF)
        p = Thread(target=receive_from_can_raw_socket_with_filter, args=("vcan0", rfilter, q,))
        p.daemon = True
        p.start()
        time.sleep(1)
        s.send(frame1)
        with pytest.raises(Empty):
            q.get(timeout=1)
        s.send(frame2)
        frame3 = q.get(timeout=10)
        p.join()

        assert frame2 == frame3


@pytest.mark.skipif(not (is_can_available()
                         and is_isotp_available()),
                    reason="this test requires a can interface to be set up and isotp kernel module, mainline kernel "
                           ">= 5.10")
class TestCanIsoTpSocket:
    """
    A collection of tests for the IsoTp socket.
    """

    def test_can_isotp_socket(self, can_interface):
        rx_addr = 0x7e0
        tx_addr = 0x7e8
        use_padding = False
        s = CanIsoTpSocket(interface=can_interface, rx_addr=rx_addr, tx_addr=tx_addr, use_padding=use_padding)
        fileno = s.fileno()
        assert fileno
        data = bytes(range(64))
        bufsize = len(data)
        q = Queue()
        # Note: the receive thread logically has rx_addr, tx_addr inverted!
        p = Thread(target=receive_from_can_isotp_socket,
                   args=(can_interface, tx_addr, rx_addr, bufsize, use_padding, False, None, False, q,))
        p.daemon = True
        p.start()
        time.sleep(1)
        s.send(data)

        data2 = q.get(timeout=10)
        p.join()

        assert data == data2

    def test_can_isotp_socket_with_extended_ids(self, can_interface):
        rx_addr = 0x18DA01FA
        tx_addr = 0x18DAFA01
        use_padding = False
        s = CanIsoTpSocket(interface=can_interface, rx_addr=rx_addr, tx_addr=tx_addr, use_padding=use_padding)
        data = bytes(range(64))
        bufsize = len(data)
        q = Queue()
        # Note: the receive thread logically has rx_addr, tx_addr inverted!
        p = Thread(target=receive_from_can_isotp_socket,
                   args=(can_interface, tx_addr, rx_addr, bufsize, use_padding, False, None, False, q,))
        p.daemon = True
        p.start()
        time.sleep(1)
        s.send(data)

        data2 = q.get(timeout=10)
        p.join()

        assert data == data2

    def test_can_isotp_socket_with_extended_ids_and_listenonly(self, can_interface):
        rx_addr = 0x18DA01FA
        tx_addr = 0x18DAFA01
        use_padding = False
        s = CanIsoTpSocket(interface=can_interface, rx_addr=rx_addr, tx_addr=tx_addr, use_padding=use_padding)
        data = bytes(range(64))
        bufsize = len(data)
        q = Queue()
        # Note: the receive thread logically has rx_addr, tx_addr inverted!
        p = Thread(target=receive_from_can_isotp_socket,
                   args=(can_interface, tx_addr, rx_addr, bufsize, use_padding, False, None, False, q,))
        p.daemon = True
        p.start()

        q2 = Queue()
        p2 = Thread(target=receive_from_can_isotp_socket,
                    args=(can_interface, tx_addr, rx_addr, bufsize, False, True, None, False, q2,))
        p2.setDaemon(True)
        p2.start()

        time.sleep(1)
        s.send(data)

        data2 = q.get(timeout=10)
        p.join()
        data3 = q2.get(timeout=10)
        p2.join()

        assert data == data2 == data3

    def test_can_isotp_socket_with_extended_ids_and_padding(self, can_interface):
        rx_addr = 0x18DA01FA
        tx_addr = 0x18DAFA01
        use_padding = True
        s = CanIsoTpSocket(interface=can_interface, rx_addr=rx_addr, tx_addr=tx_addr, use_padding=use_padding)
        data = bytes(range(64))
        bufsize = len(data)
        q = Queue()
        # Note: the receive thread logically has rx_addr, tx_addr inverted!
        p = Thread(target=receive_from_can_isotp_socket,
                   args=(can_interface, tx_addr, rx_addr, bufsize, use_padding, False, None, False, q,))
        p.daemon = True
        p.start()
        time.sleep(1)
        s.send(data)

        data2 = q.get(timeout=10)
        p.join()

        assert data == data2

    def test_should_fail_missing_flow_control_on_transfer(self, can_interface):
        rx_addr = 0x18DA01FA
        tx_addr = 0x18DAFA01
        s = CanIsoTpSocket(interface=can_interface, rx_addr=rx_addr, tx_addr=tx_addr)
        data = bytes(range(64))
        with pytest.raises(OSError):
            s.send(data)

    def test_should_fail_missing_flow_control_on_transfer_and_wait_tx(self, can_interface):
        rx_addr = 0x18DA01FA
        tx_addr = 0x18DAFA01
        s = CanIsoTpSocket(interface=can_interface, rx_addr=rx_addr, tx_addr=tx_addr, wait_tx_done=True)
        data = bytes(range(64))
        with pytest.raises(OSError):
            s.send(data)

    def test_fc_opt_stmin(self, can_interface):
        rx_addr = 0x18DA01FA
        tx_addr = 0x18DAFA01
        use_padding = True
        fc_stmin = 5
        s = CanIsoTpSocket(interface=can_interface, rx_addr=rx_addr, tx_addr=tx_addr, use_padding=use_padding,
                           fc_stmin=fc_stmin)
        data = bytes(range(64))
        bufsize = len(data)
        q = Queue()
        # Note: the receive thread logically has rx_addr, tx_addr inverted!
        p = Thread(target=receive_from_can_isotp_socket,
                   args=(can_interface, tx_addr, rx_addr, bufsize, use_padding, False, fc_stmin, False, q,))
        p.daemon = True
        p.start()
        time.sleep(1)
        s.send(data)

        data2 = q.get(timeout=10)
        p.join()

        assert data == data2

    def test_can_fd(self, can_interface):
        rx_addr = 0x18DA01FA
        tx_addr = 0x18DAFA01
        use_padding = True
        use_canfd = True
        s = CanIsoTpSocket(interface=can_interface, rx_addr=rx_addr, tx_addr=tx_addr, use_padding=use_padding,
                           use_canfd=use_canfd)
        data = bytes(range(256))
        bufsize = len(data)
        q = Queue()
        # Note: the receive thread logically has rx_addr, tx_addr inverted!
        p = Thread(target=receive_from_can_isotp_socket,
                   args=(can_interface, tx_addr, rx_addr, bufsize, use_padding, False, None, use_canfd, q,))
        p.daemon = True
        p.start()
        time.sleep(1)
        s.send(data)

        data2 = q.get(timeout=10)
        p.join()

        assert data == data2


@pytest.mark.skipif(not is_can_available(), reason="this test requires a can interface to be set up")
class TestCanBcmSocket:
    """
    A collection of tests for the BCM socket.
    """

    def test_bcm_msg_and_bcm_socket_send_operation(self, can_interface):
        s = CanBcmSocket(interface=can_interface)
        fileno = s.fileno()
        assert fileno
        can_id = 0x12345678
        data = bytes(range(0, 0x88, 0x11))
        frame1 = CanFrame(can_id=can_id,
                          data=data)
        opcode = BcmOpCodes.TX_SETUP
        flags = BCMFlags(BCMFlags.SETTIMER | BCMFlags.STARTTIMER)
        interval = 1
        frames = [frame1, ]
        bcm = BcmMsg(opcode=opcode,
                     flags=flags,
                     count=0,
                     interval1=0,
                     interval2=interval,
                     can_id=can_id,
                     frames=frames,
                     )
        q = Queue()
        p = Thread(target=receive_from_can_raw_socket, args=(can_interface, q,))
        p.daemon = True
        p.start()
        try:
            s.send(bcm)
        except OSError:
            assert False, "The length of bcm message is false. Length {0} Platform {1}".format(len(bcm.to_bytes()),
                                                                                               platform.machine())
        else:
            time.sleep(1)
            frame2 = q.get(timeout=10)
            p.join()

            assert frame1 == frame2

    def test_setup_cyclic_message_via_bcm(self, can_interface):
        interval = 0.5
        s = CanBcmSocket(interface=can_interface)
        can_id = 0x12345678
        data = bytes(range(0, 0x88, 0x11))
        frame = CanFrame(can_id=can_id,
                         data=data)

        s.setup_cyclic_transmit(frame=frame, interval=interval)

        q = Queue()
        p = Thread(target=receive_from_can_raw_socket, args=(can_interface, q,))
        p.daemon = True
        p.start()

        frame2 = q.get(timeout=interval)
        assert frame.can_id == frame2.can_id

        s.remove_all_cyclic_transmits()

        q2 = Queue()
        p2 = Thread(target=receive_from_can_raw_socket, args=(can_interface, q2,))
        p2.setDaemon(True)
        p2.start()
        with pytest.raises(Empty):
            q2.get(timeout=interval)

    def test_setup_cyclic_canfd_message_via_bcm(self, can_interface):
        interval = 0.5
        s = CanBcmSocket(interface=can_interface)
        can_id = 0x12345678
        data = bytes(range(0, 0x88, 0x11))
        frame = CanFdFrame(can_id=can_id,
                           data=data)

        s.setup_cyclic_transmit(frame=frame, interval=interval)

        q = Queue()
        p = Thread(target=receive_from_can_raw_socket, args=(can_interface, q,))
        p.daemon = True
        p.start()

        frame2 = q.get(timeout=interval)
        assert frame.can_id == frame2.can_id

        s.remove_all_cyclic_transmits()

        q2 = Queue()
        p2 = Thread(target=receive_from_can_raw_socket, args=(can_interface, q2,))
        p2.setDaemon(True)
        p2.start()
        with pytest.raises(Empty):
            q2.get(timeout=interval)

    def test_setup_receive_filter_and_read_filter_via_bcm(self, can_interface):
        interval = 0.5
        s = CanBcmSocket(interface=can_interface)
        can_id = 0x12345678
        data = bytes(range(0, 0x88, 0x11))
        frame = CanFrame(can_id=can_id,
                         data=data)

        s.setup_receive_filter(frame=frame, timeout=interval)

        # we do it wrong to trigger auto adding CAN_EFF_FLAG
        can_id = 0x12345678
        bcm = s.get_receive_filter(can_id=can_id)

        assert bcm.opcode == BcmOpCodes.RX_STATUS
        assert frame.can_id | frame.flags == bcm.can_id
        assert len(bcm.frames) == 1
        frame2 = bcm.frames[0]
        assert frame == frame2

    def test_should_fail_defect_recv_from_can_bcm_socket(self, can_interface):
        # create a cyclic message
        bcm_sock = CanBcmSocket(interface=can_interface)
        bcm_sock._s = MockSocket()
        assert bcm_sock.recv() is None

    def test_should_fail_defect_recv_from_can_raw_socket(self, can_interface):
        # create a raw message
        raw_sock = CanRawSocket(interface=can_interface)
        raw_sock._s = MockSocket()
        assert raw_sock.recv() is None

    def test_bcm_and_bcm_socket_receive_message_short_can_id(self, can_interface):
        # create a cyclic message
        interval = 0.5
        s1 = CanBcmSocket(interface=can_interface)
        can_id = 0x123
        data = bytes(range(0, 0x88, 0x11))
        frame1 = CanFrame(can_id=can_id,
                          data=data)

        q = Queue()
        p = Thread(target=receive_from_bcm_socket, args=(can_interface, can_id, interval, q))
        p.daemon = True

        s1.setup_cyclic_transmit(frame=frame1, interval=interval)

        frame1.data = bytes(range(8))
        s1.setup_cyclic_transmit(frame=frame1, interval=interval)

        p.start()

        rx_bcm = q.get(timeout=interval * 10)
        p.join()

        print("Received message from BCM")
        print("can_id {0:X} opcode {1} flags {2} nframes {3}".format(rx_bcm.can_id, rx_bcm.opcode, rx_bcm.flags,
                                                                     len(rx_bcm.frames)))
        if rx_bcm.frames:
            print("BCM message included a CAN Frame {0:X} {1} {2}".format(rx_bcm.frames[0].can_id,
                                                                          rx_bcm.frames[0].flags,
                                                                          rx_bcm.frames[0].data.hex()))
        assert rx_bcm.opcode == BcmOpCodes.RX_CHANGED
        assert frame1.can_id, frame1.flags == split_can_id_and_flags(rx_bcm.can_id)
        assert len(rx_bcm.frames) == 1
        frame2 = rx_bcm.frames[0]
        assert frame1 == frame2

    def test_bcm_and_bcm_socket_receive_message_long_can_id(self, can_interface):
        # create a cyclic message
        interval = 0.5
        s1 = CanBcmSocket(interface=can_interface)
        can_id = 0x123456FF
        data = bytes(range(0, 0x88, 0x11))
        frame1 = CanFrame(can_id=can_id,
                          data=data)

        q = Queue()
        p = Thread(target=receive_from_bcm_socket, args=(can_interface, can_id, interval, q))
        p.daemon = True

        s1.setup_cyclic_transmit(frame=frame1, interval=interval)
        p.start()

        rx_bcm = q.get(timeout=interval * 10)
        p.join()

        print("Received message from BCM")
        print("can_id {0:X} opcode {1} flags {2} nframes {3}".format(rx_bcm.can_id, rx_bcm.opcode, rx_bcm.flags,
                                                                     len(rx_bcm.frames)))
        if rx_bcm.frames:
            print("BCM message included a CAN Frame {0:X} {1} {2}".format(rx_bcm.frames[0].can_id,
                                                                          rx_bcm.frames[0].flags,
                                                                          rx_bcm.frames[0].data.hex()))

        assert rx_bcm.opcode == BcmOpCodes.RX_CHANGED
        assert frame1.can_id, frame1.flags == split_can_id_and_flags(rx_bcm.can_id)
        assert len(rx_bcm.frames) == 1
        frame2 = rx_bcm.frames[0]
        assert frame1 == frame2


@pytest.mark.skipif(not (is_can_available()
                         and is_j1939_available()),
                    reason="this test requires a can interface to be set up and j1939 kernel module, mainline kernel "
                           ">= 5.4")
class TestCanJ1939Socket:
    """
    A collection of tests for the j1939 socket.
    """

    def test_can_j1939_socket(self, can_interface):
        source_address = 0x20
        s = CanJ1939Socket(interface=can_interface, source_address=source_address)
        fileno = s.fileno()
        assert fileno
        data = bytes(range(8))
        pgn = 0xFECA
        dest = 0xFF

        q = Queue()
        p = Thread(target=receive_from_can_raw_socket, args=(can_interface, q,))
        p.daemon = True
        p.start()
        time.sleep(1)
        s.sendto(pgn=pgn, data=data, addr=dest)
        frame = q.get(timeout=10)
        p.join()

        assert frame.data == data
        assert frame.can_id == source_address + (pgn << 8) + (0x18 << 24)

    def test_can_j1939_recvfrom(self, can_interface):
        source_address = 0x20
        s = CanJ1939Socket(interface=can_interface, source_address=source_address)
        data = bytes(range(8))
        pgn = 0xFECA
        dest = 0xFF

        q = Queue()
        p = Thread(target=receive_from_j1939_socket, args=(can_interface, q,))
        p.daemon = True
        p.start()
        time.sleep(1)
        s.sendto(pgn=pgn, data=data, addr=dest)
        j1939_dict = q.get(timeout=10)
        p.join()
        LOGGER.info("{0}".format(j1939_dict))
        assert j1939_dict.get("data") == data
        assert j1939_dict.get("pgn") == pgn
