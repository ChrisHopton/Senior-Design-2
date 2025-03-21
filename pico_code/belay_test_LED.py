import belay

# ✅ Define your microcontroller connection (Update COM port if needed)
DEVICE = "COM6"  # Replace with your actual port (e.g., "COM5")
supervisor = belay.Device(DEVICE)

@supervisor.task
def ws2812_chase():
    import neopixel
    from machine import Pin
    import time

    LED_PIN = 27  # Change to your actual WS2812B data pin
    NUM_LEDS = 300  # Adjust based on your LED strip length
    BRIGHTNESS = 30  # Adjust brightness (1 - 100%)

    # ✅ Initialize WS2812B LED strip
    np = neopixel.NeoPixel(Pin(LED_PIN, Pin.OUT), NUM_LEDS)

    # ✅ Define colors for the chase effect
    colors = [
        (255, 0, 0),  # Red
        (0, 255, 0),  # Green
        (0, 0, 255),  # Blue
        (255, 255, 0),  # Yellow
        (0, 255, 255),  # Cyan
        (255, 0, 255)   # Magenta
    ]

    # ✅ Function to apply brightness scaling
    def apply_brightness(color, brightness):
        scale = brightness / 100  # Convert percentage to scale factor
        return (int(color[0] * scale), int(color[1] * scale), int(color[2] * scale))

    while True:
        for shift in range(NUM_LEDS):  # Loop through each LED position
            for i in range(NUM_LEDS):  # Set colors along the strip
                color_index = (i + shift) % len(colors)  # Cycle through colors
                np[i] = apply_brightness(colors[color_index], BRIGHTNESS)  # Apply brightness
            np.write()
            time.sleep(0.05)  # Adjust speed of chase effect

ws2812_chase()  # Run the LED chase effect