import belay

# Define your microcontroller connection (Update the port if needed)
DEVICE = "COM4"  # Change to your actual port
supervisor = belay.Device(DEVICE)

@supervisor.task
def monitor_buttons():
    from machine import Pin
    import time

    # Define button GPIO pins (Update these based on your wiring)
    BUTTON_PINS = [1, 5, 9, 17, 13, 21]  # Data pins for buttons

    # Initialize buttons as inputs with pull-up resistors
    buttons = [Pin(pin, Pin.IN, Pin.PULL_UP) for pin in BUTTON_PINS]

    while True:
        button_states = [0 if button.value() else 1 for button in buttons]  # Read button states
        print(button_states)  # Print the list of button states
        time.sleep(0.1)  # Debounce delay

monitor_buttons()  # Start monitoring
