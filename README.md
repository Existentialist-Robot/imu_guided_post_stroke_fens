# IMU-Guided Post-Stroke FENS

A closed-loop system for IMU-guided **Functional Electrical Neurostimulation (FENS)** in post-stroke upper-limb rehabilitation. Multiple body-mounted IMUs detect residual movement intent; an onboard classifier identifies the target movement and triggers the appropriate stimulation pattern to assist completion.

## What is FENS?

Functional Electrical Neurostimulation applies targeted electrical stimulation to muscles or peripheral nerves to elicit voluntary-like movement in patients with motor impairment. In post-stroke contexts, where descending motor pathways are damaged, FENS can substitute for or reinforce voluntary drive — enabling patients to complete functional arm movements they can no longer initiate fully on their own.

IMU guidance closes the loop: rather than delivering fixed stimulation schedules, the system reads the patient's residual kinematics in real time and selects stimulation parameters based on detected movement intent.

## Target Movements (6 classes)

| # | Movement |
|---|----------|
| 1 | Curl In |
| 2 | Forward Reach |
| 3 | Lift In |
| 4 | Raise Outside |
| 5 | Reach Up |
| 6 | Touch Nose |

These are standard upper-limb functional rehabilitation exercises selected for clinical relevance in post-stroke ADL recovery.

## Hardware

| Component | Role |
|-----------|------|
| Arduino Nano 33 BLE | IMU peripheral node (×N, body-mounted) |
| LSM9DS1 (onboard) | 9-DOF IMU — accel / gyro / mag |
| Arduino Nano 33 BLE (central) | BLE hub, aggregates up to 3 peripherals |
| Host PC | Serial → UDP bridge, real-time classification |

## System Architecture

```
Peripheral Node(s)  [body-mounted]
  └─ LSM9DS1 → Madgwick AHRS filter → roll/pitch/yaw + raw accel/gyro
  └─ Custom BLE GATT service (5 characteristics: orient, accel, gyro, time, count)
  └─ Sampling rate negotiated dynamically from central based on sensor count

Central Node
  └─ Scans + connects up to 3 peripherals simultaneously
  └─ Time-syncs all sensors via BLE write
  └─ Binary serial protocol → host PC (2-byte board ID + packed float triples)

Host PC
  └─ UDP bridge (python/)
  └─ Real-time movement classification → FENS trigger
  └─ Offline analysis + model training (analysis/)
```

## Signal Pipeline

1. **Sensor fusion** — Madgwick AHRS filter on 9-DOF data at 119 Hz → Euler angles (roll/pitch/yaw)
2. **Calibration** — hard-iron distortion correction on magnetometer; per-axis offset + slope on accel/gyro
3. **Epoching** — trigger-aligned windows (3s post-trigger, 15-frame baseline)
4. **Baseline correction** — subtract pre-trigger mean from each channel
5. **Classification** — MLP (2× Dense 64 ReLU → Dense 6, `SparseCategoricalCrossentropy`) → movement class → FENS trigger

## Repository Structure

```
arduino_scripts/
  BLE_IMU_peripheral_w_time/        # Peripheral firmware (sensor fusion + BLE broadcast)
  BLE_IMU_central_w_time_combined/  # Central firmware (multi-sensor aggregation + serial out)
  ESP32_UDP_Client*/                # ESP32 variants — UDP streaming over WiFi
  AsyncUDPServer/                   # Async UDP server variant
  SD_BNO085_LED/                    # SD card logging variant with BNO085

python/
  Python_UDP_Server_V3.py           # UDP host bridge

analysis/
  esp32_validation.py               # Calibration, epoching, MLP training pipeline

data/
  1001/                             # Sample session — 4 CSV recordings + calibration plot

plots/                              # Calibration validation plots (accel, gyro, magnetometer)
```

## BLE Protocol

Custom GATT service (`917649A0-D98E-11E5-9EEC-0002A5D5C51B`) with 5 characteristics:

| Characteristic | Data | Size |
|---------------|------|------|
| Orientation | heading/pitch/roll as packed floats | 12 bytes |
| Acceleration | ax/ay/az | 12 bytes |
| Gyroscope | gx/gy/gz | 12 bytes |
| Timestamp | year/month/day/hour/min/sec/ms | 11 bytes |
| Count | connected sensor count (sets sample rate per board) | 4 bytes |

Serial output from central is binary: `[2-byte board ID][12B orient][12B accel][12B gyro][11B time]` per frame.

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
