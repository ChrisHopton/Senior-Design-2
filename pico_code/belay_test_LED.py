import belay

# ✅ Define your microcontroller connection (Update COM port if needed)
DEVICE = "COM4"  # Replace with your actual port (e.g., "COM5")
supervisor = belay.Device(DEVICE)

@supervisor.task
def ws2812_chase():
    import neopixel
    from machine import Pin
    import time

    # Define LED strip pins and lengths.
    LED_PIN1 = 26  # First LED strip on GPIO 26
    LED_PIN2 = 27  # Second LED strip on GPIO 27
    NUM_LEDS_PER_STRIP = 66  # Each strip has 33 LEDs
    BRIGHTNESS = 50  # Adjust brightness (1 - 100%)

    # Initialize both WS2812B LED strips.
    np1 = neopixel.NeoPixel(Pin(LED_PIN1, Pin.OUT), NUM_LEDS_PER_STRIP)
    np2 = neopixel.NeoPixel(Pin(LED_PIN2, Pin.OUT), NUM_LEDS_PER_STRIP)

    # Define colors for the chase effect.
    colors = [
    (10, 10, 30),      # Void Black-Blue (deep space)
    (25, 25, 112),     # Midnight Blue (classic space tone)
    (75, 0, 130),      # Dark Indigo (nebula shadows)
    (47, 79, 79),      # Space Slate Gray (metallic asteroid hue)
    (70, 130, 180),    # Cold Starlight Blue (icy glint of far stars)
    (19, 24, 98),      # Dark Cosmic Blue (planetary shadow)
    (80, 0, 80),       # Distant Nebula Purple (low glow)
    (169, 169, 169)    # Dim Star Silver (subtle star shimmer)
]


    # Function to apply brightness scaling.
    def apply_brightness(color, brightness):
        scale = brightness / 100.0  # Convert percentage to scale factor
        return (int(color[0] * scale), int(color[1] * scale), int(color[2] * scale))

    # Chase effect: cycle through shifts for each LED position.
    while True:
        for shift in range(NUM_LEDS_PER_STRIP):
            for i in range(NUM_LEDS_PER_STRIP):
                # Cycle through colors for the chase effect.
                color_index = (i + shift) % len(colors)
                scaled_color = apply_brightness(colors[color_index], BRIGHTNESS)
                np1[i] = scaled_color
                np2[i] = scaled_color
            np1.write()
            np2.write()
            time.sleep(0.05)  # Adjust speed of the chase effect

ws2812_chase()  # Run the LED chase effect
