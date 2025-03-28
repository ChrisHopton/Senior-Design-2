import time
import mss
import numpy as np
import belay
import colorsys

# ✅ Define your microcontroller connection (update COM port if needed)
DEVICE = "COM4"  # Replace with your actual port
supervisor = belay.Device(DEVICE)

NUM_LEDS_PER_STRIP = 66
NUM_LEDS_TOTAL = NUM_LEDS_PER_STRIP * 2
UPDATE_INTERVAL = 0  # Seconds between updates

@supervisor.task
def update_led_1(led_colors):
    """
    Updates LED strip 1 (66 LEDs) on GPIO 26.
    """
    import neopixel
    from machine import Pin
    LED_PIN = 26
    NUM_LEDS = 66

    np_strip = neopixel.NeoPixel(Pin(LED_PIN, Pin.OUT), NUM_LEDS)
    for i in range(NUM_LEDS):
        np_strip[i] = led_colors[i]
    np_strip.write()

@supervisor.task
def update_led_2(led_colors):
    """
    Updates LED strip 2 (66 LEDs) on GPIO 27.
    """
    import neopixel
    from machine import Pin
    LED_PIN = 27
    NUM_LEDS = 66

    np_strip = neopixel.NeoPixel(Pin(LED_PIN, Pin.OUT), NUM_LEDS)
    for i in range(NUM_LEDS):
        np_strip[i] = led_colors[i]
    np_strip.write()

@supervisor.task
def read_buttons():
    from machine import Pin
    BUTTON_PINS = [1, 5, 9, 17, 13, 21]
    buttons = [Pin(pin, Pin.IN, Pin.PULL_UP) for pin in BUTTON_PINS]
    return [0 if button.value() else 1 for button in buttons]

def capture_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        img = np.array(sct_img)[:, :, :3][..., ::-1]  # Convert BGRA to RGB
        return img

def get_border_colors(img, border_thickness=20, segments_top=10, segments_bottom=10,
                      segments_left=10, segments_right=10):
    height, width, _ = img.shape
    result = {}

    def segment_colors(border, axis_segments, is_vertical=False):
        seg_size = border.shape[1] // axis_segments if not is_vertical else border.shape[0] // axis_segments
        colors = []
        for i in range(axis_segments):
            start = i * seg_size
            if i == axis_segments - 1:
                segment = border[:, start:] if not is_vertical else border[start:, :]
            else:
                segment = border[:, start:start + seg_size] if not is_vertical else border[start:start + seg_size, :]
            avg_color = np.mean(segment.reshape(-1, 3), axis=0)
            colors.append(tuple(avg_color.astype(int)))
        return colors

    top_border = img[0:border_thickness, :, :]
    bottom_border = img[height - border_thickness: height, :, :]
    left_border = img[:, 0:border_thickness, :]
    right_border = img[:, width - border_thickness: width, :]

    result['top'] = segment_colors(top_border, segments_top)
    result['bottom'] = segment_colors(bottom_border, segments_bottom)
    result['left'] = segment_colors(left_border, segments_left, is_vertical=True)
    result['right'] = segment_colors(right_border, segments_right, is_vertical=True)

    return result

def enhance_color_saturation(rgb, factor=1.5):
    r, g, b = rgb
    r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
    h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
    s = min(s * factor, 1.0)
    r_new, g_new, b_new = colorsys.hsv_to_rgb(h, s, v)
    return (int(r_new * 255), int(g_new * 255), int(b_new * 255))

def map_border_colors_to_leds(border_colors, num_leds, saturation_factor=1.5):
    colors_sequence = (border_colors['top'] +
                       border_colors['right'] +
                       border_colors['bottom'] +
                       border_colors['left'])
    led_colors = []
    for i in range(num_leds):
        base_color = colors_sequence[i % len(colors_sequence)]
        led_colors.append(enhance_color_saturation(base_color, factor=saturation_factor))
    return led_colors

# ✅ Main loop
if __name__ == "__main__":
    while True:
        img = capture_screen()
        border_colors = get_border_colors(img)
        led_colors = map_border_colors_to_leds(border_colors, NUM_LEDS_TOTAL)

        # Split into two 66-LED segments
