import pytest
import time

from feeder import Feeder
import j1939


# fmt: off
read_with_seed_key = [
    (Feeder.MsgType.CANTX, 0x18D9D4F9, [0x01, 0x13, 0x03, 0x00, 0x00, 0x92, 0x07, 0x00], 0.0), #DM14 read address 0x92000007
    (Feeder.MsgType.CANRX, 0x1CD8F9D4, [0x00, 0x11, 0xFF, 0xFF, 0xFF, 0xFF, 0x5A, 0xA5], 0.0), #DM15 seed response
    (Feeder.MsgType.CANTX, 0x18D9D4F9, [0x01, 0x13, 0x03, 0x00, 0x00, 0x92, 0xA5, 0x5A], 0.0), #DM14 key response
    (Feeder.MsgType.CANRX, 0x1CD8F9D4, [0x01, 0x11, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], 0.0), #DM15 proceed response
    (Feeder.MsgType.CANRX, 0x1CD7F9D4, [0x01, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], 0.0), #DM16 data transfer
    (Feeder.MsgType.CANRX, 0x1CD8F9D4, [0x00, 0x19, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], 0.0), #DM15 operation completed
    (Feeder.MsgType.CANTX, 0x18D9D4F9, [0x01, 0x19, 0x03, 0x00, 0x00, 0x92, 0xFF, 0xFF], 0.0), #DM14 operation completed
]

read_no_seed_key = [
    (Feeder.MsgType.CANTX, 0x18D9D4F9, [0x01, 0x13, 0x03, 0x00, 0x00, 0x92, 0x07, 0x00], 0.0), #DM14 read address 0x92000007
    (Feeder.MsgType.CANRX, 0x1CD8F9D4, [0x01, 0x11, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], 0.0), #DM15 proceed response
    (Feeder.MsgType.CANRX, 0x1CD7F9D4, [0x01, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], 0.0), #DM16 data transfer
    (Feeder.MsgType.CANRX, 0x1CD8F9D4, [0x00, 0x19, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], 0.0), #DM15 operation completed
    (Feeder.MsgType.CANTX, 0x18D9D4F9, [0x01, 0x19, 0x03, 0x00, 0x00, 0x92, 0xFF, 0xFF], 0.0), #DM14 operation completed
]
# fmt: on


def key_from_seed(seed):
    return seed ^ 0xFFFF


@pytest.mark.parametrize(
    argnames=["expected_messages"],
    argvalues=[[read_with_seed_key], [read_no_seed_key]],
    ids=["With seed key", "Without seed key"],
)
def test_dm14_read(feeder, expected_messages):
    feeder.can_messages = expected_messages
    feeder.pdus_from_messages()

    ca = feeder.accept_all_messages(
        device_address_preferred=0xF9, bypass_address_claim=True
    )

    dm14 = j1939.Dm14Query(ca)
    dm14.set_seed_key_algorithm(key_from_seed)
    dm14.read(0xD4, 1, 0x92000003, 1)

    feeder.process_messages()


# TODO: moar test
