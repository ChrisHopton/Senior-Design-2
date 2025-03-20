import time
import mss
import numpy as np
import belay
import colorsys

# Define your microcontroller connection (update COM port if needed)
DEVICE = "COM6"  # Replace with your actual port (e.g., "COM5")
supervisor = belay.Device(DEVICE)

@supervisor.task
def update_led(led_colors):
    """
    This task runs on the Pico.
    It receives a list of (R, G, B) tuples (one per LED) and updates the WS2812B LED strip.
    In this version the LED strip is reinitialized on every update.
    """
    import neopixel
    from machine import Pin
    LED_PIN = 27       # Change to your actual WS2812B data pin
    NUM_LEDS = 300     # Adjust based on your LED strip length

    # Create a new neopixel object each call.
    np_strip = neopixel.NeoPixel(Pin(LED_PIN, Pin.OUT), NUM_LEDS)
    
    # Uncomment the next line if your LED strip expects GRB order:
    # led_colors = [(g, r, b) for (r, g, b) in led_colors]
    
    for i in range(NUM_LEDS):
        np_strip[i] = led_colors[i]
    np_strip.write()

def capture_screen():
    """
    Captures the primary monitor's screenshot and returns it as a NumPy array in RGB format.
    """
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Primary monitor
        sct_img = sct.grab(monitor)
        # The image is in BGRA format; drop the alpha channel and convert to RGB.
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
    The input rgb values are expected to be in the 0-255 range.
    """
    r, g, b = rgb
    # Normalize to [0,1]
    r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
    h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
    # Increase saturation by factor (capped at 1.0)
    s = min(s * factor, 1.0)
    r_new, g_new, b_new = colorsys.hsv_to_rgb(h, s, v)
    return (int(r_new * 255), int(g_new * 255), int(b_new * 255))

def map_border_colors_to_leds(border_colors, num_leds, saturation_factor=1.5):
    """
    Creates a full LED color list by concatenating the border segments (top, right, bottom, left)
    and repeating the sequence until the number of LEDs is reached.
    Each color is enhanced to increase its saturation.
    """
    colors_sequence = (border_colors['top'] +
                       border_colors['right'] +
                       border_colors['bottom'] +
                       border_colors['left'])
    num_segments = len(colors_sequence)
    led_colors = []
    for i in range(num_leds):
        # Enhance the saturation of each color before mapping
        base_color = colors_sequence[i % num_segments]
        enhanced_color = enhance_color_saturation(base_color, factor=saturation_factor)
        led_colors.append(enhanced_color)
    return led_colors

if __name__ == "__main__":
    NUM_LEDS = 300         # Must match your LED strip's count
    UPDATE_INTERVAL = 0.1  # Seconds between updates

    while True:
        img = capture_screen()
        border_colors = get_border_colors(
            img,
            border_thickness=20,   # Adjust for your monitor's border size
            segments_top=10,
            segments_bottom=10,
            segments_left=10,
            segments_right=10
        )
        led_colors = map_border_colors_to_leds(border_colors, NUM_LEDS, saturation_factor=1.5)
        update_led(led_colors)
        time.sleep(UPDATE_INTERVAL)
