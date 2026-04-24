from vex import *
import urandom
import math

# ----------------------------
# Robot Configuration
# ----------------------------

brain = Brain()
controller_1 = Controller(PRIMARY)

# Motors
right_motor = Motor(Ports.PORT2, GearSetting.RATIO_18_1, True)
left_motor = Motor(Ports.PORT10, GearSetting.RATIO_18_1, False)
claw_motor = Motor(Ports.PORT6, GearSetting.RATIO_18_1, True)
arm_motor = Motor(Ports.PORT5, GearSetting.RATIO_18_1, False)

# Settings
speed_multiplier = 0.5

# Arm preset positions
ARM_HIGH = 566
ARM_MID = 355
ARM_LOW = 90
ARM_RESET = 0

# ----------------------------
# Setup
# ----------------------------

wait(30, MSEC)

def initialize_random_seed():
    wait(100, MSEC)
    seed = brain.battery.voltage(MV)
    seed += brain.battery.current(CurrentUnits.AMP) * 100
    seed += brain.timer.system_high_res()
    urandom.seed(int(seed))

initialize_random_seed()

# Motor stopping modes
arm_motor.set_stopping(HOLD)
claw_motor.set_stopping(HOLD)

# Arm speed for spin_to_position
arm_motor.set_velocity(30, PERCENT)

# IMPORTANT:
# This does NOT move the arm.
# It just says the current physical position is 0 degrees.
# Start the robot with the arm physically down.
arm_motor.set_position(0, DEGREES)

# Clear console
wait(200, MSEC)
print("\033[2J")

# ----------------------------
# Auto Claw Helpers
# ----------------------------

def open_claw_auto():
    claw_motor.spin_for(FORWARD, 90, DEGREES)

def close_claw_auto():
    claw_motor.spin_for(REVERSE, 90, DEGREES)

# ----------------------------
# Driver Control
# ----------------------------

def user_control():
    current_target = 0
    was_manual_arm = False

    brain.screen.clear_screen()
    brain.screen.print("Driver Control Started")

    while True:
        # ----------------------------
        # Debug Screen
        # ----------------------------

        brain.screen.set_cursor(1, 1)
        brain.screen.print("ARM TORQUE: " + str(round(arm_motor.torque(TorqueUnits.NM), 2)) + "   ")

        brain.screen.set_cursor(2, 1)
        brain.screen.print("ARM DEG: " + str(int(arm_motor.position(DEGREES))) + "      ")

        # ----------------------------
        # Drivetrain
        # ----------------------------

        forward = controller_1.axis3.position() * speed_multiplier
        turn = controller_1.axis1.position() * speed_multiplier

        left_motor.spin(FORWARD, forward + turn, PERCENT)
        right_motor.spin(FORWARD, forward - turn, PERCENT)

        # ----------------------------
        # Arm Control
        # ----------------------------

        new_target = None
        manual_arm = False

        # Manual arm controls
        if controller_1.buttonUp.pressing():
            arm_motor.spin(FORWARD, 20, PERCENT)
            manual_arm = True

        elif controller_1.buttonDown.pressing():
            arm_motor.spin(REVERSE, 20, PERCENT)
            manual_arm = True

        # Stop ONLY after manual control was being used
        elif was_manual_arm:
            arm_motor.stop(HOLD)

        # Preset arm controls
        if not manual_arm:
            if controller_1.buttonX.pressing():
                new_target = ARM_HIGH

            elif controller_1.buttonA.pressing():
                new_target = ARM_MID

            elif controller_1.buttonB.pressing():
                new_target = ARM_LOW

            elif controller_1.buttonY.pressing():
                new_target = ARM_RESET

        # Move to preset only when target changes
        if new_target is not None and new_target != current_target:
            current_target = new_target
            arm_motor.spin_to_position(current_target, DEGREES, wait=False)

        was_manual_arm = manual_arm

        # ----------------------------
        # Claw Control
        # ----------------------------

        if controller_1.buttonL2.pressing():
            claw_motor.spin(FORWARD, 50, PERCENT)

        elif controller_1.buttonL1.pressing():
            claw_motor.spin(REVERSE, 50, PERCENT)

        else:
            claw_motor.stop(HOLD)

        wait(20, MSEC)

# ----------------------------
# Start Program
# ----------------------------

user_control()
