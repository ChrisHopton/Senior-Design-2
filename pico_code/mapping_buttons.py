# main.py
import time
import numpy as np
from pynput.keyboard import Controller
import synbutton as hw

# Initialize keyboard controller for simulating key presses.
keyboard = Controller()

# Mapping of button indices to key characters.
# Player One:   (Right monitor)
# Player Two:   (Left monitor)
button_to_key = {
    0: 'I',    # Up
    1: 'K',    # Down
    2: 'O',    # Shoot
    3: 'W',    # Up
    4: 'S',    # Down
    5: 'E'     # Shoot
}

# To track changes in button state.
previous_button_states = [0, 0, 0, 0, 0, 0]

def simulate_keys(new_states):
    """
    Compares new button states with previous states and simulates key presses/releases.
    Also prints the simulated key events to the console.
    """
    global previous_button_states
    for i, (prev, new) in enumerate(zip(previous_button_states, new_states)):
        if prev != new:
            key = button_to_key.get(i)
            if new == 1:
                keyboard.press(key)
                print(f"Simulated key press: {key}")
            else:
                keyboard.release(key)
                print(f"Simulated key release: {key}")
    previous_button_states = new_states.copy()

# Main loop configuration.
NUM_LEDS = 66         # Match your LED strip count per strip.
UPDATE_INTERVAL = 0.1  # Seconds between updates.
chase_shift = 0       # For the chase effect animation.

while True:
    # Capture screen and process border colors.
    img = hw.capture_screen()
    border_colors = hw.get_border_colors(
        img,
        border_thickness=20,
        segments_top=10,
        segments_bottom=10,
        segments_left=10,
        segments_right=10
    )
    led_colors_border = hw.map_border_colors_to_leds(border_colors, NUM_LEDS, saturation_factor=1.5)
    avg_brightness = np.mean([sum(color) for color in led_colors_border])
    
    # Decide between border-based colors or a chase effect.
    if avg_brightness < hw.DETECTION_THRESHOLD:
        led_colors = hw.get_chase_led_colors(NUM_LEDS, chase_shift, brightness=hw.CHASE_BRIGHTNESS)
        chase_shift = (chase_shift + 1) % len(hw.CHASE_COLORS)
    else:
        led_colors = led_colors_border

    # Update the LED strips.
    hw.update_led(led_colors)
    
    # Read the button states and simulate key presses.
    button_states = hw.read_buttons()
    print("Button states:", button_states)
    simulate_keys(button_states)

    time.sleep(UPDATE_INTERVAL)