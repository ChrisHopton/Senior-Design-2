from neopixel import Neopixel
import utime

numpix = 300
strip = Neopixel(numpix, 0, 0, "GRB")
color = (255, 0, 255)  
strip.brightness(100)

# Main loop
while True:
    strip.fill(color)  
    strip.show()
   