#
# Origin File : PROCESS_SBR_R3_MAIN_TRT0101.py
# 25.11.08 JK
# 동일한 파일명의 계산식이 업로드 되지 않아서, 파일명만 변경
#
###############################################################################

import WAI
# Edited: DSP, Info, UnitSystemType, INF 추가
from WAI import DCN, DCP, DEP, SingleValue, RangedValue, Unit, DCR, DSP, EQP, EquipmentValue, StructureValue, STC, StructureType, TextValue, Info, UnitSystemType, INF, StandardTable, STD, StructureLayoutType
# Edited: 기계 계산식 및 구조물 계산식을 import할 필요가 없습니다.

# Edited: Info 공정 메타 정보 추가 (공정 코드, 단위계, 계산식 버전 등)
INF.Info = Info(process_code="SBR",
                unit_system=UnitSystemType.METRIC,
                formula_version="v2.0.0",
                author="정지연",
                date="2025-10-16")

import math

''' 설계조건 '''
DCN.influents.q=SingleValue("Q", 1041.8, False,"㎥/d")
DCN.influents.bod=SingleValue("BOD", 207.0, False,"mg/L")
DCN.influents.cod=SingleValue("COD", 300.0, False,"mg/L")
DCN.influents.toc=SingleValue("TOC", 133.0, False,"mg/L")
DCN.influents.ss=SingleValue("SS", 177.0, False,"mg/L")
DCN.influents.tn=SingleValue("T-N", 44.0, False,"mg/L")
DCN.influents.tp=SingleValue("T-P", 8, False,"mg/L")
DCN.influents.temp=SingleValue("Temperature", 12, False, unit=Unit.CELSIUS)

DCN.effluents.water.q=DCN.influents.q
DCN.effluents.water.bod=DCN.influents.bod
DCN.effluents.water.cod=DCN.influents.cod
DCN.effluents.water.toc=DCN.influents.toc
DCN.effluents.water.ss=DCN.influents.ss
DCN.effluents.water.tn=DCN.influents.tn
DCN.effluents.water.tp=DCN.influents.tp

DCN.effluents.sludge.q=DCN.influents.q
DCN.effluents.sludge.bod=DCN.influents.bod
DCN.effluents.sludge.cod=DCN.influents.cod
DCN.effluents.sludge.toc=DCN.influents.toc
DCN.effluents.sludge.ss=DCN.influents.ss
DCN.effluents.sludge.tn=DCN.influents.tn
DCN.effluents.sludge.tp=DCN.influents.tp

'''값이 다른 이유 -> 처리효율 및 농도의 소수점을 무시하고 정수값으로 처리했기 때문 => 그렇기 때문에 결과에 큰 차이 발생함'''

DCN.efficiency.bod=RangedValue("BOD", 97.6, True, 80, 99, unit="%")
DCN.efficiency.cod=RangedValue("COD", 88, True, 80, 95, unit="%")
DCN.efficiency.toc=RangedValue("TOC", 88, True, 70,90,unit="%")
DCN.efficiency.ss=RangedValue("SS", 92, True, 80,95,unit="%")
DCN.efficiency.tn=RangedValue("T-N", 70, True, 70,90,unit="%")
DCN.efficiency.tp=RangedValue("T-P", 79, True, 65,85,unit="%")

#농도 -> 부하량으로 계산 (INFLUENT)
Influent_water_bod_Load = DCN.influents.q * DCN.influents.bod /1000
Influent_water_cod_Load = DCN.influents.q * DCN.influents.cod/1000
Influent_water_toc_Load = DCN.influents.q * DCN.influents.toc/1000
Influent_water_ss_Load = DCN.influents.q * DCN.influents.ss/1000
Influent_water_tn_Load = DCN.influents.q * DCN.influents.tn/1000
Influent_water_tp_Load = DCN.influents.q * DCN.influents.tp/1000

#부하량을 기준으로 INFLUENT 부하량 계산
Effluent_water_bod_load = Influent_water_bod_Load - Influent_water_bod_Load * (DCN.efficiency.bod * 0.01)
Effluent_water_cod_load = Influent_water_cod_Load - Influent_water_cod_Load * (DCN.efficiency.cod * 0.01)
Effluent_water_toc_load = Influent_water_toc_Load - Influent_water_toc_Load * (DCN.efficiency.toc * 0.01)
Effluent_water_ss_load = Influent_water_ss_Load - Influent_water_ss_Load * (DCN.efficiency.ss *0.01)
Effluent_water_tn_load = Influent_water_tn_Load - Influent_water_tn_Load * (DCN.efficiency.tn *0.01)
Effluent_water_tp_load = Influent_water_tp_Load - Influent_water_tp_Load * (DCN.efficiency.tp * 0.01)

Effluent_TN = DCN.effluents.water.tn


''' 설계인자 '''
DCP.Sludge.MLSS=RangedValue("MLSS", 2800, True, 1000, 5000,unit="mg/L")
DCP.Sludge.Nitrifcation=RangedValue("Nitrifcation S.F", 1.3, True, 1, 1.5,unit="-")
DCP.Sludge.SVI=RangedValue("SVI",100, True, 50, 120,unit="ml/g")
DCP.Sludge.DecantSF=RangedValue("Decant S.F", 1.5, True, 1.0, 1.5, unit="-", remark="Decanting Safety Factor")

Setting_MLSS = DCP.Sludge.MLSS

DCP.Kinetic_Coeffient.m=RangedValue("㎛",6, True, 3, 13.2,unit="gVSS/gVSS/d", remark="Hetrotroph (20 ℃)")
DCP.Kinetic_Coeffient.ks=RangedValue("Ks",20, True, 5, 40,unit="mg bCOD/L", remark="Hetrotroph (20 ℃)")
DCP.Kinetic_Coeffient.y=RangedValue("Y",0.4, True, 0.3, 0.5,unit="gVSS/g bCOD", remark="Hetrotroph (20 ℃)")
DCP.Kinetic_Coeffient.kd=RangedValue("kd",0.12, True, 0.06, 0.2,unit="gVSS/gVSS/d", remark="Hetrotroph (20 ℃)")
DCP.Kinetic_Coeffient.fd=RangedValue("fd",0.15, True, 0.08, 0.2,unit="-", remark="Hetrotroph (20 ℃)")
DCP.Kinetic_Coeffient.thofm=RangedValue("θ of ㎛",1.07, True, 1.03, 1.08,unit="", remark="Hetrotroph")
DCP.Kinetic_Coeffient.thofkd=RangedValue("θ of Kd",1.04, True, 1.03, 1.08,unit="", remark="Hetrotroph")
DCP.Kinetic_Coeffient.thofks=RangedValue("θ of Ks",1, True, 1, 1,unit="", remark="Hetrotroph")

DCP.Kinetic_Coeffient.mn=RangedValue("㎛n",0.75, True, 0.2, 0.9,unit="gVSS/gVSS/d", remark="Autotroph (20 ℃)")
DCP.Kinetic_Coeffient.kn=RangedValue("Kn",0.74, True, 0.5, 1,unit="mgNH4-N/L", remark="Autotroph (20 ℃)")
DCP.Kinetic_Coeffient.yn=RangedValue("Yn",0.12, True, 0.1, 0.15,unit="gVSS/gNH4-N", remark="Autotroph (20 ℃)")
DCP.Kinetic_Coeffient.kdn=RangedValue("kdn",0.08, True, 0.05, 0.15,unit="gVSS/gVSS/d", remark="Autotroph (20 ℃)")
DCP.Kinetic_Coeffient.ko=RangedValue("Ko",0.5, True, 0.4, 0.6,unit="mg/L", remark="Autotroph (20 ℃)")
DCP.Kinetic_Coeffient.thofmn=RangedValue("θ of ㎛",1.07, True, 1.06, 1.12,unit="", remark="Autotroph")
DCP.Kinetic_Coeffient.thofkdn=RangedValue("θ of Kd",1.05, True, 1.03, 1.12,unit="", remark="Autotroph")
DCP.Kinetic_Coeffient.thofksn=RangedValue("θ of Ks",1.04, True, 1.03, 1.08,unit="", remark="Autotroph")

