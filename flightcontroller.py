import dji_matrix as djim
import logging
import logging.config
from datetime import datetime
import math

#------------------------- BEGIN HeadsUpTello CLASS ----------------------------

class HeadsUpTello():
    """
    An interface from Team "Heads-Up Flight" to control a DJI Tello RoboMaster 
    Drone. Uses djitellopy.Tello class as the base object.
    """

    def __init__(self, parameters, drone_object, debug_level=logging.INFO):
        """
        Constructor that establishes a connection with the drone. Pass in a
        djitellopy Tello object to give your HeadsUpTello object its wings.

        Arguments
            drone_object: A new djitellopy.Tello() object
            debug_level:  Set the desired logging level.
                          logging.INFO shows every command and response 
                          logging.WARN will only show problems
                          There are other possibilities, see logging module
        """

        self.name = parameters['name']
        self.mission = parameters['mission']

        self._setup_logging(debug_level)

        # HeadsUpTello class uses the design principal of composition (has-a)
        # instead of inheritance (is-a) so that we can choose between the real
        # drone and a simulator. If we had used inheritance, we would be forced
        # to choose one or the other.
        self.drone = drone_object
        self.drone.LOGGER.setLevel(debug_level)
        self.ceiling = parameters['ceiling']
        self.floor = parameters['floor']
        self.min_fly_battery = parameters['min_takeoff_power']
        self.min_op_battery = parameters['min_operating_power']

        try:
            self.drone.connect()
            self.connected = True
            self.logger.info(f"{self.name} connected to drone.")
        except Exception as excp:
            self.logger.error(f"ERROR: Could not connect to Tello Drone: {excp}")
            self.connected = False
            self.disconnect()
            raise

        self.initial_barometer = self.drone.get_barometer()
        self.home_coords = [0, 0]
        self.x, self.y = 0, 0
        self.rotation_angle = 0

        return
    
    def _setup_logging(self, debug_level):
        """ Set up the logging for the drone. """
        now = datetime.now().strftime("%Y%m%d.%H")
        logfile = f"Logs\\{self.mission}_{self.name}_{now}.log" # Test if folder works
        
        log_settings = {
            'version': 1,
            'disable_existing_loggers': False,
            'handlers': {
                'error_file_handler': {
                    'level': 'DEBUG',
                    'formatter': 'drone_errfile_fmt',
                    'class': 'logging.FileHandler',
                    'filename': logfile,
                    'mode': 'a',
                },
                'debug_console_handler': {
                    'level': 'WARNING',
                    'formatter': 'drone_stderr_fmt',
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stderr',
                },    
            },    
            'formatters': {
                'drone_errfile_fmt': {
                    'format': '%(asctime)s|%(levelname)s: %(message)s [%(name)s@%(filename)s.%(funcName)s.%(lineno)d]',
                    'datefmt': '%Y-%m-%dT%H:%M:%S'
                },
                'drone_stderr_fmt': {
                    'format': '%(levelname)s: %(message)s [%(name)s@%(filename)s.%(funcName)s.%(lineno)d]',
                },
            },
            'loggers': {
                'drone_logger': {
                    'handlers': ['debug_console_handler', 'error_file_handler'],
                    'level': 'DEBUG',
                    'propagate': False,
                },
            },
        }

        logging.config.dictConfig(log_settings)
        self.logger = logging.getLogger('drone_logger')

    def __del__(self):
        """ Destructor that gracefully closes the connection to the drone. """
        if self.connected:
            self.disconnect()
        return

    def disconnect(self):
        """ Gracefully close the connection with the drone. """
        self.logger.info(f"{self.name} connection closed gracefully.")
        self.drone.end()
        self.connected = False
        return
    
    def coords(self):
        """ Return coordinates of drone """
        return self.x, self.y
    
    def yaw(self):
        """ Return yaw of drone (rotation in degrees) """
        return self.drone.get_yaw()

    def get_battery(self):
        """ Returns the drone's battery level as a percent. """
        return self.drone.get_battery()

    def get_barometer(self):
        """
        Returns the drone's current barometer reading in cm from the ground.
        The accuracy of this reading fluctates with the weather. 
        """
        self.battery_check()

        return self.drone.get_barometer()

    def get_temperature(self):
        """ Returns the drone's internal temperature in °F. """
        return self.drone.get_temperature()
    
    def get_baro(self):
        """ Return drone barometer reading"""
        self.battery_check()

        self.logger.debug(f"Current barometer reading: {(self.drone.get_barometer() - self.initial_barometer)}cm")
        return (self.drone.get_barometer() - self.initial_barometer)
    
    def streamon(self):
        """ Turn on camera stream """
        self.drone.streamon()

    def get_frame_read(self):
        """ Get current frame of camera feed """
        return self.drone.get_frame_read()

    def height(self):
        """ Prints height of drone """
        return self.drone.get_height()
    
    def get_coordinates(self):
        """ Returns the current coordinates of drone """
        self.battery_check()

        return self.x, self.y
    
    def update_coordinates(self, dx, dy):
        """ Update drone coords based on where it is """
        self.x += dx
        self.y += dy

    def battery_check(self):
        """ Get battery percentage of drone and compare to mission parameters """
        if self.get_battery() < self.min_op_battery:
            self.logger.error(F"Battery too low. Landing")
            self.land()
        else:
            return

    # Used AI to help with some of the math portions
    def rotate_cw(self, degrees):
        """ Rotates  drone clockwise up to 180 degrees """
        self.battery_check()

        if degrees > 180:
            self.rotate_ccw((degrees-180))
            return

        degrees = int(degrees)
        
        # Update the rotation angle (ensuring it stays within the 0-360 range)
        self.rotation_angle = (self.rotation_angle + degrees) % 360
        
        self.drone.rotate_clockwise(degrees)
        self.logger.info(f"Rotated clockwise {degrees} to {self.rotation_angle}")
        return
    
    def rotate_ccw(self, degrees):
        """ Rotates  drone counterclockwise up to 180 degrees. """
        self.battery_check()

        if degrees > 180:
            self.rotate_cw((degrees-180))
            return

        degrees = int(degrees)
        
        # Update the rotation angle (ensuring it stays within the 0-360 range)
        self.rotation_angle = (self.rotation_angle - degrees) % 360     

        self.drone.rotate_counter_clockwise(degrees)
        self.logger.info(f"Rotated counterclockwise {degrees} to {self.rotation_angle}")
        return
    
    def takeoff(self):
        """ Prints battery charge then takes off """
        # Debugging tool
        if self.get_battery() > self.min_fly_battery:
            self.logger.debug(f"Battery good: {self.get_battery()}%")
        else:
            self.logger.error(f"Warning: Battery low: {self.get_battery()}% - Cannot take off.")
            return

        # Actual code
        self.logger.info(f"{self.name} is taking off")
        self.drone.takeoff()
        self.logger.info(f"{self.name} took off.")
        return

    def land(self):
        """ Lands drone """
        self.logger.info("Drone is landing")
        self.drone.land()
        self.logger.info(f"{self.name} has landed.")
        return
    
    def move(self, x, y, z, w):
        """ RC controls - used for pygame interface """
        
        self.battery_check()

        self.logger.info("Drone is moving")
        self.drone.send_rc_control(x, y, z, w)
        self.update_coordinates(x, y)

    def fly_up(self, distance, speed=20):
        """ Tell drone to fly up distance provided"""
        self.battery_check()

        self.drone.set_speed(speed)
        if self.ceiling - self.get_baro() <= 0:
            difference = (self.drone.get_height() + distance) - self.ceiling
            self.logger.warning(f"Cannot fly above ceiling. Command is {difference}cm above ceiling.")
            return
        else:
            self.logger.info(f"Flying up {distance}cm.")
            self.drone.move_up(distance)

    def fly_down(self, distance, speed=20):
        """ Tell drone to fly down distance provided"""
        self.battery_check()

        self.drone.set_speed(speed)
        if self.floor - self.get_baro() >= 0:
            difference = (self.drone.get_height() - distance) + self.floor
            self.logger.warning(f"Cannot fly below floor. Command is {difference}cm below floor.")
            return
        else:
            self.logger.info(f"Flying down {distance}cm.")
            self.drone.move_down(distance)

    def move_forward(self, distance, speed=20):
        """ Tell drone to fly forward distance provided"""
        self.battery_check()

        self.drone.set_speed(speed)
        
        # Get original distance for print
        od = distance

        # Convert angle to radians and do math to get new coordinates
        angle = math.radians(self.rotation_angle)
        dx = distance * math.cos(angle)
        dy = distance * math.sin(angle)

        while distance > 500:
            self.drone.move_forward(500)
            distance -= 500

        # Remainder
        if distance > 19:
            self.drone.move_forward(int(distance))
            self.update_coordinates(dy, dx)
        
        self.logger.info(f"Moved forward {od}cm, new coordinates: ({self.x}, {self.y})")

    def move_back(self, distance, speed=20):
        """ Tell drone to fly forward distance provided"""
        self.battery_check()

        self.drone.set_speed(speed)
        
        # Get original distance for print
        od = distance

        # Convert angle to radians and do math to get new coordinates
        angle = math.radians(self.rotation_angle)
        dx = -distance * math.cos(angle)
        dy = -distance * math.sin(angle)

        while distance > 500:
            self.drone.move_back(500)
            distance -= 500

        # Remainder
        if distance > 19:
            self.drone.move_back(int(distance))
            self.update_coordinates(dy, dx)
        
        self.logger.info(f"Moved back {od}cm, new coordinates: ({self.x}, {self.y})")

    def move_left(self, distance, speed=20):
        """ Tell drone to fly forward distance provided"""
        self.battery_check()

        self.drone.set_speed(speed)
        
        # Get original distance for print
        od = distance

        # Convert angle to radians and do math to get new coordinates
        angle = math.radians(self.rotation_angle + 90) # gpt said the +90 is to get the left direction
        dx = -distance * math.cos(angle)
        dy = -distance * math.sin(angle)

        while distance > 500:
            self.drone.move_left(500)
            distance -= 500

        # Remainder
        if distance > 19:
            self.drone.move_left(int(distance))
            self.update_coordinates(dx, dy)
        
        self.logger.info(f"Moved left {od}cm, new coordinates: ({self.x}, {self.y})")

    def move_right(self, distance, speed=20):
        """ Tell drone to fly forward distance provided"""
        self.battery_check()

        self.drone.set_speed(speed)
        
        # Get original distance for print
        od = distance

        # Convert angle to radians and do math to get new coordinates
        angle = math.radians(self.rotation_angle - 90) # gpt said the -90 is to get the right direction
        dx = distance * math.cos(angle)
        dy = distance * math.sin(angle)

        while distance > 500:
            self.drone.move_right(500)
            distance -= 500

        # Remainder
        if distance > 19:
            self.drone.move_right(int(distance))
            self.update_coordinates(dx, dy)
        
        self.logger.info(f"Moved right {od}cm, new coordinates: ({self.x}, {self.y})")

    def flip(self, direction):
        """ Have drone flip in any direction provided (f, b, r, l) """
        self.battery_check()

        self.drone.flip(direction)

    # gpt helped with a lot of the math
    def go_home(self, direct_flight=True, speed=20):
        """ Returns the drone home """
        self.battery_check()

        self.fly_to_coordinates(0, 0, direct_flight)

        # Rotate bearing back to original
        self.rotate_to_bearing(0)

        self.x = 0
        self.y = 0
        self.logger.info("Returned home.")

    def flyto_mission_ceiling(self, speed=20):
        """ Flies drone to mission ceiling"""
        self.battery_check()


        diff = self.ceiling - self.get_baro()

        time = diff//20

        for i in range(int(time)+1):
            self.drone.move_up(20)

        self.logger.info(f"Reached ceiling: {self.get_baro}")

    def flyto_mission_floor(self, speed=20):
        """ Flies drone to mission floor"""
        self.battery_check()

        diff = self.get_baro - self.floor

        time = diff//20

        for i in range(int(time)+1):
            self.drone.move_down(20)

        self.logger.info(f"Reached floor: {self.get_baro()}")

    def rotate_to_bearing(self, degrees):
        """ Rotates the drone to an absolute bearing (direction). """
        self.battery_check()

        # Calculate the difference in bearing
        difference = (degrees - self.rotation_angle) % 360
        
        # If difference is greater than 180, rotate the other way around
        if difference > 180:
            difference -= 360

        # Rotate clockwise or counterclockwise depending on the smallest angle
        if difference > 0:
            self.rotate_cw(abs(difference))
        elif difference < 0:
            self.rotate_ccw(abs(difference))

        # Update the current rotation angle
        self.rotation_angle = degrees
        self.logger.info(f"Rotated the bearing: {self.rotation_angle}")

    def fly_to_coordinates(self, x, y, direct_flight=False):
        """ Flies the drone to the coordinates (x, y). """
        self.battery_check()

        self.drone.set_speed(50)

        delta_x = x - self.x
        delta_y = y - self.y

        # Rotate
        if direct_flight:

            angle_to_target = math.degrees(math.atan2(delta_y, delta_x))
            
            # Rotate bearing towards point
            self.rotate_to_bearing(angle_to_target)

            # Calculate distance to the destination - used gpt for the math
            distance_to_target = math.hypot(delta_x, delta_y)

            self.move_forward(distance_to_target)
            self.x = x
            self.y = y

            self.logger.info(f"Moved directly to coordinates: ({self.x}, {self.y})")
            return
        
        # Don't rotate
        else:
            # Check which direction is further
            if abs(delta_x) > abs(delta_y):
                # Move along X first
                if delta_x != 0:
                    if delta_x > 0:
                        self.move_right(delta_x)
                    else:
                        self.move_left(abs(delta_x))
                
                # Then move along Y
                if delta_y != 0:
                    if delta_y > 0:
                        self.move_forward(delta_y)
                    else:
                        self.move_back(abs(delta_y))
            else:
                # Move along Y first
                if delta_y != 0:
                    if delta_y > 0:
                        self.move_forward(delta_y)
                    else:
                        self.move_back(abs(delta_y))

                # Then move along X
                if delta_x != 0:
                    if delta_x > 0:
                        self.move_right(delta_x)
                    else:
                        self.move_left(abs(delta_x))

            self.x = x
            self.y = y
            self.logger.info(f"Moved to coordinates: ({self.x}, {self.y})")

#------------------------- END OF HeadsUpTello CLASS ---------------------------