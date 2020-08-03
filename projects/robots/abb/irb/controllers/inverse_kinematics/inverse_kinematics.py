# Copyright 1996-2020 Cyberbotics Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Demonstration of inverse kinematics using the "ikpy" Python module."""

import sys
import tempfile
try:
    import ikpy
    from ikpy.chain import Chain
    from ikpy.link import OriginLink, URDFLink
except ImportError:
    sys.exit('The "ikpy" Python module is not installed. '
             'To run this sample, please upgrade "pip" and install ikpy with this command: "pip install ikpy"')

import math
from controller import Supervisor

if ikpy.__version__[0] < '3':
    sys.exit('The "ikpy" Python module version is too old. '
             'Please upgrade "ikpy" Python module to version "3.0" or newer with this command: "pip install --upgrade ikpy"')

# Initialize the Webots Supervisor.
supervisor = Supervisor()
timeStep = int(4 * supervisor.getBasicTimeStep())

# Create the arm chain from the URDF
filename = None
with tempfile.NamedTemporaryFile(suffix='.urdf', delete=False) as file:
    filename = file.name
    file.write(supervisor.getUrdf())
armChain = Chain.from_urdf_file(filename)

# Initialize the arm motors.
motors = []
for motorName in ['A motor', 'B motor', 'C motor', 'D motor', 'E motor', 'F motor']:
    motor = supervisor.getMotor(motorName)
    motor.setVelocity(1.0)
    motors.append(motor)

# Get the arm and target nodes.
target = supervisor.getFromDef('TARGET')
arm = supervisor.getSelf()

# Loop 1: Draw a circle on the paper sheet.
print('Draw a circle on the paper sheet...')
while supervisor.step(timeStep) != -1:
    t = supervisor.getTime()

    # Use the circle equation relatively to the arm base as an input of the IK algorithm.
    x = 0.25 * math.cos(t) + 1.1
    y = 0.25 * math.sin(t) - 0.95
    z = 0.23

    # Call "ikpy" to compute the inverse kinematics of the arm.
    ikResults = armChain.inverse_kinematics([x, y, z])

    # Actuate the 3 first arm motors with the IK results.
    for i in range(3):
        motors[i].setPosition(ikResults[i + 1])
    # Keep the hand orientation down.
    motors[4].setPosition(-ikResults[2] - ikResults[3] + math.pi / 2)
    # Keep the hand orientation perpendicular.
    motors[5].setPosition(ikResults[1])

    # Conditions to start/stop drawing and leave this loop.
    if supervisor.getTime() > 2 * math.pi + 1.5:
        break
    elif supervisor.getTime() > 1.5:
        # Note: start to draw at 1.5 second to be sure the arm is well located.
        supervisor.getPen('pen').write(True)

# Loop 2: Move the arm hand to the target.
print('Move the yellow and black sphere to move the arm...')
while supervisor.step(timeStep) != -1:
    # Get the absolute postion of the target and the arm base.
    targetPosition = target.getPosition()
    armPosition = arm.getPosition()

    # Compute the position of the target relatively to the arm.
    # x and y axis are inverted because the arm is not aligned with the Webots global axes.
    x = targetPosition[0] - armPosition[0]
    y = - (targetPosition[2] - armPosition[2])
    z = targetPosition[1] - armPosition[1]

    # Call "ikpy" to compute the inverse kinematics of the arm.
    ikResults = armChain.inverse_kinematics([x, y, z])

    # Actuate the 3 first arm motors with the IK results.
    for i in range(3):
        motors[i].setPosition(ikResults[i + 1])