DCP.Operation_Cycle.RAS=RangedValue("RAS Time",10, True, unit="min/Cycle")
DCP.Operation_Cycle.Anoxic=RangedValue("Anoxic Time",0, True, unit="min/Cycle")
DCP.Operation_Cycle.Fill=RangedValue("Fill/Anoxic Mix Time",80, True, unit="min/Cycle")
DCP.Operation_Cycle.Aeration=RangedValue("Aeration Time",150, True, unit="min/Cycle")
DCP.Operation_Cycle.Setting=RangedValue("Setting Time",60, True, unit="min/Cycle")
DCP.Operation_Cycle.Discharge=RangedValue("Discharge Time",60, False, unit="min/Cycle")
DCP.Operation_Cycle.Decant=RangedValue("Decant Time",55, True, unit="min/Cycle")
DCP.Operation_Cycle.Sludge=RangedValue("Sludge Discharge Time",5, True, unit="min/Cycle")
DCP.Operation_Cycle.Pause=RangedValue("Pause Time",0, True, unit="min/Cycle")
DCP.Operation_Cycle.Total=RangedValue("Total Time",360, False, unit="min/Cycle")

DCP.ETC.DO_in_Basin=RangedValue("DO in Aeration Basin",2, True, 2.0, 4.0,unit="mg/L")
DCP.ETC.BDCOD_ratio=RangedValue("BDCOD rato",1.5, True, 1.3, 1.5,unit="-", remark="BDBOD = BOD * BDCOD Ratio")
DCP.ETC.bpCOD_pCOD_ratio=RangedValue("bpCOD/pCOD",0.8, True, 0.8, 1,unit="-")
DCP.ETC.EffluentOrgN=RangedValue("Effluent Org-N",0.6, True, 0.8, 1,unit="mg/L")
DCP.ETC.EffluentNH4=RangedValue("Effluent NH4", 1, True, 0.8, 1,unit="mg/L")

'''
Operation_total_Time = DCP.Operation_Cycle.Total.value

Temp_Condition = DCN.influents.temp# 
Influent_q = DCN.influents.q#
DO_basin = DCP.ETC.DO_in_Basin#
Nitrification_SF = DCP.Sludge.Nitrifcation #
BDCOD_ratio = DCP.ETC.BDCOD_ratio#
Infleunt_TN = DCN.influents.tn#
Effluent_NO3 = DCN.effluents.water.tn - DCP.ETC.EffluentOrgN - DCP.ETC.EffluentNH4#
Effluent_NH4 = DCP.ETC.EffluentNH4#
Delta_BOD = DCN.influents.bod - DCN.effluents.water.bod#
Aeration_time_per_cycle = DCP.Operation_Cycle.Aeration#
Anoxic_time_per_cycle = DCP.Operation_Cycle.Fill#
Effluent_orgN = 1
'''

#이건 DCN에 넣어야할 수도 있겠다.
Influent_alk = 250 #(mg/L as CaCO3)

# DCN으로 통합 제안 -> 통합될 경우, 모든 계산식에 해당 내용이 추가되어야할까?
#DCN.influents.Influent_alk = SingleValue("Influent_alk", 250, False, unit="mg/L as CaCO3")

# ===== DSP 통합 제안 =====

# 1. 운전 조건 관련 변수들
DSP.Operation.Operation_total_Time = SingleValue("Operation_total_Time", 0, False, unit="min/Cycle")
DSP.Operation.Aeration_time_per_cycle = SingleValue("Aeration_time_per_cycle", 0, False, unit="min/Cycle")
DSP.Operation.Anoxic_time_per_cycle = SingleValue("Anoxic_time_per_cycle", 0, False, unit="min/Cycle")

DSP.Operation.Operation_total_Time = DCP.Operation_Cycle.Total.value
DSP.Operation.Aeration_time_per_cycle = DCP.Operation_Cycle.Aeration.value
DSP.Operation.Anoxic_time_per_cycle = DCP.Operation_Cycle.Fill.value

# 2. 수질 조건 관련 변수들
DSP.Water_Quality.Temp_Condition = SingleValue("Temp_Condition", 20, False, unit="℃")
DSP.Water_Quality.Influent_q = SingleValue("Influent_q", 1000, False, unit="㎥/d")
DSP.Water_Quality.Infleunt_TN = SingleValue("Infleunt_TN", 50, False, unit="mg/L")
DSP.Water_Quality.Delta_BOD = SingleValue("Delta_BOD", 200, False, unit="mg/L")
DSP.Water_Quality.Influent_alk = SingleValue("Influent_alk", 250, False, unit="mg/L as CaCO3")

DSP.Water_Quality.Temp_Condition = DCN.influents.temp
DSP.Water_Quality.Influent_q = DCN.influents.q.value
DSP.Water_Quality.Infleunt_TN = DCN.influents.tn.value
DSP.Water_Quality.Delta_BOD = DCN.influents.bod - DCN.effluents.water.bod
# DSP.Water_Quality.Influent_alk = DCN.influents.Influent_alk # DCN에 등록될 경우


# 3. 설계 파라미터 관련 변수들 
DSP.Design_Parameters.DO_basin = SingleValue("DO_basin", 2.0, False, unit="mg/L")
DSP.Design_Parameters.Nitrification_SF = SingleValue("Nitrification_SF", 2.5, False, unit="-")
DSP.Design_Parameters.BDCOD_ratio = SingleValue("BDCOD_ratio", 0.8, False, unit="-")

DSP.Design_Parameters.DO_basin = DCP.ETC.DO_in_Basin.value
DSP.Design_Parameters.Nitrification_SF = DCP.Sludge.Nitrifcation.value
DSP.Design_Parameters.BDCOD_ratio = DCP.ETC.BDCOD_ratio.value


# 4. 유출수질 관련 변수들
DSP.Effluent_Quality.Effluent_NO3 = SingleValue("Effluent_NO3", 10, False, unit="mg/L", remark="유출수 질산성질소")
DSP.Effluent_Quality.Effluent_NH4 = SingleValue("Effluent_NH4", 1, False, unit="mg/L", remark="유출수 암모니아성질소")
DSP.Effluent_Quality.Effluent_orgN = SingleValue("Effluent_orgN", 1, False, unit="mg/L", remark="유출수 유기질소")

DSP.Effluent_Quality.Effluent_NO3 = DCN.effluents.water.tn - DCP.ETC.EffluentOrgN - DCP.ETC.EffluentNH4
DSP.Effluent_Quality.Effluent_NH4 = DCP.ETC.EffluentNH4.value

# 5. 기타 계산된 변수들
DSP.Calculated.Effluent_TN = SingleValue("Effluent_TN", 12, False, unit="mg/L", remark="유출수 총질소")
DSP.Calculated.Effluent_TN = DCN.effluents.water.tn.value

# 6. 슬러지 관련 변수들
DSP.Sludge.Setting_MLSS = SingleValue("Setting_MLSS", 3000, False, unit="mg/L", remark="설정 MLSS")
DSP.Sludge.Setting_MLSS = DCP.Sludge.MLSS.value


''' 20C에서 활성슬러지 내 종속영양미생물(Heterotrophs)의 반응속도계수 
#Specific Growth Rate of Hetero in 20 degree celcius
m_hetero_design_temp = DCP.Kinetic_Coeffient.m * DCP.Kinetic_Coeffient.thofm ** (DCN.influents.temp - 20)
# KS of Hetero in 20 degree celcius
ks_hetero_design_temp  = DCP.Kinetic_Coeffient.ks* DCP.Kinetic_Coeffient.thofks ** (DCN.influents.temp - 20)
# Yield of Hetero in 20 degree celcius
yield_hetero_design_temp = DCP.Kinetic_Coeffient.y
# Kd of Hetero in 20 degree celcius
kd_hetero_design_temp = DCP.Kinetic_Coeffient.kd * DCP.Kinetic_Coeffient.thofkd ** (DCN.influents.temp - 20)
#fd of Hetero in 20 degree celcius
fd_hetero_design_temp = DCP.Kinetic_Coeffient.fd
'''

# ===== DSP 통합 제안 =====
DSP.Kinetics.m_hetero_design_temp = SingleValue("m_hetero_design_temp", 3.0, False, unit="gVSS/gVSS/d")
DSP.Kinetics.ks_hetero_design_temp = SingleValue("ks_hetero_design_temp", 20, False, unit="mg bCOD/L")
DSP.Kinetics.yield_hetero_design_temp = SingleValue("yield_hetero_design_temp", 0.4, False, unit="gVSS/g bCOD")
DSP.Kinetics.kd_hetero_design_temp = SingleValue("kd_hetero_design_temp", 0.05, False, unit="gVSS/gVSS/d")
DSP.Kinetics.fd_hetero_design_temp = SingleValue("fd_hetero_design_temp", 0.08, False, unit="-")

