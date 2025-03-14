import machine
import utime
import random

# Setup LED on GPIO 2 (so we can turn it on/off)
led = machine.Pin(2, machine.Pin.OUT)

# Setup button on GPIO 3 (with internal pull-up resistor)
button = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)

while True:
    # Wait for a random time before turning the LED on
    wait_time = random.uniform(1, 3)  # Random delay before LED turns ON
    utime.sleep(wait_time)

    led.value(1)  # Turn LED ON
    skibidi_count = 0  # Reset Skibidi score for this round

    # Set a random ON duration before the LED turns OFF
    led_on_time = random.uniform(1, 4)  # Random LED ON duration (1 to 4 sec)
    start_time = utime.ticks_ms()

    while utime.ticks_diff(utime.ticks_ms(), start_time) < led_on_time * 1000:
        if button.value() == 0:  # Button is pressed
            skibidi_count += 1  # Increase score
            print("Skibidi")  # Print Skibidi when button is pressed
            utime.sleep(0.2)  # Debounce delay

    led.value(0)  # Turn LED OFF
    print(f"Skibidi Score: {skibidi_count}")  # Print total score for this round

    # Wait a short random delay before restarting the game
    utime.sleep(random.uniform(1, 2))
