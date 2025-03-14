import machine
import utime
import random

# Setup LED on GPIO 2
led = machine.Pin(2, machine.Pin.OUT)

# Setup button on GPIO 3 (with internal pull-up resistor)
button = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)

best_time = None  # Variable to track the best reaction time

while True:
    # Wait a random time before turning the LED on
    wait_time = random.uniform(2, 5)  # Random delay before LED turns ON
    utime.sleep(wait_time)

    led.value(1)  # Turn LED ON (signal to react!)
    print("NOW! Slam the button!")

    start_time = utime.ticks_ms()  # Start timing the reaction
    button_pressed = False

    # Wait for up to 1.5 seconds for a button press
    while utime.ticks_diff(utime.ticks_ms(), start_time) < 1000:
        if button.value() == 0:  # Button is pressed
            reaction_time = utime.ticks_diff(utime.ticks_ms(), start_time)
            button_pressed = True

            # Update best reaction time
            if best_time is None or reaction_time < best_time:
                best_time = reaction_time  # New best time!

            print(f"Skibidi! Your reaction time: {reaction_time} ms | Best so far: {best_time} ms")
            utime.sleep(0.5)  # Small delay to prevent multiple triggers
            break  # Exit the waiting loop

    led.value(0)  # Turn LED OFF

    if not button_pressed:
        print("Too slow!")  # If you didn’t press fast enough

    # Wait before the next round
    utime.sleep(2)