DSP.Kinetics.m_hetero_design_temp = DCP.Kinetic_Coeffient.m * DCP.Kinetic_Coeffient.thofm ** (DCN.influents.temp - 20)
DSP.Kinetics.ks_hetero_design_temp = DCP.Kinetic_Coeffient.ks * DCP.Kinetic_Coeffient.thofks ** (DCN.influents.temp - 20)
DSP.Kinetics.yield_hetero_design_temp = DCP.Kinetic_Coeffient.y.value
DSP.Kinetics.kd_hetero_design_temp = DCP.Kinetic_Coeffient.kd * DCP.Kinetic_Coeffient.thofkd ** (DCN.influents.temp - 20)
DSP.Kinetics.fd_hetero_design_temp = DCP.Kinetic_Coeffient.fd.value


''' 20C에서 활성슬러지 내 질산화미생물(Autotrophs)의 반응속도계수
#Specific Growth Rate of Auto in 20 degree celcius
mn_auto_design_temp = DCP.Kinetic_Coeffient.mn * DCP.Kinetic_Coeffient.thofmn ** (DCN.influents.temp - 20)
#Kn of Auto in 20 degree celcius
kn_auto_design_temp = DCP.Kinetic_Coeffient.kn * DCP.Kinetic_Coeffient.thofkdn ** (DCN.influents.temp - 20)
#Yn(Yield) of auto in 20 degree celcius
yn_auto_design_temp = DCP.Kinetic_Coeffient.yn
#kdn of auto in 20 degree celcius
kdn_auto_design_temp = DCP.Kinetic_Coeffient.kdn * DCP.Kinetic_Coeffient.thofksn ** (DCN.influents.temp - 20)
#ko of auto in 20 degree celcius
ko_auto_design_temp = DCP.Kinetic_Coeffient.ko
 '''

# ===== DSP 통합 제안 =====
DSP.Kinetics.mn_auto_design_temp = SingleValue("mn_auto_design_temp", 0.5, False, unit="gVSS/gVSS/d")
DSP.Kinetics.kn_auto_design_temp = SingleValue("kn_auto_design_temp", 0, False, unit="mgNH4-N/L")
DSP.Kinetics.yn_auto_design_temp = SingleValue("yn_auto_design_temp", 0, False, unit="gVSS/gNH4-N")
DSP.Kinetics.kdn_auto_design_temp = SingleValue("kdn_auto_design_temp", 0.05, False, unit="gVSS/gVSS/d")
DSP.Kinetics.ko_auto_design_temp = SingleValue("ko_auto_design_temp", 0.5, False, unit="mg/L")

DSP.Kinetics.mn_auto_design_temp = DCP.Kinetic_Coeffient.mn * DCP.Kinetic_Coeffient.thofmn ** (DCN.influents.temp - 20)
DSP.Kinetics.kn_auto_design_temp = DCP.Kinetic_Coeffient.kn * DCP.Kinetic_Coeffient.thofkdn ** (DCN.influents.temp - 20)
DSP.Kinetics.yn_auto_design_temp = DCP.Kinetic_Coeffient.yn.value
DSP.Kinetics.kdn_auto_design_temp = DCP.Kinetic_Coeffient.kdn * DCP.Kinetic_Coeffient.thofksn ** (DCN.influents.temp - 20)
DSP.Kinetics.ko_auto_design_temp = DCP.Kinetic_Coeffient.ko.value


''' A-1. 운전주기 결정
# 1Cycle당 총 운전시간(hr)
Reaction_time_aCycle = DCP.Operation_Cycle.Total / 60

# 1Cycle당 포기시간(hr)
Aeration_time_aCycle = DCP.Operation_Cycle.Aeration / 60

# 1지 운전주기 (Cycle/d)
Number_of_Cycle_Per_day = 24 / (Operation_total_Time / 60)

# Fill volume 계산 (1Cycle당 Fill Volume) (㎥/cycle)
Fillvolume = Influent_q / Number_of_Cycle_Per_day
 '''

# ===== DSP 통합 제안 =====
DSP.Operation.Reaction_time_aCycle = SingleValue("Reaction_time_aCycle", 0, False, unit="hr", remark="1Cycle당 총 운전시간")
DSP.Operation.Aeration_time_aCycle = SingleValue("Aeration_time_aCycle", 0, False, unit="hr", remark="1Cycle당 포기시간")
DSP.Operation.Number_of_Cycle_Per_day = SingleValue("Number_of_Cycle_Per_day", 0, False, unit="Cycle/d", remark="1지 운전주기")
DSP.Operation.Fillvolume = SingleValue("Fillvolume", 0, False, unit="㎥/cycle", remark="1Cycle당 Fill Volume")

DSP.Operation.Reaction_time_aCycle = DCP.Operation_Cycle.Total / 60
DSP.Operation.Aeration_time_aCycle = DCP.Operation_Cycle.Aeration / 60
DSP.Operation.Number_of_Cycle_Per_day = 24 / (DCP.Operation_Cycle.Total / 60)
DSP.Operation.Fillvolume = DSP.Water_Quality.Influent_q / DSP.Operation.Number_of_Cycle_Per_day


''' A-2. 한 주기당 허용 유입분율(VF/VT) 결정
# Calculation MLSS Conc in Settle Vol(Xs) under Supposed SVI (mg/L)
Xs = 1000 * 1000 / DCP.Sludge.SVI

# Decant Safety Factor considered Safety Factor (Unitless)
Setting_Ratio = DCP.Sludge.MLSS / Xs * DCP.Sludge.DecantSF

# Minimum Fill ratio Cal (Unitless)
Min_fill_ratio = 1 - Setting_Ratio

# Fill Vol에 의한 반응조 소요용량 계산 (㎥)
Fill_ratio_Reactor_Req_Vol = Fillvolume / Min_fill_ratio
 '''

# ===== DSP 변환 제안 =====
DSP.Sludge.Xs = SingleValue("Xs", 0, False, unit="mg/L")
DSP.Sludge.Setting_Ratio = SingleValue("Setting_Ratio", 0, False, unit="-")
DSP.Sludge.Min_fill_ratio = SingleValue("Min_fill_ratio", 0, False, unit="-")       # 유입분율 최대
DSP.Reactor.Fill_ratio_Reactor_Req_Vol = SingleValue("Fill_ratio_Reactor_Req_Vol", 0, False, unit="㎥")

DSP.Sludge.Xs = 1000 * 1000 / DCP.Sludge.SVI
DSP.Sludge.Setting_Ratio = DCP.Sludge.MLSS / DSP.Sludge.Xs * DCP.Sludge.DecantSF
DSP.Sludge.Min_fill_ratio = 1 - DSP.Sludge.Setting_Ratio
DSP.Reactor.Fill_ratio_Reactor_Req_Vol = DSP.Operation.Fillvolume / DSP.Sludge.Min_fill_ratio


''' A-4. 슬러지 HRT(SRT) 결정
# 질산화미생물(Autotrophs)의 비성장율(Specific Growth Rate(μn)) Cal (g/g/d)
# (여기서 1은 유출 암모니아 농도인데 추가 수정될 여지가 있음)
Specificgrowthrate_Auto = (mn_auto_design_temp * 1) / (kn_auto_design_temp + 1) * (DO_basin) / (ko_auto_design_temp + DO_basin) - kdn_auto_design_temp

# 최소 고형물 SRT (Minimum SRT for nitrification (d))
SRTmin = 1 / Specificgrowthrate_Auto

# 질산화를 위한 최소 SRT(Design SRT Cal (d))
SRT_designed = Nitrification_SF * SRTmin * Reaction_time_aCycle / Aeration_time_aCycle

# 슬러지 농도 관련 값들
Solid_Concentration = DCN.effluents.sludge.ss
Pump_inflow_solid_conc = DCN.effluents.water.ss / 10000  # Unit = %
 '''

# ===== DSP 변환 제안 =====
DSP.Biology.Specificgrowthrate_Auto = SingleValue("Specificgrowthrate_Auto", 0, False, unit="g/g/d")
DSP.Biology.SRTmin = SingleValue("SRTmin", 0, False, unit="d")
DSP.Biology.SRT_designed = SingleValue("SRT_designed", 0, False, unit="d")
DSP.Sludge.Solid_Concentration = SingleValue("Solid_Concentration", 0, False, unit="mg/L")
DSP.Sludge.Pump_inflow_solid_conc = SingleValue("Pump_inflow_solid_conc", 0, False, unit="%")

