import pygame
from djitellopy import Tello
from flightcontroller import HeadsUpTello
import threading
import queue
import cv2

# Initialize Pygame
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 720
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Initialize common colors
COLOR_GREEN = (64, 255, 64)
background_color = (33, 29, 30)

# Initialize font for placing text on the screen
font = pygame.font.Font('freesansbold.ttf', 24)

# Make an all black surface (black is default color: 0,0,0)
background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
background.fill(background_color)

# Initialize our opening screen logo
logo_surface = pygame.image.load('logo.jpg')
logo_rect = logo_surface.get_rect()
logo_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
show_logo = True

# Initialize if there has been takeoff
t = False

# Velocities
xv = 0
yv = 0
zv = 0
wv = 0

# Flag to track if a flip is in progress
flip_in_progress = False

# Flag to track if landing or takeoff is in progress
t_in_progress = False

mission_params = {
    'mission': 'Drone Race',
    'name': 'hawk',
    'min_takeoff_power': 30,
    'min_operating_power': 20,
    'ceiling': 10000,
    'floor': -10000,
}

# Connect to drone
tello = Tello()
hawk = HeadsUpTello(mission_params, tello)
hawk.battery_check()

# Get drone's video stream
hawk.streamon()

def camera_thread():
    """ Thread function to continuously update the camera frame """
    while True:
        frame = hawk.get_frame_read().frame
        if frame is not None:
            # Rotate frame to match display
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            # Put the frame in the queue (overwrite old frame if queue is full)
            if frame_queue.full():
                frame_queue.get()
            frame_queue.put(frame)

def perform_flip(direction):
    """ Perform a flip """
    global flip_in_progress
    if not flip_in_progress:
        flip_in_progress = True
        hawk.flip(direction)
        flip_in_progress = False

# Landing and takeoff separate because of t variable
def takeoff():
    """ Perform takeoff """
    global t_in_progress
    if not t_in_progress:
        t_in_progress = True
        hawk.takeoff()
        t_in_progress = False

def land():
    """ Perform landing """
    global t_in_progress
    if not t_in_progress:
        t_in_progress = True
        hawk.land()
        t_in_progress = False

# Shared queue for camera frames
frame_queue = queue.Queue(maxsize=1)  # Limit queue size to avoid lag

# Start the camera thread
camera_thread = threading.Thread(target=camera_thread, daemon=True)
camera_thread.start()

# Load keyboard overlay images
KEY_SIZE = (50, 50)

