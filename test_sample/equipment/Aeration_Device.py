import WAI
from WAI import DCN, DCP, SingleValue, StructureValue, STD
import numpy as np
import math

# Edited: FormulaBase 클래스 제거로 직접 함수 정의
# 기계계산식 : forward_calculate

'''수중포기기 - True (editable)'''
def forward_calculate(input_values:dict):
    '''설계조건'''
    SOR_O2_per_day = float(input_values.get("SOR_O2_per_day", 329.8)) # 지당 표준 산소요구량(SOR) - False
    Aeration_depth = int(input_values.get("Aeration_Depth", 5))            # 폭기 수심(m) - False
    Operation_time = float(input_values.get("Operation_Time", 10.00))         # 가동시간(hr) - True
    Number_of_Device = int(input_values.get("Device_number", 2))              # 가동대수 - True
    Number_of_Tank = int(input_values.get("Tank_number", 2))                  # 조 수량 - False
    W = float(input_values.get("width",8.7))                                  # 조 규격 W(mm) - True
    L = float(input_values.get("length",8.7))                                 # 조 규격 L(mm) - True
    He = float(input_values.get("water_level",5.5))                           # 조 규격 Water Level(mm) - True
    Tank_Total_Volume = W * L * He * Number_of_Tank                           # 전체 조 용적(㎥)

    '''설계기준'''
    # 1. 산소이송량에 따른 단위부피당 교반동력 조건
    # 산소전달량 상한 (kgO2/hr/대)
    oxygen_breaks = np.array([8.0, 13.8, 22.0, 32.5, 45.5, 65.0, 92.0, 125.0])

    # 정격동력 (kW)
    rated_powers = np.array([2.2, 3.7, 5.5, 7.5, 11.0, 15.0, 22.0, 30.0])

    # 정격정류 (A)
    rated_currents = np.array([7.1, 10.7, 16.6, 22.3, 31.8, 45.8, 66.7, 89.7])

    
    # 2. 장폭비에 따른 단위부피당 교반동력 조건
    # 장폭비 상한
    aspect_breaks = np.array([1.1, 1.5, 2.0])

    # 교반동력 밀도 (kW/m³) - 유효수심 6m 미만
    power_density_under6m = np.array([0.006, 0.007, 0.010])
    power_density_over6m = np.array([0.008, 0.008, 0.010])


    '''용량계산'''
    # 1. 수중포기기 산소이송량(kgO2/hr·대)
    Oxygen_transfer_amount = round(SOR_O2_per_day / Operation_time / Number_of_Device , 1)

    # 2. 교반용적(㎥) -***************** 이 부분 생물반응조 규격 불러와서 작성해야할듯 ************************
    Stirring_Volume = Tank_Total_Volume / Number_of_Device

    # 3. 장폭비 산정(AR)
    AR = W / L / Number_of_Device / Number_of_Device


    # 4. 동력산정(P)
    # 산소 공급 소요동력(Po, kW) - 수중포기기 규격 표 참조
    Oxygen_supply_power = next(
        (p for brk, p in zip(oxygen_breaks, rated_powers) if Oxygen_transfer_amount <= brk),
        rated_powers[-1]
        )
    
    # 유효수심 조건에 맞는 리스트 선택
    rated_density = power_density_under6m if Aeration_depth < 6 else power_density_over6m

    Determined_density = next(
        (pd for brk, pd in zip(aspect_breaks, rated_density) if AR <= brk),
        rated_density[-1])

    # 교반 필요동력
    Mixing_Efficiency = 0.5
    Motor_required_power = Determined_density * Stirring_Volume / Mixing_Efficiency
    Determined_power = max(Oxygen_supply_power, Motor_required_power)


    # 전류(A)
    Determined_current = next(
        (I for brk, I in zip(rated_powers, rated_currents) if Determined_power <= brk),
        rated_currents[-1])

    result = {
        "equipment_capacity": Oxygen_transfer_amount,
        "power": Determined_power, 
        "current": Determined_current,
        "operating_unit_count": Number_of_Device}
    return result

# 테스트 코드
if __name__ == "__main__":
    test_input = {}
    result = forward_calculate(test_input)
    print("수중포기기 규격(kgO2/hr*EA)", result["equipment_capacity"])
    print("수중포기기 실제 동력(kW): ", result["power"])
    print("수중포기기 전류(A): ", result["current"])
    print("수중포기기 대수(EA): ", result["operating_unit_count"])