DSP.Biology.Specificgrowthrate_Auto = (DSP.Kinetics.mn_auto_design_temp * 1) / (DSP.Kinetics.kn_auto_design_temp + 1) * (DSP.Design_Parameters.DO_basin) / (DSP.Kinetics.ko_auto_design_temp + DSP.Design_Parameters.DO_basin) - DSP.Kinetics.kdn_auto_design_temp
DSP.Biology.SRTmin = 1 / DSP.Biology.Specificgrowthrate_Auto
DSP.Biology.SRT_designed = DSP.Design_Parameters.Nitrification_SF * DSP.Biology.SRTmin * DSP.Operation.Reaction_time_aCycle / DSP.Operation.Aeration_time_aCycle
DSP.Sludge.Solid_Concentration = DCN.effluents.sludge.ss.value
DSP.Sludge.Pump_inflow_solid_conc = DCN.effluents.water.ss / 10000


''' A-5. 일일 순미생물생성량 산정
# Influent VSS Concentration(mg/L)
Influent_VSS = DCN.influents.ss * 0.9

# Influent nonbiodegradable nbVSS Concentration (mg/L)
Influent_nbVSS = (1-DCP.ETC.bpCOD_pCOD_ratio) * Influent_VSS

# Growth Limiting biodegradable soluble COD(bsCOD) concentration (mg bsCOD/L)
S = ks_hetero_design_temp * (1 + kd_hetero_design_temp * SRT_designed) / (SRT_designed * (m_hetero_design_temp - kd_hetero_design_temp) -1)

# Influent NOx
Infleunt_NOx = DCN.influents.tn.value * (Effluent_NO3 / Effluent_TN)
 '''

# ===== DSP 변환 제안 =====
DSP.Biology.Influent_VSS = SingleValue("Influent_VSS", 0, False, unit="mg/L")
DSP.Biology.Influent_nbVSS = SingleValue("Influent_nbVSS", 0, False, unit="mg/L")
DSP.Biology.S = SingleValue("S", 0, False, unit="mg bsCOD/L")
DSP.Biology.Infleunt_NOx = SingleValue("Infleunt_NOx", 0, False, unit="mg/L")

DSP.Biology.Influent_VSS = DCN.influents.ss * 0.9
DSP.Biology.Influent_nbVSS = (1-DCP.ETC.bpCOD_pCOD_ratio) * DSP.Biology.Influent_VSS
DSP.Biology.S = DSP.Kinetics.ks_hetero_design_temp * (1 + DSP.Kinetics.kd_hetero_design_temp * DSP.Biology.SRT_designed) / (DSP.Biology.SRT_designed * (DSP.Kinetics.m_hetero_design_temp - DSP.Kinetics.kd_hetero_design_temp) -1)
DSP.Biology.Infleunt_NOx = DCN.influents.tn.value * (DSP.Effluent_Quality.Effluent_NO3 / DSP.Calculated.Effluent_TN)


''' A-6. 슬러지 생산량, 반응 중 MLSS 및 MLVSS 결정
#PxVSS (kg/d)
Act_Biomass = Influent_q * yield_hetero_design_temp * (DCN.influents.bod * BDCOD_ratio - S) / (1+ SRT_designed * kd_hetero_design_temp) / 1000
Endogenous_respiration_Biomass = fd_hetero_design_temp * kd_hetero_design_temp * Influent_q * yield_hetero_design_temp * (DCN.influents.bod.value * BDCOD_ratio - S) * SRT_designed /1000/ (1+kd_hetero_design_temp*SRT_designed)
#Non-biodegradable organic suspended solids
Nonbiodegradable_SS = Influent_q * yn_auto_design_temp * Infleunt_NOx / (1+ kdn_auto_design_temp*SRT_designed)/1000
#nbVSS MAss
nbVSS_Mass = Influent_q * Influent_nbVSS / 1000
PxVSS = Act_Biomass + Endogenous_respiration_Biomass + Nonbiodegradable_SS + nbVSS_Mass
#PxTSS (kg/d)
PxTSS = (Act_Biomass + Endogenous_respiration_Biomass + Nonbiodegradable_SS)/0.85 + nbVSS_Mass + Influent_q*(DCN.influents.ss.value - Influent_VSS)/1000
#Mass of MLVSS (kg VSS)
Xvss_V = PxVSS * SRT_designed
#Mass of MLSS (kg SS)
Xtss_V = PxTSS * SRT_designed
#Fraction VSS (-)
VSS_TSS_Ratio = Xvss_V / Xtss_V

# Secondary Sludge Production (㎥/d)
Sludge_production_q = PxTSS * 1000 / Xs
#sludge discharge time (min)
Sludge_discharge_time = (DCP.Operation_Cycle.Sludge/60)* Number_of_Cycle_Per_day * 60

# Reactor Required Capacity (㎥)
#Setting_MLSS = DCP.Sludge.MLSS
MLSS_Sustain_Reactor_Req_Vol = Xtss_V * 1000 / DCP.Sludge.MLSS 
Fill_ratio_Reactor_Req_Vol
Final_Req_Vol = max(MLSS_Sustain_Reactor_Req_Vol, Fill_ratio_Reactor_Req_Vol)
 '''

# ===== DSP 변환 제안 =====
DSP.Biology.Act_Biomass = SingleValue("Act_Biomass", 0, False, unit="kg/d")
DSP.Biology.Endogenous_respiration_Biomass = SingleValue("Endogenous_respiration_Biomass", 0, False, unit="kg/d")
DSP.Biology.Nonbiodegradable_SS = SingleValue("Nonbiodegradable_SS", 0, False, unit="kg/d")
DSP.Biology.nbVSS_Mass = SingleValue("nbVSS_Mass", 0, False, unit="kg/d")
DSP.Biology.PxVSS = SingleValue("PxVSS", 0, False, unit="kg/d")
DSP.Biology.PxTSS = SingleValue("PxTSS", 0, False, unit="kg/d")
DSP.Biology.Xvss_V = SingleValue("Xvss_V", 0, False, unit="kg VSS")
DSP.Biology.Xtss_V = SingleValue("Xtss_V", 0, False, unit="kg SS")
DSP.Biology.VSS_TSS_Ratio = SingleValue("VSS_TSS_Ratio", 0, False, unit="-")

DSP.Sludge.Sludge_production_q = SingleValue("Sludge_production_q", 0, False, unit="㎥/d")
DSP.Operation.Sludge_discharge_time = SingleValue("Sludge_discharge_time", 0, False, unit="min")

DSP.Reactor.MLSS_Sustain_Reactor_Req_Vol = SingleValue("MLSS_Sustain_Reactor_Req_Vol", 0, False, unit="㎥")
DSP.Reactor.Final_Req_Vol = SingleValue("Final_Req_Vol", 0, False, unit="㎥")
DSP.SBR_Tank.Final_Req_Vol = SingleValue("SBR_Req_Vol", 0, False, unit="㎥")

DSP.Biology.Act_Biomass = DSP.Water_Quality.Influent_q * DSP.Kinetics.yield_hetero_design_temp * (DCN.influents.bod * DSP.Design_Parameters.BDCOD_ratio - DSP.Biology.S) / (1+ DSP.Biology.SRT_designed * DSP.Kinetics.kd_hetero_design_temp) / 1000
DSP.Biology.Endogenous_respiration_Biomass = DSP.Kinetics.fd_hetero_design_temp * DSP.Kinetics.kd_hetero_design_temp * DSP.Water_Quality.Influent_q * DSP.Kinetics.yield_hetero_design_temp * (DCN.influents.bod.value * DSP.Design_Parameters.BDCOD_ratio - DSP.Biology.S) * DSP.Biology.SRT_designed /1000/ (1+DSP.Kinetics.kd_hetero_design_temp*DSP.Biology.SRT_designed)
DSP.Biology.Nonbiodegradable_SS = DSP.Water_Quality.Influent_q * DSP.Kinetics.yn_auto_design_temp * DSP.Biology.Infleunt_NOx / (1+ DSP.Kinetics.kdn_auto_design_temp*DSP.Biology.SRT_designed)/1000
DSP.Biology.nbVSS_Mass = DSP.Water_Quality.Influent_q * DSP.Biology.Influent_nbVSS / 1000
DSP.Biology.PxVSS = DSP.Biology.Act_Biomass + DSP.Biology.Endogenous_respiration_Biomass + DSP.Biology.Nonbiodegradable_SS + DSP.Biology.nbVSS_Mass
DSP.Biology.PxTSS = (DSP.Biology.Act_Biomass + DSP.Biology.Endogenous_respiration_Biomass + DSP.Biology.Nonbiodegradable_SS)/0.85 + DSP.Biology.nbVSS_Mass + DSP.Water_Quality.Influent_q*(DCN.influents.ss.value - DSP.Biology.Influent_VSS)/1000
DSP.Biology.Xvss_V = DSP.Biology.PxVSS * DSP.Biology.SRT_designed
DSP.Biology.Xtss_V = DSP.Biology.PxTSS * DSP.Biology.SRT_designed
DSP.Biology.VSS_TSS_Ratio = DSP.Biology.Xvss_V / DSP.Biology.Xtss_V


