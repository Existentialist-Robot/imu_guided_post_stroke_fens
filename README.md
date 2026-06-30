# IMU-Guided Post-Stroke Rehabilitation

A wireless multi-sensor system for capturing and classifying upper-limb movements in post-stroke rehabilitation contexts. Built on Arduino Nano 33 BLE with a 9-DOF IMU, BLE mesh coordination, and an MLP classifier trained on six functional arm movements.

## Overview

Post-stroke patients commonly present with arm and shoulder movement deficits. This system captures kinematic data from multiple body-mounted IMUs simultaneously and classifies movement intent — supporting both assessment and biofeedback applications.

**Target movements (6 classes):**
- Curl In
- Forward Reach
- Lift In
- Raise Outside
- Reach Up
- Touch Nose

## Hardware

| Component | Role |
|-----------|------|
| Arduino Nano 33 BLE | IMU peripheral node (×N) |
| LSM9DS1 (onboard) | 9-DOF IMU — accel / gyro / mag |
| Arduino Nano 33 BLE (central) | BLE hub, aggregates up to 3 peripherals |
| Host PC | Serial → UDP bridge, analysis |

## System Architecture

```
Peripheral Node(s)
  └─ LSM9DS1 → Madgwick AHRS filter → roll/pitch/yaw + raw accel/gyro
  └─ Custom BLE GATT service (5 characteristics: orient, accel, gyro, time, count)
  └─ Sampling rate negotiated dynamically from central based on sensor count

Central Node
  └─ Scans + connects up to 3 peripherals
  └─ Time-syncs all sensors via BLE write
  └─ Binary serial protocol → host PC (2-byte board ID + packed float triples)

Host PC
  └─ UDP bridge (python/)
  └─ Offline analysis + classification (analysis/)
```

## Repository Structure

```
arduino_scripts/
  BLE_IMU_peripheral_w_time/   # Peripheral firmware (sensor + BLE broadcast)
  BLE_IMU_central_w_time_combined/  # Central firmware (multi-sensor aggregation)
  ESP32_UDP_Client*/           # ESP32 variants — UDP streaming over WiFi
  AsyncUDPServer/              # Async UDP server variant
  SD_BNO085_LED/               # SD card logging variant with BNO085
  ...

python/
  Python_UDP_Server_V3.py      # UDP host bridge

analysis/
  esp32_validation.py          # Calibration, epoching, MLP training

data/
  1001/                        # Sample session — 4 CSV recordings + calibration plot

plots/                         # Calibration validation plots
```

## Signal Pipeline

1. **Sensor fusion** — Madgwick AHRS filter applied to raw 9-DOF data at 119 Hz → Euler angles (roll/pitch/yaw)
2. **Calibration** — hard-iron distortion correction on magnetometer; per-axis offset + slope on accel/gyro
3. **Epoching** — trigger-aligned windows (3s post-trigger, 15-frame baseline)
4. **Baseline correction** — subtract pre-trigger mean from each channel
5. **Classification** — MLP (2× Dense 64 ReLU → Dense 6, trained with `SparseCategoricalCrossentropy`)

## BLE Protocol

Custom GATT service (`917649A0-D98E-11E5-9EEC-0002A5D5C51B`) with 5 characteristics:

| Characteristic | Data | Size |
|---------------|------|------|
| Orientation | heading/pitch/roll as packed floats | 12 bytes |
| Acceleration | ax/ay/az | 12 bytes |
| Gyroscope | gx/gy/gz | 12 bytes |
| Timestamp | year/month/day/hour/min/sec/ms | 11 bytes |
| Count | connected sensor count (controls sample rate) | 4 bytes |

Serial output from central is binary (not ASCII): `[2-byte board ID][12B orient][12B accel][12B gyro][11B time]` per frame.

## Dependencies

**Arduino:**
- `ArduinoBLE`
- `Arduino_LSM9DS1` (with calibration extensions)
- `MadgwickAHRS` (included in peripheral sketch)
- `mbed.h` (time sync)

**Python:**
- `numpy`, `pandas`, `matplotlib`
- `tensorflow` / `keras`
- `sklearn`