# Define key images with both default and pressed states
key_images = {
    'w': {
        'default': pygame.transform.scale(pygame.image.load('Keys\\w_w.png').convert_alpha(), KEY_SIZE),
        'pressed': pygame.transform.scale(pygame.image.load('Keys\\w_b.png').convert_alpha(), KEY_SIZE),
    },
    'a': {
        'default': pygame.transform.scale(pygame.image.load('Keys\\a_w.png').convert_alpha(), KEY_SIZE),
        'pressed': pygame.transform.scale(pygame.image.load('Keys\\a_b.png').convert_alpha(), KEY_SIZE),
    },
    's': {
        'default': pygame.transform.scale(pygame.image.load('Keys\\s_w.png').convert_alpha(), KEY_SIZE),
        'pressed': pygame.transform.scale(pygame.image.load('Keys\\s_b.png').convert_alpha(), KEY_SIZE),
    },
    'd': {
        'default': pygame.transform.scale(pygame.image.load('Keys\\d_w.png').convert_alpha(), KEY_SIZE),
        'pressed': pygame.transform.scale(pygame.image.load('Keys\\d_b.png').convert_alpha(), KEY_SIZE),
    },
    'q': {
        'default': pygame.transform.scale(pygame.image.load('Keys\\q_w.png').convert_alpha(), KEY_SIZE),
        'pressed': pygame.transform.scale(pygame.image.load('Keys\\q_b.png').convert_alpha(), KEY_SIZE),
    },
    'e': {
        'default': pygame.transform.scale(pygame.image.load('Keys\\e_w.png').convert_alpha(), KEY_SIZE),
        'pressed': pygame.transform.scale(pygame.image.load('Keys\\e_b.png').convert_alpha(), KEY_SIZE),
    },
    'up': {
        'default': pygame.transform.scale(pygame.image.load('Keys\\up_w.png').convert_alpha(), KEY_SIZE),
        'pressed': pygame.transform.scale(pygame.image.load('Keys\\up_b.png').convert_alpha(), KEY_SIZE),
    },
    'down': {
        'default': pygame.transform.scale(pygame.image.load('Keys\\down_w.png').convert_alpha(), KEY_SIZE),
        'pressed': pygame.transform.scale(pygame.image.load('Keys\\down_b.png').convert_alpha(), KEY_SIZE),
    },
    'space': {
        'default': pygame.transform.scale(pygame.image.load('Keys\\space_w.png').convert_alpha(), KEY_SIZE),
        'pressed': pygame.transform.scale(pygame.image.load('Keys\\space_b.png').convert_alpha(), KEY_SIZE),
    },
    'shift': {
        'default': pygame.transform.scale(pygame.image.load('Keys\\shift_w.png').convert_alpha(), KEY_SIZE),
        'pressed': pygame.transform.scale(pygame.image.load('Keys\\shift_b.png').convert_alpha(), KEY_SIZE),
    },
    '1': {
        'default': pygame.transform.scale(pygame.image.load('Keys\\1_w.png').convert_alpha(), KEY_SIZE),
        'pressed': pygame.transform.scale(pygame.image.load('Keys\\1_b.png').convert_alpha(), KEY_SIZE),
    },
    '2': {
        'default': pygame.transform.scale(pygame.image.load('Keys\\2_w.png').convert_alpha(), KEY_SIZE),
        'pressed': pygame.transform.scale(pygame.image.load('Keys\\2_b.png').convert_alpha(), KEY_SIZE),
    },
    '3': {
        'default': pygame.transform.scale(pygame.image.load('Keys\\3_w.png').convert_alpha(), KEY_SIZE),
        'pressed': pygame.transform.scale(pygame.image.load('Keys\\3_b.png').convert_alpha(), KEY_SIZE),
    },
    '4': {
        'default': pygame.transform.scale(pygame.image.load('Keys\\4_w.png').convert_alpha(), KEY_SIZE),
        'pressed': pygame.transform.scale(pygame.image.load('Keys\\4_b.png').convert_alpha(), KEY_SIZE),
    },
}