# 잉여슬러지 발생량
DSP.Sludge.Sludge_production_q = DSP.Biology.PxTSS * 1000 / DSP.Sludge.Xs
DSP.Operation.Sludge_discharge_time = (DCP.Operation_Cycle.Sludge/60)* DSP.Operation.Number_of_Cycle_Per_day * 60

DSP.Reactor.MLSS_Sustain_Reactor_Req_Vol = DSP.Biology.Xtss_V * 1000 / DSP.Sludge.Setting_MLSS
DSP.Reactor.Final_Req_Vol = max(DSP.Reactor.MLSS_Sustain_Reactor_Req_Vol.value, DSP.Reactor.Fill_ratio_Reactor_Req_Vol.value)
DSP.SBR_Tank.Final_Req_Vol = DSP.Reactor.Final_Req_Vol.value

##여기에 Effluent MB 작성
Effluent_sludge_ss_load = DSP.Biology.PxTSS.value
Effluent_sludge_bod_load = Effluent_sludge_ss_load* 1.42/1.72
Effluent_sludge_cod_load = Effluent_sludge_bod_load * 0.75
Effluent_sludge_toc_load = Effluent_sludge_bod_load * 0.75
Effluent_sludge_tn_load = DSP.Biology.PxVSS * 0.12  # 수정
Effluent_sludge_tp_load = Influent_water_tp_Load - Effluent_water_tp_load

# 농도
DCN.effluents.sludge.q = DSP.Sludge.Sludge_production_q.value
DCN.effluents.sludge.bod = Effluent_sludge_bod_load / DSP.Sludge.Sludge_production_q * 1000 
DCN.effluents.sludge.cod = Effluent_sludge_bod_load / DSP.Sludge.Sludge_production_q * 1000
DCN.effluents.sludge.toc = Effluent_sludge_toc_load / DSP.Sludge.Sludge_production_q * 1000
DCN.effluents.sludge.ss = DSP.Sludge.Xs
DCN.effluents.sludge.tn = Effluent_sludge_tn_load / DSP.Sludge.Sludge_production_q * 1000
DCN.effluents.sludge.tp = Effluent_sludge_tp_load / DSP.Sludge.Sludge_production_q * 1000

DCN.effluents.water.q = DCN.influents.q - DCN.effluents.sludge.q

DCN.effluents.water.bod = Effluent_water_bod_load / DCN.effluents.water.q * 1000
DCN.effluents.water.cod = Effluent_water_cod_load / DCN.effluents.water.q * 1000
DCN.effluents.water.toc = Effluent_water_toc_load / DCN.effluents.water.q * 1000
DCN.effluents.water.ss = Effluent_water_ss_load / DCN.effluents.water.q * 1000
DCN.effluents.water.tn = Effluent_water_tn_load / DCN.effluents.water.q * 1000
DCN.effluents.water.tp = Effluent_water_tp_load / DCN.effluents.water.q * 1000

# 4. 유출수질 관련 변수들
DSP.Effluent_Quality.Effluent_NO3 = SingleValue("Effluent_NO3", 10, False, unit="mg/L", remark="유출수 질산성질소")
DSP.Effluent_Quality.Effluent_NH4 = SingleValue("Effluent_NH4", 1, False, unit="mg/L", remark="유출수 암모니아성질소")
DSP.Effluent_Quality.Effluent_orgN = SingleValue("Effluent_orgN", 1, False, unit="mg/L", remark="유출수 유기질소")

DSP.Effluent_Quality.Effluent_NO3 = DCN.effluents.water.tn - DCP.ETC.EffluentOrgN - DCP.ETC.EffluentNH4
print(DSP.Effluent_Quality.Effluent_NO3)
print(DCP.ETC.EffluentOrgN)
print(DCP.ETC.EffluentNH4)
DSP.Effluent_Quality.Effluent_NH4 = DCP.ETC.EffluentNH4.value

# 5. 기타 계산된 변수들
DSP.Calculated.Effluent_TN = SingleValue("Effluent_TN", 12, False, unit="mg/L", remark="유출수 총질소")
DSP.Calculated.Effluent_TN = DCN.effluents.water.tn.value

# 6. 슬러지 관련 변수들
DSP.Sludge.Setting_MLSS = SingleValue("Setting_MLSS", 3000, False, unit="mg/L", remark="설정 MLSS")
DSP.Sludge.Setting_MLSS = DCP.Sludge.MLSS.value

''' A-7. 반응조 용량 결정 - DSP 전용 계산 체계 '''
# 1. 기존 계산식
'''
tank_number = 2
water_level = 5.0
width = round(math.sqrt(DSP.Reactor.Final_Req_Vol/tank_number * 1.1 / water_level),1)
length = round(math.sqrt(DSP.Reactor.Final_Req_Vol/tank_number * 1.1 / water_level),1)
'''

STC.flowtank = StructureValue(
    name="SBR tank",
    code_key_list=[StructureType.CONCRETE_SQUARE],
    code_key=StructureType.CONCRETE_SQUARE,
    tank_number_list=[2, 4, 6, 8],  # 구조물 지수 목록, 첫번째 지수가 tank_number 기본값으로 등록
    water_level=10.8,
    width=7,
    length=7,
    height=7.0,
    required_capacity=DSP.Reactor.Final_Req_Vol/2)

STC.flowtank.required_capacity=DSP.Reactor.Final_Req_Vol/STC.flowtank.tank_number

#STC.flowtank.W = round(math.sqrt(DSP.Reactor.Final_Req_Vol/STC.flowtank.tank_number * 1.1 / STC.flowtank.water_level),1)
#STC.flowtank.L = round(math.sqrt(DSP.Reactor.Final_Req_Vol/STC.flowtank.tank_number * 1.1 / STC.flowtank.water_level),1)


'''
# 1. 기존 계산식
Working_Vol = STC.flowtank.tank_number *  STC.flowtank.W * STC.flowtank.L * STC.flowtank.water_level
'''

# 2. DSP 변수 정의
DSP.SBR_Tank.Working_Vol = SingleValue("Working_Vol", 940, False, unit="㎥")
DSP.SBR_Tank.Working_Vol = STC.flowtank.tank_number *  STC.flowtank.W * STC.flowtank.L * STC.flowtank.water_level       # 실제

DCR.Working_Vol = RangedValue("Working_Vol", DSP.SBR_Tank.Working_Vol.value, False, Min = DSP.SBR_Tank.Final_Req_Vol.value, unit = "㎥")
#STC.flowtank.required_capacity =  STC.flowtank.tank_number *  STC.flowtank.W * STC.flowtank.L * STC.flowtank.water_level

''' A-8. 설계검토(MLSS, F/M, HRT)
# 1. 기존 계산식
Operational_MLSS = round(Xtss_V *1000 / Working_Vol,1)
Operational_MLVSS = round(Operational_MLSS * VSS_TSS_Ratio,1)
FM_ratio = round(Influent_q * (Delta_BOD) / (Working_Vol*Operational_MLVSS),1)
Designed_HRT = Working_Vol / (Influent_q / 24)
Designed_Fillratio = Fillvolume / Working_Vol
 '''

# 2. DSP 변수들 정의
DSP.Design_Check.Operational_MLSS = SingleValue("Operational_MLSS", 1, False, unit="mg/L", remark="운전 MLSS")
DSP.Design_Check.Operational_MLVSS = SingleValue("Operational_MLVSS", 1, False, unit="mg/L", remark="운전 MLVSS")
DSP.Design_Check.FM_ratio = SingleValue("FM_ratio", 1, False, unit="-", remark="F/M 비율")
DSP.Design_Check.Designed_HRT = SingleValue("Designed_HRT", 0, False, unit="hr", remark="설계 HRT")
DSP.Design_Check.Designed_Fillratio = SingleValue("Designed_Fillratio", 0, False, unit="-", remark="설계 충전비율")


DSP.Design_Check.Operational_MLSS = round(DSP.Biology.Xtss_V *1000 / DSP.SBR_Tank.Working_Vol)
DSP.Design_Check.Operational_MLVSS =round(DSP.Design_Check.Operational_MLSS * DSP.Biology.VSS_TSS_Ratio)
DSP.Design_Check.FM_ratio = round(DSP.Water_Quality.Influent_q * (DSP.Water_Quality.Delta_BOD) / (DSP.SBR_Tank.Working_Vol*DSP.Design_Check.Operational_MLVSS))
DSP.Design_Check.Designed_HRT =  DSP.SBR_Tank.Working_Vol / (DSP.Water_Quality.Influent_q / 24)
DSP.Design_Check.Designed_Fillratio =DSP.Operation.Fillvolume / DSP.SBR_Tank.Working_Vol


