# SIMPLE DYNAMIC PROCESS TEST CASE

This model implements **Linear Time-Invariant (LTI) system identification** on a simple dynamic process using the **N4SID algorithm** (Numerical algorithms for Subspace State Space System Identification). Our goal is to identify a discrete-time state-space model from input-output measurements and validate its accuracy.

![DIP-3](https://github.com/user-attachments/assets/496bf53e-4ca7-43d0-a9b0-e1d2ebb1f85b)

## Problem Statement:

The input dataset is `simple_dynamic_process.xlsx` containing two sheets: 
    - Training Data: 2,001 samples with 2 inputs (U1, U2) and 2 outputs (Y1, Y2)
    - Testing Data: 2,001 samples with 2 inputs (U1, U2) and 2 outputs (Y1, Y2)

Data Characteristics:
    - Synthetic, noise-free data from a controlled dynamic system
    - Time is sampling index only (not a regressor or model input)
    - Input ranges: U1, U2 ∈ [-10, 10]
    - Output ranges: Y1 ∈ [-15, 15], Y2 ∈ [-30, 30]

We aim to identify a 2nd-order LTI state-space model that:
    - Captures the underlying system dynamics from input-output measurements
    - Is time-invariant
    - Is continuous
    - Can be used for prediction and control

We choose N4SID for state-space identification as it requires only input-output measurements, no prior model knowledge, no hyperparameters. N4SID first constructs Hankel matrices from input-output measurements. These matrices capture temporal dynamics in a structured way. Then it performs SVD to extract state evolution information, system order, and past input/output relationships, captured by the U,Σ and V matrices respectively. With state information extracted from SVD, it performs least squares to extract four system matrices:

```
Discrete-time State-Space Model:
x[k+1] = A·x[k] + B·u[k]        
y[k]   = C·x[k] + D·u[k]        

where:
  x[k] ∈ ℝ²     - 2-dimensional state vector
  u[k] ∈ ℝ²     - 2-dimensional input vector
  y[k] ∈ ℝ²     - 2-dimensional output vector
  
  A ∈ ℝ²ˣ²     - State transition matrix
  B ∈ ℝ²ˣ²     - Input matrix
  C ∈ ℝ²ˣ²     - Output matrix
  D ∈ ℝ²ˣ²     - Feedthrough matrix
```

We simulate the identified model on test data that unseen during identification, and compare predicted vs. measured outputs.

## Identified Model:

A Matrix (2×2):
```
[[ 9.679881e-01  -6.449348e-04]
 [-1.069063e-02   9.347679e-01]]
```
We observe that eigenvalues are near 0.97 (<1) indicating stability. We also observe low coupling between states as off-diagonals are small

B Matrix (2×2):
```
[[-6.752000e-04  -1.125649e-02]
 [ 1.213200e-02  -7.368800e-04]]
```
- U2 has stronger effect on x[2] (0.0112 vs. 0.00012)
- U1 has stronger effect on x[1] (0.0121 vs. 0.00068)

C Matrix (2×2):
```
[[ -0.573614   7.942033]
 [-13.059585  -0.710215]]
```
- Strong coupling between states and outputs
- Asymmetric influence (Y2 strongly depends on x[1])

D Matrix (2×2):
```
≈ almost 0
```
- No direct input-to-output feedthrough

## Continuity & Smoothness:

- The state evolution x[k+1] = A·x[k] + B·u[k] is continuous in the discrete-time domain (C0)
- First derivatives are well-defined, rate of change is smooth and the system has bounded eigenvalues (C1)
- Second derivatives exist and are bounded (C2)

## Accuracy & Performance:

<img width="2086" height="1184" alt="test_validation" src="https://github.com/user-attachments/assets/4100a2cb-34b2-4dc1-adb4-2f6673a13a6c" />

- Mean Absolute Error = Y1: 8.30e-14, Y2: 1.94e-13

- Maximum Absolute Error = Y1: 3.77e-13, Y2: 5.04e-13

- R² Score = Y1: 1.000000, Y2: 1.000000

We observe near-perfect accuracy as the data is generated from known process model, there are no bad values or noise, and the 2nd order model captures all dynamics.

### Data Limitations:

- It is understood that real-world performance will be worse, expected R² = 0.7-0.95 with noise. Real processes also often exhibit nonlinearities.

- The system here is fully observable and controllable, real systems may have unobservable and uncontrollable modes (hidden dynamics and possibility of not affecting all states).

### Output Files
- **Console**: System matrices (A, B, C, D) and performance metrics
- **test_validation.png**: Plot of measured vs. predicted outputs with error metrics