# Define positions for the keys (adjust as needed)
key_positions = {
    'w': (SCREEN_WIDTH // 2 - 400, SCREEN_HEIGHT - 100),
    'a': (SCREEN_WIDTH // 2 - 450, SCREEN_HEIGHT - 50),
    's': (SCREEN_WIDTH // 2 - 400, SCREEN_HEIGHT - 50),
    'd': (SCREEN_WIDTH // 2 - 350, SCREEN_HEIGHT - 50),
    'q': (SCREEN_WIDTH // 2 - 450, SCREEN_HEIGHT - 100),
    'e': (SCREEN_WIDTH // 2 - 350, SCREEN_HEIGHT - 100),
    'up': (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100),
    'down': (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 50),
    'space': (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50),
    'shift': (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 150),
    '1': (SCREEN_WIDTH // 2 - 450, SCREEN_HEIGHT - 150),
    '2': (SCREEN_WIDTH // 2 - 400, SCREEN_HEIGHT - 150),
    '3': (SCREEN_WIDTH // 2 - 350, SCREEN_HEIGHT - 150),
    '4': (SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT - 150),
}

# Initialize pressed keys set
pressed_keys = set()

# Initialize a dictionary to track the key states (default or pressed)
key_states = {key: 'default' for key in key_images}

# Key presses
W = False
S = False
A = False
D = False
PU = False
PD = False
Q = False
E = False

# Run the game loop
running = True
while running:
    # Cycle through all of the current events
    for event in pygame.event.get():
        # User clicked the X to close program
        if event.type == pygame.QUIT:
            running = False

        # Special one-time keys: SPACE -> 'boom' and ESC -> Quit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                show_logo = not show_logo
            if event.key == pygame.K_ESCAPE:
                running = False

        # Mark the key as pressed when it's pressed down
            if event.key == pygame.K_w:
                pressed_keys.add('w')
                key_states['w'] = 'pressed'
            elif event.key == pygame.K_a:
                pressed_keys.add('a')
                key_states['a'] = 'pressed'
            elif event.key == pygame.K_s:
                pressed_keys.add('s')
                key_states['s'] = 'pressed'
            elif event.key == pygame.K_d:
                pressed_keys.add('d')
                key_states['d'] = 'pressed'
            elif event.key == pygame.K_q:
                pressed_keys.add('q')
                key_states['q'] = 'pressed'
            elif event.key == pygame.K_e:
                pressed_keys.add('e')
                key_states['e'] = 'pressed'
            elif event.key == pygame.K_UP:
                pressed_keys.add('up')
                key_states['up'] = 'pressed'
            elif event.key == pygame.K_DOWN:
                pressed_keys.add('down')
                key_states['down'] = 'pressed'
            elif event.key == pygame.K_SPACE:
                pressed_keys.add('space')
                key_states['space'] = 'pressed'
            elif event.key == pygame.K_RSHIFT:
                pressed_keys.add('shift')
                key_states['shift'] = 'pressed'
            elif event.key == pygame.K_1:
                pressed_keys.add('1')
                key_states['1'] = 'pressed'
            elif event.key == pygame.K_2:
                pressed_keys.add('2')
                key_states['2'] = 'pressed'
            elif event.key == pygame.K_3:
                pressed_keys.add('3')
                key_states['3'] = 'pressed'
            elif event.key == pygame.K_4:
                pressed_keys.add('4')
                key_states['4'] = 'pressed'

        # Remove the key from pressed_keys set and update key states when it's released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                pressed_keys.discard('w')
                key_states['w'] = 'default'
            elif event.key == pygame.K_a:
                pressed_keys.discard('a')
                key_states['a'] = 'default'
            elif event.key == pygame.K_s:
                pressed_keys.discard('s')
                key_states['s'] = 'default'
            elif event.key == pygame.K_d:
                pressed_keys.discard('d')
                key_states['d'] = 'default'
            elif event.key == pygame.K_q:
                pressed_keys.discard('q')
                key_states['q'] = 'default'
            elif event.key == pygame.K_e:
                pressed_keys.discard('e')
                key_states['e'] = 'default'
            elif event.key == pygame.K_UP:
                pressed_keys.discard('up')
                key_states['up'] = 'default'
            elif event.key == pygame.K_DOWN:
                pressed_keys.discard('down')
                key_states['down'] = 'default'
            elif event.key == pygame.K_SPACE:
                pressed_keys.discard('space')
                key_states['space'] = 'default'
            elif event.key == pygame.K_RSHIFT:
                pressed_keys.discard('shift')
                key_states['shift'] = 'default'
            elif event.key == pygame.K_1:
                pressed_keys.discard('1')
                key_states['1'] = 'default'
            elif event.key == pygame.K_2:
                pressed_keys.discard('2')
                key_states['2'] = 'default'
            elif event.key == pygame.K_3:
                pressed_keys.discard('3')
                key_states['3'] = 'default'
            elif event.key == pygame.K_4:
                pressed_keys.discard('4')
                key_states['4'] = 'default'

    # Update the key images based on the current key states
    for key in key_images:
        if key_states[key] == 'pressed':
            key_images[key] = pygame.transform.scale(pygame.image.load(f'Keys\\{key}_b.png').convert_alpha(), KEY_SIZE)
        else:
            key_images[key] = pygame.transform.scale(pygame.image.load(f'Keys\\{key}_w.png').convert_alpha(), KEY_SIZE)

    # Capture all of the simultaneously pressed keys
    keys = pygame.key.get_pressed()

    # Takeoff / land
    if t == False:
        if keys[pygame.K_RSHIFT]:
            threading.Thread(target=takeoff()).start()
            t = True
    else:
        if keys[pygame.K_RSHIFT]:
            threading.Thread(target=land()).start()
            t = False

    if t == True:

        # flips
        if keys[pygame.K_1]:
            threading.Thread(target=perform_flip, args=("f",)).start()
        elif keys[pygame.K_2]:
            threading.Thread(target=perform_flip, args=("b",)).start()
        elif keys[pygame.K_3]:
            threading.Thread(target=perform_flip, args=("r",)).start()
        elif keys[pygame.K_4]:
            threading.Thread(target=perform_flip, args=("l",)).start()

        # Up down
        if keys[pygame.K_UP] and keys[pygame.K_DOWN]:
            PU = True
            PD = True
            zv = 0
        elif keys[pygame.K_UP]:
            if hawk.ceiling - (hawk.get_baro() + 20) >= 0:  # ceiling
                PU = True
                zv = 100
            else:
                print("Uh oh")  # needed this else
        elif keys[pygame.K_DOWN]:
            if hawk.floor - (hawk.get_baro() + 20) <= 0:  # floor
                PD = True
                zv = -100
            else:
                print("Uh oh")  # needed this else
        else:
            PU = False
            PD = False
            zv = 0

        # Rotate
        if keys[pygame.K_q] and keys[pygame.K_e]:
            Q = True
            E = True
            wv = 0
        elif keys[pygame.K_q]:
            Q = True
            wv = -100
        elif keys[pygame.K_e]:
            E = True
            wv = 100
        else:
            Q = False
            E = False
            wv = 0

        # Forward and back
        if keys[pygame.K_w] and keys[pygame.K_s]:
            W = True
            S = True
            yv = 0
        elif keys[pygame.K_w]:
            W = True
            yv = 100
        elif keys[pygame.K_s]:
            S = True
            yv = -100
        else:
            W = False
            S = False
            yv = 0

        # Right and left
        if keys[pygame.K_d] and keys[pygame.K_a]:
            D = True
            A = True
            xv = 0
        elif keys[pygame.K_d]:
            D = True
            xv = 100
        elif keys[pygame.K_a]:
            A = True
            xv = -100
        else:
            D = False
            A = False
            xv = 0

        # Make nicer
        try:
            hawk.move(xv, yv, zv, wv)
        except:
            print("Unable to move")

    # Place surfaces on the screen but don't display them (order matters)
    screen.blit(background, (0, 0))

    if show_logo:
        screen.blit(logo_surface, logo_rect)
    else:
        # Get the latest frame from the queue
        if not frame_queue.empty():
            frame = frame_queue.get()
            # Convert the frame to a Pygame surface
            webcam_surface = pygame.surfarray.make_surface(frame)
            webcam_rect = webcam_surface.get_rect()
            webcam_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            screen.blit(webcam_surface, webcam_rect)

    # Coords and degrees
    x, y = hawk.coords()
    coords = f"Rotation = {round(hawk.yaw())}°"
    coords_surface = font.render(coords, True, COLOR_GREEN)
    coords_rect = coords_surface.get_rect()
    coords_rect.topright = (960, 0)
    screen.blit(coords_surface, coords_rect)

    # Height
    height = hawk.height()
    h = f"Height = {round(height, 2)}cm"
    hs = font.render(h, True, COLOR_GREEN)
    hr = hs.get_rect()
    hr.topright = (960, 25)
    screen.blit(hs, hr)

    # Baro
    barometer = hawk.get_baro()
    b = f"Baro = {round(barometer, 2)}cm"
    bs = font.render(b, True, COLOR_GREEN)
    br = bs.get_rect()
    br.topright = (960, 50)
    screen.blit(bs, br)

    # Battery
    battery = hawk.get_battery()
    bat = f"{battery}%"
    b_surface = font.render(bat, True, COLOR_GREEN)
    b_rect = b_surface.get_rect()
    b_rect.topleft = (0, 0)
    screen.blit(b_surface, b_rect)

    # Temp
    temp = hawk.get_temperature()
    temperature = f"{temp}°F"
    t_surface = font.render(temperature, True, COLOR_GREEN)
    t_rect = t_surface.get_rect()
    t_rect.topleft = (0, 25)
    screen.blit(t_surface, t_rect)

    # Place key images on the screen (keyboard overlay)
    for key, image in key_images.items():
        screen.blit(image, key_positions[key])

    # Draw the current frame on the screen
    pygame.display.update()

    # Set a consistent speed that is reasonable and matches our camera
    clock.tick(30)

# Close down everything
hawk.land()
hawk.disconnect()
pygame.quit()