''' A-10. 질소 Balance 
# 1. 기존 계산식
Xn = (Influent_q*yn_auto_design_temp*Infleunt_NOx*SRT_designed)/(1+kdn_auto_design_temp*SRT_designed)/Working_Vol
NH4_conc_for_nitrification = Infleunt_TN-Effluent_NH4-(0.12*(Act_Biomass + Endogenous_respiration_Biomass + Nonbiodegradable_SS)/Influent_q * 1000)
Vf_NOx = (Fillvolume/STC.flowtank.tank_number)*NH4_conc_for_nitrification/1000
'''

# 2. DSP 변수들 정의
DSP.Nitrogen_Balance.Xn = SingleValue("Xn", 0, False, unit="mg/L", remark="질산화미생물 농도")
DSP.Nitrogen_Balance.NH4_conc_for_nitrification = SingleValue("NH4_conc_for_nitrification", 0, False, unit="mg NOx/L", remark="질산화용 NH4-N 농도")
DSP.Nitrogen_Balance.Vf_NOx = SingleValue("Vf_NOx", 0, False, unit="kg/fill", remark="주기당 NH4-N 부하량") 

#NH4 Loading Before Fill
# 1. 기존 계산식
DSP.Nitrogen_Balance.Xn = (DSP.Water_Quality.Influent_q *DSP.Kinetics.yn_auto_design_temp*DSP.Biology.Infleunt_NOx*DSP.Biology.SRT_designed)/(1+DSP.Kinetics.kdn_auto_design_temp*DSP.Biology.SRT_designed)/DSP.SBR_Tank.Working_Vol
DSP.Nitrogen_Balance.NH4_conc_for_nitrification = DSP.Water_Quality.Infleunt_TN-DSP.Effluent_Quality.Effluent_NH4-(0.12*(DSP.Biology.Act_Biomass + DSP.Biology.Endogenous_respiration_Biomass + DSP.Biology.Nonbiodegradable_SS)/DSP.Water_Quality.Influent_q * 1000)
DSP.Nitrogen_Balance.Vf_NOx = (DSP.Operation.Fillvolume/STC.flowtank.tank_number)*DSP.Nitrogen_Balance.NH4_conc_for_nitrification/1000


''' A-12. 질산화율(SNR), 탈질율(SDNR)
# 1. 기존 계산식
Nitrified_TN = NH4_conc_for_nitrification * Influent_q / 1000
Denitrified_TN = (NH4_conc_for_nitrification - Effluent_NO3) * Influent_q / 1000
total_MLVSS_in_reactor = Operational_MLVSS/1000*Working_Vol
Total_Aeration_Time = Aeration_time_per_cycle / 60 * Number_of_Cycle_Per_day
Total_Anoxic_Time = Anoxic_time_per_cycle / 60 * Number_of_Cycle_Per_day
Designed_SNR = Nitrified_TN / total_MLVSS_in_reactor / (Total_Aeration_Time / 24)
Designed_SDNR = Denitrified_TN / total_MLVSS_in_reactor / (Total_Anoxic_Time / 24)
 '''

# 2. DSP 변수들 정의
DSP.Nitrogen_Process.Nitrified_TN = SingleValue("Nitrified_TN", 0, False, unit="kg/d", remark="질산화된 총질소")
DSP.Nitrogen_Process.Denitrified_TN = SingleValue("Denitrified_TN", 0, False, unit="kg/d", remark="탈질된 총질소")
DSP.Nitrogen_Process.total_MLVSS_in_reactor = SingleValue("total_MLVSS_in_reactor", 0, False, unit="kgMLVSS", remark="반응조 내 총 MLVSS")
DSP.Nitrogen_Process.Total_Aeration_Time = SingleValue("Total_Aeration_Time", 0, False, unit="hr", remark="총 포기시간")
DSP.Nitrogen_Process.Total_Anoxic_Time = SingleValue("Total_Anoxic_Time", 0, False, unit="hr", remark="총 무산소시간")
DSP.Nitrogen_Process.Designed_SNR = SingleValue("Designed_SNR", 0, False, unit="gNH3-N/gMv/d", remark="설계 질산화율")
DSP.Nitrogen_Process.Designed_SDNR = SingleValue("Designed_SDNR", 0, False, unit="gNOx-N/gMv/d", remark="설계 탈질율")

DSP.Nitrogen_Process.Nitrified_TN = DSP.Nitrogen_Balance.NH4_conc_for_nitrification * DSP.Water_Quality.Influent_q / 1000
DSP.Nitrogen_Process.Denitrified_TN = (DSP.Nitrogen_Balance.NH4_conc_for_nitrification - DSP.Effluent_Quality.Effluent_NO3) * DSP.Water_Quality.Influent_q / 1000
DSP.Nitrogen_Process.total_MLVSS_in_reactor = DSP.Design_Check.Operational_MLVSS/1000 * DSP.SBR_Tank.Working_Vol
DSP.Nitrogen_Process.Total_Aeration_Time = DSP.Operation.Aeration_time_per_cycle / 60 * DSP.Operation.Number_of_Cycle_Per_day
DSP.Nitrogen_Process.Total_Anoxic_Time = DSP.Operation.Anoxic_time_per_cycle / 60 * DSP.Operation.Number_of_Cycle_Per_day
DSP.Nitrogen_Process.Designed_SNR = DSP.Nitrogen_Process.Nitrified_TN / DSP.Nitrogen_Process.total_MLVSS_in_reactor / (DSP.Nitrogen_Process.Total_Aeration_Time / 24)
DSP.Nitrogen_Process.Designed_SDNR = DSP.Nitrogen_Process.Denitrified_TN / DSP.Nitrogen_Process.total_MLVSS_in_reactor / (DSP.Nitrogen_Process.Total_Anoxic_Time / 24)


# 3. DCP에 저장
DCP.Aeration.total_time = SingleValue("Total_Aeration_Time", DSP.Nitrogen_Process.Total_Aeration_Time, False, "hr")

# 제거 BOD 당 필요한 산소량(0.5~0.7)
DCP.Aeration.A=RangedValue("A",0.6, True,0.5,0.7, unit="kgO2/kgBOD", remark="Required O2 / Removed BOD")
# 탈질에 의해 소비된 BOD량
DCP.Aeration.K=RangedValue("K",2.9, True, unit="kgBOD/kgN", remark="BOD consumed by Denitrifcation")
# Unit MLVSS 당 내생호흡에 의한 산소소비량(0.05~0.15)
DCP.Aeration.B=RangedValue("B",0.1, True,0.05,0.15, unit="kgO2/kgMLVSS/d", remark="Consumed O2 per MLVSS due to Endogenous Respiration")
# 질산화 반응에 따라 소비된 산소량
DCP.Aeration.C=RangedValue("C",4.6, True, unit="kgO2/kgN", remark="Consumed O2 Per Nitrificaiton")
# 청수에 대한 산소전달률
DCP.Aeration.Ea=RangedValue("Ea",18, True, unit="%", remark="OTE of Clean Water")
# 송풍량 여유율
DCP.Aeration.Safety=RangedValue("Safety Factor",10, True, unit="%", remark="Safety Factor of Gs")
#OTE는 Aerator의 타입에 따라 변경되어야함. 즉, OTE객체를 미리 만들어두고 해당객체가 송풍기 타입에 따라 값이 변경되게 코드 작성
DCP.Aeration.OTE=RangedValue("OTE",18, True, unit="%", remark="Oxygen transfer Efficiency")
OTE = DCP.Aeration.OTE
Aeration_SF = DCP.Aeration.Safety


''' B. 소요공기량 - 재계산 필요'''  
# 1. DSP 변수 정의
DSP.Aeration.OD1 = SingleValue("OD1", 0, False, unit="kg_O2/d", remark="BOD 산화용 산소요구량")
DSP.Aeration.OD2 = SingleValue("OD2", 0, False, unit="kg_O2/d", remark="내생호흡용 산소요구량")
DSP.Aeration.OD3 = SingleValue("OD3", 0, False, unit="kg_O2/d", remark="질산화용 산소요구량")
DSP.Aeration.OD4 = SingleValue("OD4", 0, False, unit="kg_O2/d", remark="기타 산소요구량")
DSP.Aeration.Va = SingleValue("Va", 0, False, unit="㎥", remark="포기용 반응조 용적")
DSP.Aeration.MLVSS_Mass = SingleValue("MLVSS_Mass", 0, False, unit="kg", remark="MLVSS 질량")

