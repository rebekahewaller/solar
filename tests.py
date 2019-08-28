import cc

# --------------------------------------------------
def test_init_load():
    """Docstring"""

    ser1 = cc.init_load(baud_rate=9600, port='COM3', timeout=1)
    ser2 = cc.init_load(baud_rate=500, port='COM1', timeout=3)

    assert ser1.baud_rate == 9600
    assert ser1.port == 'COM3'

