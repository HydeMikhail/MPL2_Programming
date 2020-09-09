# MPL2_Programming

Main Program to coordinate temperature calibration with MPL2
driver board.

PHYSICAL GPIO:
37 - 3.3 V   (VDD) ::: Provides power to PIC
6 - GND      (GND) ::: Provides ground to PIC
7 - GPIO     (VPP) ::: Used to signal start of programming procedure
8 - Tx       (CLK) ::: Transmit Pin
10 - Rx      (DAT) ::: Receive Pin

11 - GPIO (OUT)    ::: Pass LED (GREEN)
12 - GPIO (OUT)    ::: Idle LED (RED)

13 - GPIO (IN)     ::: Trigger Calibration Button
15 - GPIO (IN)     ::: Close Application Button

The Pi is integrated with a fixture including 5 pins to interface
with the MPL2 driver board, 2 indicator LEDs, and two buttons to
trigger programming and exit the application.

When the board is interfaced with the fixture/pi and the trigger button
is pressed the Pi provides power to the PIC and pulls VPP low, indicating
to the PIC that a temperature calibration procedure should be started. The
PIC then takes 32 temperature readings, averages those values, and sends an
ASCII value to the Pi via UART. This program receives that value and passes
it through a model, which was determined experimentally, that calcuates the
expected value at 80 C based on the room temperature reading. The Pi will then
send that value back to the PIC, which will store that value in it's memory.

To verify this process, the PIC will then send back a checksum to confirm that
the value it received is correct. At this point, the green LED will turn on to
show the operator that the process was successful. If, at any point, there is an
issue, the red idle LED will flash to indicate the issue.