# 2. DSP 변수들만을 사용한 AOR 계산
A = DCP.Aeration.A
K = DCP.Aeration.K
DSP.Aeration.OD1 = A * ((DSP.Water_Quality.Delta_BOD.value * DSP.Water_Quality.Influent_q.value / 1000) - DSP.Nitrogen_Process.Denitrified_TN * K)

B = DCP.Aeration.B
DSP.Aeration.Va = DSP.SBR_Tank.Working_Vol * DSP.Operation.Aeration_time_per_cycle * DSP.Operation.Number_of_Cycle_Per_day / 24
DSP.Aeration.MLVSS_Mass = DSP.Design_Check.Operational_MLVSS / 1000
DSP.Aeration.OD2 = B * DSP.Aeration.Va * DSP.Aeration.MLVSS_Mass

C = DCP.Aeration.C
DSP.Aeration.OD3 = C * (DSP.Nitrogen_Process.Nitrified_TN * DSP.Water_Quality.Influent_q.value / 1000)

# 3. AOR 계산 (DSP 변수들만 사용)
DSP.Aeration.AOR = SingleValue("AOR", 0, False, unit="kgO2/d", remark="실제 산소요구량")
DSP.Aeration.AOR = DSP.Aeration.OD1 + DSP.Aeration.OD2 + DSP.Aeration.OD3 + DSP.Aeration.OD4
#SOR, GS 계산해야함
#Csw = Oxygen Saturation Concentration(@ 20℃) (mg/L)
Csw = 8.84

#Cs값 계산 (수온에 따른 산소포화량)(mg/L)
import numpy as np
# 온도 및 산소량 테이블
temperatures = np.array([8, 9, 10, 11, 12, 13, 14, 15,
                         16, 17, 18, 19, 20, 21, 22, 23, 24, 25])
oxygen_levels = np.array([11.47, 11.19, 10.92, 10.67, 10.43, 10.20,
                          9.97, 9.76, 9.56, 9.37, 9.18, 9.01,
                          8.84, 8.68, 8.53, 8.39, 8.25, 8.11])

# 4. DSP 변수들만을 사용한 SOR 및 송풍량 계산
DSP.Aeration.Cs = SingleValue("Cs", 0, False, unit="mg/L", remark="수온에 따른 산소포화량")
DSP.Aeration.Ca = SingleValue("Ca", 2.0, False, unit="mg/L", remark="반응조 내 DO")
DSP.Aeration.alpha = SingleValue("alpha", 0, False, unit="-", remark="상대 산소전달율")
DSP.Aeration.beta = SingleValue("beta", 0.95, False, unit="-", remark="상대 DO 포화농도")
DSP.Aeration.Cs_correction_Factor = SingleValue("Cs_correction_Factor", 0, False, unit="-", remark="Cs 보정계수")
DSP.Aeration.Atmospheric_Pressure = SingleValue("Atmospheric_Pressure", 760, False, unit="mmHg", remark="대기압")
DSP.Aeration.SOR = SingleValue("SOR", 0, False, unit="kgO2/d", remark="표준 산소요구량")
DSP.Aeration.Gs = SingleValue("Gs", 0, False, unit="㎥-air/min", remark="송풍량")

# DSP 변수들만을 사용한 계산
DSP.Aeration.Cs = np.interp(DSP.Water_Quality.Temp_Condition.value, temperatures, oxygen_levels)
DSP.Aeration.alpha = math.exp(-0.082 * DSP.Design_Check.Operational_MLSS / 1000)
DSP.Aeration.Cs_correction_Factor = 1 + 0.5 * STC.flowtank.water_level / 10.24

DSP.Aeration.SOR = DSP.Aeration.AOR * Csw * DSP.Aeration.Cs_correction_Factor / (DSP.Aeration.alpha * 1.024**(DSP.Water_Quality.Temp_Condition.value - 20) * (DSP.Aeration.beta * DSP.Aeration.Cs * DSP.Aeration.Cs_correction_Factor - DSP.Aeration.Ca)) * (760 / DSP.Aeration.Atmospheric_Pressure)

Density_of_air = 1.2923
Ow = 0.2315
DSP.Aeration.Gs = DSP.Aeration.SOR / (OTE/100*Density_of_air*Ow) * (293/273) / (DSP.Nitrogen_Process.Total_Aeration_Time*60) * (1+Aeration_SF/100)

# 5. DCP에 DSP 변수들 저장
DCP.Aeration.OD1=RangedValue("OD1", DSP.Aeration.OD1.value, False, unit="kgO2/day", remark="Required O2 to Oxidate BOD")
DCP.Aeration.OD2=RangedValue("OD2", DSP.Aeration.OD2.value, False, unit="kgO2/day", remark="Required O2 for Endogenous Respiration [kgO2/day]")
DCP.Aeration.OD3=RangedValue("OD3", DSP.Aeration.OD3.value, False, unit="kgO2/day", remark="Required O2 for nitrification")
DCP.Aeration.OD4=RangedValue("OD4", DSP.Aeration.OD4.value, False, unit="kgO2/day", remark="O2 in Effluent Flow")
DCP.Aeration.AOR=RangedValue("AOR", DSP.Aeration.AOR.value, False, unit="kgO2/day")
DCP.Aeration.SOR=RangedValue("SOR", DSP.Aeration.SOR.value, False, unit="kgO2/day")
DCP.Aeration.Gs=RangedValue("Gs", DSP.Aeration.Gs.value, False, unit="㎥-air/min", remark="Blower Flow (Total Requirment)")

DCP.Alk_Chemical.required=RangedValue("Required Alk",148, False, unit="mg/L as CaCO3")
DCP.Alk_Chemical.influent=RangedValue("Influent Alk",250, False, unit="mg/L as CaCO3")
DCP.Alk_Chemical.additional=RangedValue("Additional Alk",0, True, unit="mg/L as CaCO3")

DCP.CH3OH_Chemical.required=RangedValue("Required Carbon",158, False, unit="mg/L")
DCP.CH3OH_Chemical.influent=RangedValue("Influent BOD",207, False, unit="mg/L")
DCP.CH3OH_Chemical.additional=RangedValue("Additional Carbon",0, True, unit="mg/L")
DCP.CH3OH_Chemical.conc=RangedValue("CH3OH Conc",99, True, unit="%")

# ===== DSP 전용 DCR 저장 =====
# DSP 변수들을 사용한 DCR 저장
DCR.MLSS= RangedValue("MLSS", DSP.Design_Check.Operational_MLSS.value, False, 2000,4000,unit="mg/L", remark="MLSS of Designed Reactor")
DCR.MLVSS= RangedValue("MLVSS", DSP.Design_Check.Operational_MLVSS.value, False, 1500,3000,unit="mg/L", remark="MLVSS of Designed Reactor")
DCR.MLSSpMLVSS= RangedValue("MLVSS/MLSS", DSP.Biology.VSS_TSS_Ratio.value, False, 0.6,0.8,unit="-")
DCR.SRT= RangedValue("SRT", DSP.Biology.SRT_designed.value, False, 12,24,unit="d")
DCR.SNR= RangedValue("SNR", DSP.Nitrogen_Process.Designed_SNR.value, False, 0.04, 0.07, unit="gNH3-N/gMv/d")
DCR.SDNR= RangedValue("SDNR", DSP.Nitrogen_Process.Designed_SDNR.value, False, 0.05,0.15,unit="gNO3-N/gMv/d")
DCR.HRT= RangedValue("HRT", DSP.Design_Check.Designed_HRT.value, False, 12,30,unit="hr")
DCR.FM= RangedValue("F/M ratio", DSP.Design_Check.FM_ratio.value, False, 0.05,0.3,unit="kgBOD/kgMLVSS/d")
DCR.Fill= RangedValue("Fill Fraction", DSP.Design_Check.Designed_Fillratio*100, False, unit="%")


