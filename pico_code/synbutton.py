import time
import mss
import numpy as np
import belay
import colorsys

# Define your microcontroller connection (update COM port if needed)
DEVICE = "COM4"  # Replace with your actual port
supervisor = belay.Device(DEVICE)

# Global chase effect configuration.
CHASE_COLORS = [
    (10, 10, 30),      # Void Black-Blue (deep space)
    (25, 25, 112),     # Midnight Blue (classic space tone)
    (75, 0, 130),      # Dark Indigo (nebula shadows)
    (47, 79, 79),      # Space Slate Gray (metallic asteroid hue)
    (70, 130, 180),    # Cold Starlight Blue (icy glint of far stars)
    (19, 24, 98),      # Dark Cosmic Blue (planetary shadow)
    (80, 0, 80),       # Distant Nebula Purple (low glow)
    (169, 169, 169)    # Dim Star Silver (subtle star shimmer)
]
CHASE_BRIGHTNESS = 100  # 100% brightness for the chase effect

@supervisor.task
def update_led(led_colors):
    """
    Runs on the Pico.
    Receives a list of (R, G, B) tuples (one per LED) and updates two WS2812B LED strips.
    In this version, both LED strips are reinitialized on every update.
    """
    import neopixel
    from machine import Pin
    # Define the data pins for each strip.
    LED_PIN1 = 26  # First LED strip on GPIO 26
    LED_PIN2 = 27  # Second LED strip on GPIO 27
    NUM_LEDS = len(led_colors)  # Number of LEDs per strip

    # Create neopixel objects for both LED strips.
    np_strip1 = neopixel.NeoPixel(Pin(LED_PIN1, Pin.OUT), NUM_LEDS)
    np_strip2 = neopixel.NeoPixel(Pin(LED_PIN2, Pin.OUT), NUM_LEDS)
    
    for i in range(NUM_LEDS):
        np_strip1[i] = led_colors[i]
        np_strip2[i] = led_colors[i]
    np_strip1.write()
    np_strip2.write()

@supervisor.task
def read_buttons():
    """
    Runs on the Pico.
    Reads the arcade button states once and returns a list.
    Each button is assumed to be connected with a pull-up resistor (0 = pressed, 1 = released).
    """
    from machine import Pin
    # Define the GPIO pins for your arcade buttons (adjust based on your wiring)
    BUTTON_PINS = [1, 5, 9, 17, 13, 21]
    buttons = [Pin(pin, Pin.IN, Pin.PULL_UP) for pin in BUTTON_PINS]
    button_states = [0 if button.value() else 1 for button in buttons] 
    return button_states

# The following functions remain available in case you need them later.
def capture_screen():
    """
    Captures the primary monitor's screenshot and returns it as a NumPy array in RGB format.
    """
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Primary monitor
        sct_img = sct.grab(monitor)
        img = np.array(sct_img)
        img = img[:, :, :3]
        img = img[..., ::-1]
        return img

def get_border_colors(img, border_thickness=20, segments_top=10, segments_bottom=10,
                      segments_left=10, segments_right=10):
    """
    Divides the image's borders into segments and computes an average RGB color for each.
    Returns a dictionary with keys "top", "bottom", "left", "right" mapping to lists of RGB tuples.
    """
    height, width, _ = img.shape
    result = {}

    # Top border
    top_border = img[0:border_thickness, :, :]
    seg_width_top = width // segments_top
    top_colors = []
    for i in range(segments_top):
        start = i * seg_width_top
        segment = top_border[:, start: width if i == segments_top - 1 else start + seg_width_top, :]
        avg_color = np.mean(segment.reshape(-1, 3), axis=0)
        top_colors.append(tuple(avg_color.astype(int)))
    result['top'] = top_colors

    # Bottom border
    bottom_border = img[height - border_thickness: height, :, :]
    seg_width_bottom = width // segments_bottom
    bottom_colors = []
    for i in range(segments_bottom):
        start = i * seg_width_bottom
        segment = bottom_border[:, start: width if i == segments_bottom - 1 else start + seg_width_bottom, :]
        avg_color = np.mean(segment.reshape(-1, 3), axis=0)
        bottom_colors.append(tuple(avg_color.astype(int)))
    result['bottom'] = bottom_colors

    # Left border
    left_border = img[:, 0:border_thickness, :]
    seg_height_left = height // segments_left
    left_colors = []
    for i in range(segments_left):
        start = i * seg_height_left
        segment = left_border[start: height if i == segments_left - 1 else start + seg_height_left, :, :]
        avg_color = np.mean(segment.reshape(-1, 3), axis=0)
        left_colors.append(tuple(avg_color.astype(int)))
    result['left'] = left_colors

    # Right border
    right_border = img[:, width - border_thickness: width, :]
    seg_height_right = height // segments_right
    right_colors = []
    for i in range(segments_right):
        start = i * seg_height_right
        segment = right_border[start: height if i == segments_right - 1 else start + seg_height_right, :, :]
        avg_color = np.mean(segment.reshape(-1, 3), axis=0)
        right_colors.append(tuple(avg_color.astype(int)))
    result['right'] = right_colors

    return result

def enhance_color_saturation(rgb, factor=1.5):
    """
    Increases the saturation of an RGB color by the given factor.
    """
    r, g, b = rgb
    r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
    h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
    s = min(s * factor, 1.0)
    r_new, g_new, b_new = colorsys.hsv_to_rgb(h, s, v)
    return (int(r_new * 255), int(g_new * 255), int(b_new * 255))

def map_border_colors_to_leds(border_colors, num_leds, saturation_factor=1.5):
    """
    Creates a full LED color list by concatenating the border segments and repeating until num_leds is reached.
    """
    colors_sequence = (border_colors['top'] +
                       border_colors['right'] +
                       border_colors['bottom'] +
                       border_colors['left'])
    num_segments = len(colors_sequence)
    led_colors = []
    for i in range(num_leds):
        base_color = colors_sequence[i % num_segments]
        enhanced_color = enhance_color_saturation(base_color, factor=saturation_factor)
        led_colors.append(enhanced_color)
    return led_colors

def apply_brightness(color, brightness):
    """
    Applies brightness scaling to a given color.
    """
    scale = brightness / 100.0
    return (int(color[0] * scale), int(color[1] * scale), int(color[2] * scale))

def get_chase_led_colors(num_leds, shift, brightness=CHASE_BRIGHTNESS):
    """
    Computes the LED colors for a chase effect.
    The 'shift' value creates the moving effect.
    """
    led_colors = []
    num_colors = len(CHASE_COLORS)
    for i in range(num_leds):
        color_index = (i + shift) % num_colors
        scaled_color = apply_brightness(CHASE_COLORS[color_index], brightness)
        led_colors.append(scaled_color)
    return led_colors

# Main loop: always use the chase effect as the default.
if __name__ == "__main__":
    NUM_LEDS = 300         # Must match your LED strip's count (per strip)
    UPDATE_INTERVAL = 0.1  # Seconds between updates
    chase_shift = 0        # Initialize the shift for the chase effect

    while True:
        # Always use the chase effect (ignoring border detection).
        led_colors = get_chase_led_colors(NUM_LEDS, chase_shift, brightness=CHASE_BRIGHTNESS)
        chase_shift = (chase_shift + 1) % len(CHASE_COLORS)

        update_led(led_colors)
        button_states = read_buttons()
        print("Button states:", button_states)

        time.sleep(UPDATE_INTERVAL)
