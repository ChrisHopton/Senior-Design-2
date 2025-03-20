import argparse
from time import sleep
import belay

# Parse command-line arguments for the serial port.
parser = argparse.ArgumentParser()
# Set default to COM6 for Windows
parser.add_argument("--port", "-p", default="COM6", help="Serial port for the board")
args = parser.parse_args()

# Initialize the device connection.
device = belay.Device(args.port)

@device.thread
def led_chase():
    import neopixel
    from machine import Pin
    import time
    """
    Run a WS2812 LED chase effect continuously.
    """
    LED_PIN = 27       # Data pin for the WS2812 LED strip (adjust as needed)
    NUM_LEDS = 300     # Number of LEDs on your strip
    BRIGHTNESS = 30    # Brightness percentage (1-100%)
    
    # Initialize the LED strip.
    np = neopixel.NeoPixel(Pin(LED_PIN, Pin.OUT), NUM_LEDS)
    
    # Define the color palette for the chase effect.
    colors = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Yellow
        (0, 255, 255),  # Cyan
        (255, 0, 255)   # Magenta
    ]
    
    def apply_brightness(color, brightness):
        scale = brightness / 100.0
        return (int(color[0] * scale),
                int(color[1] * scale),
                int(color[2] * scale))
    
    shift = 0
    while True:
        # Update the LED colors based on the current shift value.
        for i in range(NUM_LEDS):
            color_index = (i + shift) % len(colors)
            np[i] = apply_brightness(colors[color_index], BRIGHTNESS)
        np.write()  # Refresh the LED strip
        shift = (shift + 1) % NUM_LEDS
        sleep(0.05)  # Short delay to yield control

@device.task
def read_buttons():
    from machine import Pin
    import time
    """
    Read the arcade button states and return a list of values.
    Each button is assumed to be connected with a pull-up resistor:
      - Returns 0 if pressed, 1 if released.
    """
    # Define the GPIO pins for your arcade buttons.
    BUTTON_PINS = [1, 5, 9, 17, 13, 21]
    
    # Initialize button inputs with pull-up resistors.
    buttons = [Pin(pin, Pin.IN, Pin.PULL_UP) for pin in BUTTON_PINS]
    
    # Read and return the button states.
    button_states = [0 if button.value() else 1 for button in buttons]
    return button_states

# Start the LED chase effect in the background.
led_chase()

# Main loop: periodically read button states and print them.
while True:
    states = read_buttons()
    print("Button states:", states)
    sleep(0.1)
