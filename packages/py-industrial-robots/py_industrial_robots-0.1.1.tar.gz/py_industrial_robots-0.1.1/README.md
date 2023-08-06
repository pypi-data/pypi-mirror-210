# Python Industrial Robots

This is an experimental set of python bindings for the also-experimental [Industrial Robots](https://github.com/mattj23/industrial-robots) library written in Rust.

This is a proof-of-concept for some simple tools related to generating and predicting motion and planning for industrial robots.  Currently, it is only wrapping a forward and inverse kinematics solver for the Fanuc LR Mate 200iD, a small, prolific industrial robot arm.  The solver itself uses the [K](https://github.com/openrr/k) library for kinematics, with the robot model painstakingly verified against the R30iB controller's handling of joints and the J2/J3 interaction so that values put into the model matching the controller will produce the same pose and format that the actual controller will report.

In the longer term, if the underlying Rust library proves to be useful, I will likely expand it to perform some amount of motion planning and collision detection and leave it open for others to add robots, and will update these bindings to match as many features as possible.

## Simple Use

```python 
import numpy
from py_industrial_robots import fanuc_fk, fanuc_ik

# Forward Kinematics
# =============================================

# Specify the joint angles in degrees exactly as they would go into the R30iB
poses = fanuc_fk([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
```

The result is a list of six poses, one for each joint. The poses themselves are in the form of lists 16 elements long, representing a 4x4 matrix in row-major order.  The last pose is the pose of the robot flange and will match what the controller reports when set to an empty tool frame. The other poses will have origins which lie on the X-Z plane on the axis of the joint, but the orientation of the poses will match the world coordinate system when the robot is at its zero position.

Physical distance units are in millimeters, as that's what the robot itself uses.

Poses can be converted to numpy matrices as follows:

```python
for i, pose in enumerate(poses):
    mat = numpy.matrix(pose).reshape(4, 4)
    print(f"Joint {i} pose:\n{mat}\n")
```

Inverse kinematics can be performed by passing a pose (in the same list-based, row-major format as they are received) and a list of initial joint angles to the `fanuc_ik` function. The underlying solver uses a Jacobian based approach.  The function will throw an exception if the solver does not find a result.  The result will be a list of six joint values in degrees as they would be sent to the R30iB controller.

```python
current_joints = [20.0, 30.0, -10.0, 15.0, 90.0, 12.0]
poses = fanuc_fk(current_joints)

# Get the pose of the robot flange and turn it into a numpy matrix
end_pose = numpy.matrix(poses[-1]).reshape(4, 4)

# Build a transform that moves the current position by x=10, y=20, z=30
transform = numpy.identity(4)
transform[:3, 3] = [10.0, 20.0, 30.0]

# Generate a new desired target pose
target_pose = transform * end_pose

# Convert into the list-based, row-major format
target = list(target_pose.flat)

# Run the IK solver
new_joints = fanuc_ik(target, current_joints)
```

***Note:** I currently use lists to move numbers back and forth across the boundary of Python and the compiled Rust binaries because I have yet to figure out how to use the Rust `numpy` package to create native `numpy` arrays.*

## Building

The goal is to be able to cross compile libraries for x86_64 Windows and Linux in a Linux based build environment.  I've managed to do that locally with the following.

### Prerequisites

* The Rust toolchain must be installed first
* MinGW-w64 must be installed. On Debian based systems this is the `mingw-w64` package.
* `llvm` must be installed, on Debian based systems this is the `llvm` package.
* The Windows target must be added to the Rust toolchain.  This can be done with `rustup target add x86_64-pc-windows-msvc`. There is a `-gnu` version as well, but the default Python Windows binaries are built with MSVC.
* Python must be installed and `maturin` must be installed into the Python environment.  This can be done with `pip install maturin`.

Example on Debian/Ubuntu build environment:

```bash
sudo apt-get install mingw-w64 llvm curl python3 python3-pip 
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup target add x86_64-pc-windows-msvc

# Install maturin into the Python environment, if you're not in a container you 
probably want to do this in a virtualenv 
pip3 install maturin
```

### Building

```bash
# Build for Linux
maturin build --release --strip

# Build for Windows
maturin build --release --strip --target x86_64-pc-windows-msvc
```
