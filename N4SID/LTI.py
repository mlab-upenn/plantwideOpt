import numpy as np
import pandas as pd
from nfoursid.nfoursid import NFourSID

excel_file = pd.ExcelFile('simple_dynamic_process.xlsx')
train_data = pd.read_excel(excel_file, sheet_name='Training Data')
test_data = pd.read_excel(excel_file, sheet_name='Testing Data')

U_train = train_data[['U1', 'U2']].values #2columns
Y_train = train_data[['Y1', 'Y2']].values #2columns

U_test = test_data[['U1', 'U2']].values #2columns
Y_test = test_data[['Y1', 'Y2']].values #2columns

n4sid_algo = NFourSID(
    dataframe=train_data,
    output_columns=['Y1', 'Y2'],
    input_columns=['U1', 'U2'],
    num_block_rows=20
)

n4sid_algo.subspace_identification()
state_space, cov = n4sid_algo.system_identification(rank=2)

A = state_space.a
B = state_space.b
C = state_space.c
D = state_space.d

print(f"A matrix shape: {A.shape}")
print(f"A matrix:\n{A}")
print(f"\nB matrix shape: {B.shape}")
print(f"B matrix:\n{B}")
print(f"\nC matrix shape: {C.shape}")
print(f"C matrix:\n{C}")
print("\nD matrix shape: {D.shape}")
print(f"D matrix:\n{D}")

N_test = len(U_test)
x = np.zeros((2, 1))  
Y_pred = np.zeros((N_test, 2))

for k in range(N_test):
    y_k = C @ x + D @ U_test[k:k+1].T
    Y_pred[k] = y_k.flatten()
    x = A @ x + B @ U_test[k:k+1].T

mae = np.mean(np.abs(Y_test - Y_pred), axis=0)
max_ae = np.max(np.abs(Y_test - Y_pred), axis=0)
ss_res = np.sum((Y_test - Y_pred) ** 2, axis=0)
ss_tot = np.sum((Y_test - np.mean(Y_test, axis=0)) ** 2, axis=0)
r2_score = 1 - (ss_res / ss_tot)

print(f"  Y1 - MAE: {mae[0]:.6e}, Max AE: {max_ae[0]:.6e}, R²: {r2_score[0]:.6f}")
print(f"  Y2 - MAE: {mae[1]:.6e}, Max AE: {max_ae[1]:.6e}, R²: {r2_score[1]:.6f}")
print(f"\n  Overall R²: {np.mean(r2_score):.6f}")

import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 1, figsize=(14, 8))

axes[0].plot(Y_test[:, 0], 'b-', label='Measured', linewidth=2)
axes[0].plot(Y_pred[:, 0], 'r--', label='Predicted (N4SID)', linewidth=2, alpha=0.8)
axes[0].set_title(f'Test Data - Y1', fontsize=12, fontweight='bold')
axes[0].set_ylabel('Y1', fontsize=11)
axes[0].legend(fontsize=10)
axes[0].grid(True, alpha=0.3)

metrics_text_y1 = f"MAE: {mae[0]:.6e}\nMax AE: {max_ae[0]:.6e}\nR²: {r2_score[0]:.6f}"
axes[0].text(0.98, 0.97, metrics_text_y1, transform=axes[0].transAxes, fontsize=9,
             verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

axes[1].plot(Y_test[:, 1], 'b-', label='Measured', linewidth=2)
axes[1].plot(Y_pred[:, 1], 'r--', label='Predicted (N4SID)', linewidth=2, alpha=0.8)
axes[1].set_title(f'Test Data - Y2', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Sample', fontsize=11)
axes[1].set_ylabel('Y2', fontsize=11)
axes[1].legend(fontsize=10)
axes[1].grid(True, alpha=0.3)
metrics_text_y2 = f"MAE: {mae[1]:.6e}\nMax AE: {max_ae[1]:.6e}\nR²: {r2_score[1]:.6f}"
axes[1].text(0.98, 0.97, metrics_text_y2, transform=axes[1].transAxes, fontsize=9,
             verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.tight_layout()
plt.savefig('test_validation.png', dpi=150, bbox_inches='tight')