'''기계 작성 예시'''
# 1. 생물반응조 송풍기
DEP.Air_Blower.SOR_O2_per_day = SingleValue("SOR_O2_per_day", DSP.Aeration.SOR, False, unit="kgO2/d", remark = "지당 표준 산소요구량(SOR)")
DEP.Air_Blower.Temperature = SingleValue("Temperature", DSP.Water_Quality.Temp_Condition.value, False, unit="℃", remark = "설계 수온")
DEP.Air_Blower.EA_percent = SingleValue("EA_percent", 18.00, False, unit="%", remark = "산소전달율")
DEP.Air_Blower.Aeration_Depth = SingleValue("Aeration_Depth", 5.5, False, unit="m", remark = "폭기 수심")
DEP.Air_Blower.Operation_Time = SingleValue("Operation_Time", 10, True, unit="hr", remark = "가동시간")
DEP.Air_Blower.Device_number = SingleValue("Device_number", STC.flowtank.tank_number, True, unit="EA", remark = "가동대수")
DEP.Air_Blower.Safety_Factor = SingleValue("Safety_Factor", 20.00, True, unit="%", remark = "여유율")
DEP.Air_Blower.Pipe_length = SingleValue("Pipe_length", 100.00, True, unit="m", remark = "총배관 상당길이")
DEP.Air_Blower.Motor_Efficiency = SingleValue("Motor_Efficiency", 10, True, unit="%", remark = "전동기 여유율")

EQP.Air_Blower = EquipmentValue(
    name="생물반응조 송풍기",                        # 장비 이름
    code_key_list=["M_AEB0101"],                  # 장비 코드 그룹
    code_key="M_AEB0101",                         # 장비 코드
    inputs=DEP.Air_Blower,                        # 계산식 입력값들
    structure=STC.flowtank                        # 구조물 정보
)

# 2. 생물반응조 수중포기기
DEP.Aeration_Device.SOR_O2_per_day = SingleValue("SOR_O2_per_day", DSP.Aeration.SOR, False, unit="kgO2/d", remark = "지당 표준 산소요구량(SOR)")
DEP.Aeration_Device.Aeration_Depth = SingleValue("Aeration_Depth", STC.flowtank.water_level.value, True, unit="m", remark = "폭기 수심")
DEP.Aeration_Device.Operation_Time = SingleValue("Operation_Time", 10, True, unit="hr", remark = "가동시간")
DEP.Aeration_Device.Device_number = SingleValue("Device_number", STC.flowtank.tank_number, True, unit="EA", remark = "가동대수")
DEP.Aeration_Device.Tank_number = SingleValue("Tank_number", STC.flowtank.tank_number, False, unit="EA", remark = "조 수량")
DEP.Aeration_Device.width = SingleValue("width", STC.flowtank.W.value, True, remark = "조 너비")
DEP.Aeration_Device.length = SingleValue("length", STC.flowtank.L.value, True, remark = "조 길이")
DEP.Aeration_Device.water_level = SingleValue("water_level", STC.flowtank.height.value, True, remark = "조 높이")
DEP.Aeration_Device.Total_Tank_Volume = SingleValue("Total_Tank_Volume", DSP.Reactor.Final_Req_Vol, remark = "전체 조 용적")

# EquipmentValue 생성 (StructureValue에서 계산된 상세값 활용)
EQP.Aeration_Device = EquipmentValue(
    name="생물반응조 수중포기기",           # 장비 이름
    code_key_list=["M_AQR05"],              # 장비 코드 그룹
    code_key="M_AQR05",                         # 장비 코드
    inputs=DEP.Aeration_Device,                   # 계산식 입력값들
    structure=STC.flowtank,                       # 구조물 정보

)


# 3. 상등수 배출장치
# DCP.Floating_Decanter.Type = TextValue("Floating_Decanter", Floating_Decanter.Type, True, remark = "무동력부력식 배출장치")
DEP.Floating_Decanter.Inflow_Flowrate = SingleValue("Decanter_Flowrate", DSP.Water_Quality.Influent_q, False, unit="㎥/d", remark = "일 배출량")
DEP.Floating_Decanter.Discharge_Time = SingleValue("Discharge_Time", DSP.Operation.Sludge_discharge_time, False, unit="hr/Cycle", remark = "배출 시간")
DEP.Floating_Decanter.Drives_number = SingleValue("Drives_number", DSP.Operation.Number_of_Cycle_Per_day, True, unit="Cycle/d", remark = "일 운전 횟수")
DEP.Floating_Decanter.Device_number = SingleValue("Device_number", STC.flowtank.tank_number, True, unit="EA", remark = "가동대수")
DEP.Floating_Decanter.Safety_Factor = SingleValue("Safety_Factor", 20.00, True, unit="%", remark = "여유율")

EQP.Floating_Decanter = EquipmentValue(
    name="상등수 배출장치",
    code_key_list=["M_FDC01"],
    code_key="M_FDC01",
    inputs= DEP.Floating_Decanter,
    structure=STC.flowtank )

# 4. ★추가★ 밸브
DEP.Valve.diameter = EQP.Floating_Decanter.outputs.get("diameter",SingleValue("diameter", 150, False, unit="A", remark = "직경"))
DEP.Valve.Drives_number = SingleValue("Drives_number", DEP.Floating_Decanter.Drives_number.value, False, unit="EA", remark = "가동대수")

EQP.Valve = EquipmentValue(
    name="밸브",
    code_key_list=["M_VAV0201"],
    code_key="M_VAV0201",
    inputs= DEP.Valve,
    structure=STC.flowtank)

# 5. ★추가★ 공법제어반
DEP.Control_Panel.Drives_number = SingleValue("Drives_number", 1, True, unit="EA", remark = "가동대수")

EQP.Valve = EquipmentValue(
    name="공법제어반",
    code_key_list=["M_CTR01"],
    code_key="M_CTR01",
    inputs= DEP.Control_Panel,
    structure=STC.flowtank)

# 6. 잉여슬러지 배출펌프
# DCP.Sludge_Discharge_Pump.Type = TextValue("Spurt_Pump", Sludge_Discharge_Pump.Type, True, remark = "스프르트 펌프")
DEP.Sludge_Discharge_Pump.Pump_Flowrate = SingleValue("Pump_Flowrate", DSP.Sludge.Sludge_production_q.value, False, unit="㎥/d", remark = "유입량")
DEP.Sludge_Discharge_Pump.Solid_Concenctration = SingleValue("Solid_Concenctration", DSP.Sludge.Pump_inflow_solid_conc.value, False, unit="%", remark = "고형물 농도")
DEP.Sludge_Discharge_Pump.Operation_Time = SingleValue("Operation_Time", 0.3, True, unit="hr", remark = "가동시간")
DEP.Sludge_Discharge_Pump.Device_number = SingleValue("Device_number", 2, True, unit="EA", remark = "가동대수")
DEP.Sludge_Discharge_Pump.Specific_Gravity_Influent = SingleValue("Specific_Gravity_Influent", 1.0, False, unit="ton/㎥", remark = "비중")
DEP.Sludge_Discharge_Pump.Safety_Factor = SingleValue("Safety_Factor", 20.00, True, unit="%", remark = "여유율")
DEP.Sludge_Discharge_Pump.Total_Dynamic_Headd = SingleValue("Total_Dynamic_Head", 10.00, True, unit="m", remark = "실양정")
DEP.Sludge_Discharge_Pump.Pipe_length = SingleValue("Pipe_length", 50.00, True, unit="m", remark = "총배관 상당길이")
# DCP.Sludge_Discharge_Pump.Designed_friction_Loss_coefficien = SingleValue("Designed_friction_Loss_coefficien", 100.0, False, unit="-", remark = "고형물농도에 따른 계수")
# >> Sprut_Pump()에 DCP로 위의 계산값을 출력할 수 있는지
DEP.Sludge_Discharge_Pump.Pump_Efficiency = SingleValue("Pump_Efficiency", 37.6, False, unit="%", remark = "펌프 효율")

EQP.Sludge_Discharge_Pump = EquipmentValue(
    name="잉여슬러지 배출펌프",
    code_key_list=["M_PMP0601"],      # DropboxValue(), False,
    code_key="M_PMP0601",                        # 실제 기계 코드명
    inputs= DEP.Sludge_Discharge_Pump,
    structure=STC.flowtank )

calutemp = EQP.Sludge_Discharge_Pump.spare_count*2

# 구조물(Structure) 레이아웃 타입 선택 부분 
# # 펌프 타입 결정 테이블
tank_type_decision_table = {
    "name": "tank_type_decision",
    "table": {
        2: (StructureLayoutType.D_TYPE, 2),
        4: (StructureLayoutType.D_TYPE, 4),
        6: (StructureLayoutType.D_TYPE, 6),
        8: (StructureLayoutType.D_TYPE, 8),
        }
    }

STD.TankTypeTable = StandardTable(tank_type_decision_table)

if STC.flowtank.code_key == StructureType.CONCRETE_SQUARE.value:
    STC.flowtank.layout_type = STD.TankTypeTable.get_value(int(STC.flowtank.tank_number))[0]
    STC.flowtank.layout_type_number = STC.flowtank.tank_number
else:
    STC.flowtank.layout_type = StructureLayoutType.None_TYPE