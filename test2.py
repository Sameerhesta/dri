from gpiozero import Buzzer
from time import sleep

buzzer = Buzzer(17)

while True:
	buzzer.beep()
	#buzzer.on()
	print("here", buzzer);
	sleep(1)
	#buzzer.off()
	#print("here", buzzer);
	#sleep(1)
