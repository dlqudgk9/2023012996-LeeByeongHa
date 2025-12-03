import pandas as pd
import numpy as np

# ==========================
# 0. 상수 정의 (cfg + 공기)
# ==========================
p_inf = 101325.0      # FREESTREAM_PRESSURE [Pa]
T_inf = 288.15        # FREESTREAM_TEMPERATURE [K]
gamma = 1.4
R = 287.0             # 공기 기체상수 [J/kg/K]
M_tip = 0.877         # MACH_MOTION

# 밀도, 음속, 기준속도, 동압 계산
rho_inf = p_inf / (R * T_inf)
a_inf = np.sqrt(gamma * R * T_inf)
V_ref = M_tip * a_inf
q_inf = 0.5 * rho_inf * V_ref**2   # 0.5 * rho * V^2

print("rho_inf =", rho_inf)
print("a_inf   =", a_inf)
print("V_ref   =", V_ref)
print("q_inf   =", q_inf)

# ==========================
# 1. CSV 불러오기
# ==========================
df = pd.read_csv("su2.csv")
print("Loaded", len(df), "points.")

required_columns = ['Points_0', 'Points_1', 'Pressure']
if not all(col in df.columns for col in required_columns):
    raise ValueError(f"CSV에 {required_columns} 컬럼이 있어야 해!")

# ==========================
# 2. Cp 직접 계산
# ==========================
df['Cp'] = (df['Pressure'] - p_inf) / q_inf

# ==========================
# 3. x/c 계산 (Points_1 방향이 chord 방향)
# ==========================
y_min = df['Points_1'].min()
y_max = df['Points_1'].max()
c = y_max - y_min

df['x_over_c'] = (df['Points_1'] - y_min) / c

# ==========================
# 4. Upper / Lower 면 분리
#    (Points_0 중간값 기준)
# ==========================
x_mid = 0.5 * (df['Points_0'].min() + df['Points_0'].max())

# 필요에 따라 부등호 방향이 바뀔 수도 있음 (그래프 보고 판단)
df_upper = df[df['Points_0'] >= x_mid].copy()
df_lower = df[df['Points_0'] <  x_mid].copy()

print("Upper points:", len(df_upper))
print("Lower points:", len(df_lower))

# 정렬
upper_sorted = df_upper[['x_over_c', 'Cp']].sort_values(by='x_over_c', ascending=True)
upper_sorted['Surface'] = 'Upper'

lower_sorted = df_lower[['x_over_c', 'Cp']].sort_values(by='x_over_c', ascending=False)
lower_sorted['Surface'] = 'Lower'

combined = pd.concat([upper_sorted, lower_sorted])
combined.to_excel("Cp_x_over_c_from_pressure.xlsx", index=False)

print("Saved to 'Cp_x_over_c_from_pressure.xlsx'")