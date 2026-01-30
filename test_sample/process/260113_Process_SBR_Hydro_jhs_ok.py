# 25.11.11 편집 : 부강 정지연
# 1. 부하(bodload), 농도(bod_공정명)으로 작성
# 2. UI 구성 시 ‘부하 → 농도’ 순으로 작성
# 3. ibod, sbod 성상 항목 추가
# 4. 제어반 코드 M_CTR01=>M_CTR0102로 수정함- by_이안_김성철_1205
# 5. MAP, 수리, 양정 (HWL 등) 코드 추가 : 부강 서준호

########################################

import WAI
# Edited: DSP, Info, UnitSystemType, INF 추가
from WAI import DCN, DCP, DEP, MAP, SingleValue, DropboxValue, RangedValue, Unit, DCR, DSP, EQP, EquipmentValue, HWL, StructureValue, STC, StructureType, TextValue, Info, UnitSystemType, INF, StandardTable, STD, StructureLayoutType, InfoValue, RawType #HWL
# Edited: 기계 계산식 및 구조물 계산식을 import할 필요가 없습니다.

# Edited: Info 공정 메타 정보 추가 (공정 코드, 단위계, 계산식 버전 등)
INF.Info = Info(process_code="SBR",
                unit_system=UnitSystemType.METRIC,
                formula_version="v2.0.0",
                author="서준호",
                date="2025-12-08")

import math


 # ★ 유출수 Q = 유입수 Q - 슬러지 Q이므로 
 # 각 성상에 대한 농도는 슬러지 농도 및 부하 산정 후 계산되어야 합니다.
 # 궁금한 점 → Threshold값을 지정해 반복 계산된다면, 
 # 파이썬 아래에 재선언된 변수가 파이썬 위에 위치한 동일 변수의 값 변경에 영향을 미치는 지 궁금합니다. (가능하다면 문제 X)


''' 설계조건 '''
DCN.influents.q=SingleValue("Q", 1317, False,"㎥/d", string_format="N2")
# 1. 부하 작성
DCN.influents.bodload=SingleValue("BOD", 272.619, True,"kg/d", string_format="N2")      
DCN.influents.ibodload=SingleValue("IBOD", 172.619, True,"kg/d", string_format="N2")
DCN.influents.sbodload=SingleValue("SBOD", 100, True,"kg/d", string_format="N2")
DCN.influents.codload=SingleValue("COD", 272.619, True,"kg/d", string_format="N2")
DCN.influents.tocload=SingleValue("TOC", 175.161, True,"kg/d", string_format="N2")
DCN.influents.ssload=SingleValue("SS", 233.109, True,"kg/d", string_format="N2")
DCN.influents.tnload=SingleValue("TN", 57.6846, True,"kg/d", string_format="N2")
DCN.influents.tpload=SingleValue("TP", 10.2726, True,"kg/d", string_format="N2")

# 2. 농도 작성
DCN.influents.bod=SingleValue("BOD", 2000, False,"mg/L", summary = True, string_format="N2")
DCN.influents.bod=DCN.influents.bodload.value/ DCN.influents.q.value *1000

DCN.influents.ibod=SingleValue("IBOD", 2000, False,"mg/L", summary = True, string_format="N2")
DCN.influents.ibod=DCN.influents.ibodload.value/ DCN.influents.q.value *1000

DCN.influents.sbod=SingleValue("SBOD", 2000, False,"mg/L", summary = True, string_format="N2")
DCN.influents.sbod=DCN.influents.sbodload.value/ DCN.influents.q.value *1000

DCN.influents.cod=SingleValue("COD", 300.0, False,"mg/L", summary = True, string_format="N2")
DCN.influents.cod=DCN.influents.codload.value/ DCN.influents.q.value *1000

DCN.influents.toc=SingleValue("TOC", 133.0, False,"mg/L", summary = True, string_format="N2")
DCN.influents.toc=DCN.influents.tocload.value/ DCN.influents.q.value *1000

DCN.influents.ss=SingleValue("SS", 172.0, False,"mg/L", summary = True, string_format="N2")
DCN.influents.ss=DCN.influents.ssload.value/ DCN.influents.q.value *1000

DCN.influents.tn=SingleValue("TN", 44.0, False,"mg/L", summary = True, string_format="N2")
DCN.influents.tn.value=DCN.influents.tnload.value/ DCN.influents.q.value *1000

DCN.influents.tp=SingleValue("TP", 8, False,"mg/L", summary = True, string_format="N2")
DCN.influents.tp=DCN.influents.tpload.value/ DCN.influents.q.value *1000

# DCN.influents.bodload=SingleValue("BOD Load", 207.0, False,"kg/d")
DCN.influents.temp=SingleValue("Temperature", 12, False, unit=Unit.CELSIUS)


'''유출수 정의'''
DCN.effluents.water.q = DCN.influents.q
DCN.effluents.sludge.q = DCN.influents.q

# 유출수 농도
DCN.effluents.water.bod=DCN.influents.bod
DCN.effluents.water.ibod=DCN.influents.ibod
DCN.effluents.water.sbod=DCN.influents.sbod
DCN.effluents.water.cod=DCN.influents.cod
DCN.effluents.water.toc=DCN.influents.toc
DCN.effluents.water.ss=DCN.influents.ss
DCN.effluents.water.tn=DCN.influents.tn
DCN.effluents.water.tp=DCN.influents.tp

# 유출수 부하
DCN.effluents.water.bodload = DCN.influents.bodload
DCN.effluents.water.ibodload = DCN.influents.ibodload
DCN.effluents.water.sbodload = DCN.influents.sbodload
DCN.effluents.water.codload = DCN.influents.codload
DCN.effluents.water.tocload= DCN.influents.tocload
DCN.effluents.water.ssload= DCN.influents.ssload
DCN.effluents.water.tnload= DCN.influents.tnload
DCN.effluents.water.tpload= DCN.influents.tpload

# SBR 제거효율
DCN.efficiency.bod=RangedValue("BOD", 98, True, 80, 99, unit="%")
DCN.efficiency.ibod=RangedValue("IBOD", 98, True, 80, 99, unit="%")
DCN.efficiency.sbod=RangedValue("SBOD", 98, True, 80, 99, unit="%")
DCN.efficiency.cod=RangedValue("COD", 98, True, 80, 95, unit="%")
DCN.efficiency.toc=RangedValue("TOC", 88, True, 70,90,unit="%")
DCN.efficiency.ss=RangedValue("SS", 92, True, 80,95,unit="%")
DCN.efficiency.tn=RangedValue("TN", 80, True, 70,90,unit="%")
DCN.efficiency.tp=RangedValue("TP", 79, True, 65,85,unit="%")

# 유출수 부하량(kg/d) = 유입수 부하량 * (1-제거효율)
DCN.effluents.water.bodload = DCN.influents.bodload - DCN.influents.bodload * (DCN.efficiency.bod * 0.01)
DCN.effluents.water.ibodload = DCN.influents.ibodload - DCN.influents.ibodload * (DCN.efficiency.ibod * 0.01)
DCN.effluents.water.sbodload = DCN.influents.sbodload - DCN.influents.sbodload * (DCN.efficiency.sbod * 0.01)
DCN.effluents.water.codload = DCN.influents.codload - DCN.influents.codload * (DCN.efficiency.cod * 0.01)
DCN.effluents.water.tocload = DCN.influents.tocload - DCN.influents.tocload * (DCN.efficiency.toc * 0.01)
DCN.effluents.water.ssload = DCN.influents.ssload - DCN.influents.ssload * (DCN.efficiency.ss *0.01)
DCN.effluents.water.tnload = DCN.influents.tnload -  DCN.influents.tnload * (DCN.efficiency.tn *0.01)
DCN.effluents.water.tpload =  DCN.influents.tpload -  DCN.influents.tpload * (DCN.efficiency.tp * 0.01)

# 유출수 농도(mg/L) =  부하량(kg/d) / 유량(㎥/d) * 1000
DCN.effluents.water.bod = DCN.effluents.water.bodload / DCN.effluents.water.q * 1000
DCN.effluents.water.ibod = DCN.effluents.water.ibodload / DCN.effluents.water.q * 1000
DCN.effluents.water.sbod = DCN.effluents.water.sbodload / DCN.effluents.water.q * 1000
DCN.effluents.water.cod = DCN.effluents.water.codload / DCN.effluents.water.q * 1000
DCN.effluents.water.toc = DCN.effluents.water.tocload / DCN.effluents.water.q * 1000
DCN.effluents.water.ss = DCN.effluents.water.ssload / DCN.effluents.water.q * 1000
DCN.effluents.water.tn.value = DCN.effluents.water.tnload / DCN.effluents.water.q * 1000
DCN.effluents.water.tp = DCN.effluents.water.tpload / DCN.effluents.water.q * 1000


'''슬러지 정의'''
# 슬러지 농도
DCN.effluents.sludge.q=DCN.influents.q
DCN.effluents.sludge.bod=DCN.influents.bod
DCN.effluents.sludge.ibod=DCN.influents.ibod
DCN.effluents.sludge.sbod=DCN.influents.sbod
DCN.effluents.sludge.cod=DCN.influents.cod
DCN.effluents.sludge.toc=DCN.influents.toc
DCN.effluents.sludge.ss=DCN.influents.ss
DCN.effluents.sludge.tn=DCN.influents.tn
DCN.effluents.sludge.tp=DCN.influents.tp

# 슬러지 부하
DCN.effluents.sludge.bodload = DCN.influents.bodload
DCN.effluents.sludge.ibodload = DCN.influents.ibodload
DCN.effluents.sludge.sbodload = DCN.influents.sbodload
DCN.effluents.sludge.codload = DCN.influents.codload
DCN.effluents.sludge.tocload= DCN.influents.tocload
DCN.effluents.sludge.ssload= DCN.influents.ssload
DCN.effluents.sludge.tnload= DCN.influents.tnload
DCN.effluents.sludge.tpload= DCN.influents.tpload

''' 설계인자 '''
DCP.Sludge.MLSS=RangedValue("MLSS", 3000, True, 1000, 5000,unit="mg/L", string_format="N2")
DCP.Sludge.Nitrifcation=RangedValue("Nitrifcation S.F", 1.3, True, 1, 1.5,unit="-")
DCP.Sludge.SVI=RangedValue("SVI",100, True, 50, 120,unit="ml/g")
DCP.Sludge.DecantSF=RangedValue("Decant S.F", 1.3, True, 1.0, 1.5, unit="-", remark="Decanting Safety Factor")

DCP.Kinetic_Coeffient.m=RangedValue("㎛", 6, True, 3, 13.2,unit="gVSS/gVSS/d", remark="Hetrotroph (20 ℃)")
DCP.Kinetic_Coeffient.ks=RangedValue("Ks",20, True, 5, 40,unit="mg bCOD/L", remark="Hetrotroph (20 ℃)")
DCP.Kinetic_Coeffient.y=RangedValue("Y",0.4, True, 0.3, 0.5,unit="gVSS/g bCOD", remark="Hetrotroph (20 ℃)")
DCP.Kinetic_Coeffient.kd=RangedValue("kd",0.12, True, 0.06, 0.2,unit="gVSS/gVSS/d", remark="Hetrotroph (20 ℃)")
DCP.Kinetic_Coeffient.fd=RangedValue("fd",0.15, True, 0.08, 0.2,unit="-", remark="Hetrotroph (20 ℃)")
DCP.Kinetic_Coeffient.thofm=RangedValue("θ of ㎛",1.07, True, 1.03, 1.08,unit="", remark="Hetrotroph (20 ℃)")
DCP.Kinetic_Coeffient.thofkd=RangedValue("θ of Kd",1.04, True, 1.03, 1.08,unit="", remark="Hetrotroph (20 ℃)")
DCP.Kinetic_Coeffient.thofks=RangedValue("θ of Ks",1, True, 1, 1,unit="", remark="Hetrotroph (20 ℃)")

DCP.Kinetic_Coeffient.mn=RangedValue("㎛n",0.75, True, 0.2, 0.9,unit="gVSS/gVSS/d", remark="Autotroph (20 ℃)")
DCP.Kinetic_Coeffient.kn=RangedValue("Kn",0.74, True, 0.5, 1,unit="mgNH4-N/L", remark="Autotroph (20 ℃)")
DCP.Kinetic_Coeffient.yn=RangedValue("Yn",0.12, True, 0.1, 0.15,unit="gVSS/gNH4-N", remark="Autotroph (20 ℃)")
DCP.Kinetic_Coeffient.kdn=RangedValue("kdn",0.08, True, 0.05, 0.15,unit="gVSS/gVSS/d", remark="Autotroph (20 ℃)")
DCP.Kinetic_Coeffient.ko=RangedValue("Ko",0.5, True, 0.4, 0.6,unit="mg/L", remark="Autotroph (20 ℃)")
DCP.Kinetic_Coeffient.thofmn=RangedValue("θ of ㎛",1.07, True, 1.06, 1.12,unit="", remark="Autotroph (20 ℃)")
DCP.Kinetic_Coeffient.thofkdn=RangedValue("θ of Kd",1.05, True, 1.03, 1.12,unit="", remark="Autotroph (20 ℃)")
DCP.Kinetic_Coeffient.thofksn=RangedValue("θ of Ks",1.04, True, 1.03, 1.08,unit="", remark="Autotroph (20 ℃)")

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
DSP.Water_Quality.Influent_alk = SingleValue("Influent_alk", 250, False, unit="mg/L as CaCO3")

DSP.Water_Quality.Temp_Condition.value = DCN.influents.temp.value
DSP.Water_Quality.Influent_q.value = DCN.influents.q.value
DSP.Water_Quality.Infleunt_TN.value = DCN.influents.tn.value          

# DSP.Water_Quality.Influent_alk = DCN.influents.Influent_alk # DCN에 등록될 경우


# 3. 설계 파라미터 관련 변수들 
DSP.Design_Parameters.DO_basin = SingleValue("DO_basin", 2.0, False, unit="mg/L")
DSP.Design_Parameters.Nitrification_SF = SingleValue("Nitrification_SF", 2.5, False, unit="-")
DSP.Design_Parameters.BDCOD_ratio = SingleValue("BDCOD_ratio", 0.8, False, unit="-")

DSP.Design_Parameters.DO_basin.value = DCP.ETC.DO_in_Basin.value
DSP.Design_Parameters.Nitrification_SF.value = DCP.Sludge.Nitrifcation.value
DSP.Design_Parameters.BDCOD_ratio.value = DCP.ETC.BDCOD_ratio.value


# 4. 유출수질 관련 변수들
DSP.Effluent_Quality.Effluent_NO3 = SingleValue("Effluent_NO3", 10, False, unit="mg/L", remark="유출수 질산성질소")
DSP.Effluent_Quality.Effluent_NH4 = SingleValue("Effluent_NH4", 1, False, unit="mg/L", remark="유출수 암모니아성질소")
DSP.Effluent_Quality.Effluent_orgN = SingleValue("Effluent_orgN", 1, False, unit="mg/L", remark="유출수 유기질소")

DSP.Effluent_Quality.Effluent_NO3.value = DCN.effluents.water.tn - DCP.ETC.EffluentOrgN - DCP.ETC.EffluentNH4     # ★DCN.effluents.water.tn은 line 512의 다시 재선언된 값이 실제값입니다.
DSP.Effluent_Quality.Effluent_NH4.value = DCP.ETC.EffluentNH4.value

# 5. 기타 계산된 변수들
DSP.Calculated.Effluent_TN = SingleValue("Effluent_TN", 12, False, unit="mg/L", remark="유출수 총질소")
DSP.Calculated.Effluent_TN.value = DCN.effluents.water.tn.value                                                    # ★DCN.effluents.water.tn은 line 512의 다시 재선언된 값이 실제값입니다.

# 6. 슬러지 관련 변수들
DSP.Sludge.Setting_MLSS = SingleValue("Setting_MLSS", 3000, False, unit="mg/L", remark="설정 MLSS", string_format="N2")
DSP.Sludge.Setting_MLSS.value = DCP.Sludge.MLSS.value


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

DSP.Kinetics.m_hetero_design_temp.value = DCP.Kinetic_Coeffient.m * DCP.Kinetic_Coeffient.thofm ** (DCN.influents.temp - 20)
DSP.Kinetics.ks_hetero_design_temp.value = DCP.Kinetic_Coeffient.ks * DCP.Kinetic_Coeffient.thofks ** (DCN.influents.temp - 20)
DSP.Kinetics.yield_hetero_design_temp.value = DCP.Kinetic_Coeffient.y.value
DSP.Kinetics.kd_hetero_design_temp.value = DCP.Kinetic_Coeffient.kd * DCP.Kinetic_Coeffient.thofkd ** (DCN.influents.temp - 20)
DSP.Kinetics.fd_hetero_design_temp.value = DCP.Kinetic_Coeffient.fd.value


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

DSP.Kinetics.mn_auto_design_temp.value = DCP.Kinetic_Coeffient.mn * DCP.Kinetic_Coeffient.thofmn ** (DCN.influents.temp - 20)
DSP.Kinetics.kn_auto_design_temp.value = DCP.Kinetic_Coeffient.kn * DCP.Kinetic_Coeffient.thofkdn ** (DCN.influents.temp - 20)
DSP.Kinetics.yn_auto_design_temp.value = DCP.Kinetic_Coeffient.yn.value
DSP.Kinetics.kdn_auto_design_temp.value = DCP.Kinetic_Coeffient.kdn * DCP.Kinetic_Coeffient.thofksn ** (DCN.influents.temp - 20)
DSP.Kinetics.ko_auto_design_temp.value = DCP.Kinetic_Coeffient.ko.value


''' A-1. 운전주기 결정 '''

# ===== DSP 통합 제안 =====
DSP.Operation.Reaction_time_aCycle = SingleValue("Reaction_time_aCycle", 0, False, unit="hr", remark="1Cycle당 총 운전시간")
DSP.Operation.Aeration_time_aCycle = SingleValue("Aeration_time_aCycle", 0, False, unit="hr", remark="1Cycle당 포기시간")
DSP.Operation.Number_of_Cycle_Per_day = SingleValue("Number_of_Cycle_Per_day", 0, False, unit="Cycle/d", remark="1지 운전주기")
DSP.Operation.Fillvolume = SingleValue("Fillvolume", 0, False, unit="㎥/cycle", remark="1Cycle당 Fill Volume")

DSP.Operation.Reaction_time_aCycle.value = DCP.Operation_Cycle.Total / 60
DSP.Operation.Aeration_time_aCycle.value = DCP.Operation_Cycle.Aeration / 60
DSP.Operation.Number_of_Cycle_Per_day.value = 24 / (DCP.Operation_Cycle.Total / 60)
DSP.Operation.Fillvolume.value = DSP.Water_Quality.Influent_q / DSP.Operation.Number_of_Cycle_Per_day
#print(DSP.Operation.Number_of_Cycle_Per_day.value) → OK
#print(DSP.Operation.Fillvolume.value) → OK

''' A-2. 한 주기당 허용 유입분율(VF/VT) 결정 '''
# ===== DSP 변환 제안 =====
DSP.Sludge.Xs = SingleValue("Xs", 0, False, unit="mg/L")
DSP.Sludge.Setting_Ratio = SingleValue("Setting_Ratio", 0, False, unit="-")
DSP.Sludge.Min_fill_ratio = SingleValue("Min_fill_ratio", 0, False, unit="-")       # 유입분율 최대
DSP.Reactor.Fill_ratio_Reactor_Req_Vol = SingleValue("Fill_ratio_Reactor_Req_Vol", 0, False, unit="㎥")

DSP.Sludge.Xs.value = 1000 * 1000 / DCP.Sludge.SVI
DSP.Sludge.Setting_Ratio.value = DCP.Sludge.MLSS / DSP.Sludge.Xs * DCP.Sludge.DecantSF
DSP.Sludge.Min_fill_ratio.value = 1 - DSP.Sludge.Setting_Ratio
DSP.Reactor.Fill_ratio_Reactor_Req_Vol.value = DSP.Operation.Fillvolume / DSP.Sludge.Min_fill_ratio
# print(DSP.Reactor.Fill_ratio_Reactor_Req_Vol.value) → OK


''' A-4. 슬러지 HRT(SRT) 결정'''
# ===== DSP 변환 제안 =====
DSP.Biology.Specificgrowthrate_Auto = SingleValue("Specificgrowthrate_Auto", 0, False, unit="g/g/d")
DSP.Biology.SRTmin = SingleValue("SRTmin", 0, False, unit="d")
DSP.Biology.SRT_designed = SingleValue("SRT_designed", 0, False, unit="d")
DSP.Sludge.Solid_Concentration = SingleValue("Solid_Concentration", 0, False, unit="mg/L")
DSP.Sludge.Pump_inflow_solid_conc = SingleValue("Pump_inflow_solid_conc", 0, False, unit="%")

DSP.Biology.Specificgrowthrate_Auto.value = (DSP.Kinetics.mn_auto_design_temp * 1) / (DSP.Kinetics.kn_auto_design_temp + 1) * (DSP.Design_Parameters.DO_basin) / (DSP.Kinetics.ko_auto_design_temp + DSP.Design_Parameters.DO_basin) - DSP.Kinetics.kdn_auto_design_temp
DSP.Biology.SRTmin.value = 1 / DSP.Biology.Specificgrowthrate_Auto.value
DSP.Biology.SRT_designed.value = DSP.Design_Parameters.Nitrification_SF * DSP.Biology.SRTmin * DSP.Operation.Reaction_time_aCycle / DSP.Operation.Aeration_time_aCycle
DSP.Sludge.Solid_Concentration.value = DCN.effluents.sludge.ss.value          # ★DCN.effluents.sludge.ss은 line 512 다시 재선언된 값이 실제값입니다.
DSP.Sludge.Pump_inflow_solid_conc.value = DCN.effluents.water.ss / 10000      # ★DCN.effluents.sludge.ss은 line 512 다시 재선언된 값이 실제값입니다.
#print(DSP.Biology.Specificgrowthrate_Auto.value) → OK
#print(DSP.Biology.SRTmin.value) → OK
#print(DSP.Biology.SRT_designed.value) → OK


''' A-5. 일일 순미생물생성량 산정'''
# ===== DSP 변환 제안 =====
DSP.Biology.Influent_VSS = SingleValue("Influent_VSS", 0, False, unit="mg/L")
DSP.Biology.Influent_nbVSS = SingleValue("Influent_nbVSS", 0, False, unit="mg/L")
DSP.Biology.S = SingleValue("S", 0, False, unit="mg bsCOD/L")
DSP.Biology.Infleunt_NOx = SingleValue("Infleunt_NOx", 0, False, unit="mg/L")

DSP.Biology.Influent_VSS = DCN.influents.ss * 0.9
DSP.Biology.Influent_nbVSS = (1-DCP.ETC.bpCOD_pCOD_ratio) * DSP.Biology.Influent_VSS
DSP.Biology.S = DSP.Kinetics.ks_hetero_design_temp * (1 + DSP.Kinetics.kd_hetero_design_temp * DSP.Biology.SRT_designed) / (DSP.Biology.SRT_designed * (DSP.Kinetics.m_hetero_design_temp - DSP.Kinetics.kd_hetero_design_temp) -1)
DSP.Biology.Infleunt_NOx = DCN.influents.tn.value * (DSP.Effluent_Quality.Effluent_NO3 / DSP.Calculated.Effluent_TN)
#print(DSP.Biology.Influent_VSS.value) → OK
#print(DSP.Biology.Influent_nbVSS.value) → OK
#print(DSP.Biology.S.value) → OK
#print(DSP.Biology.Infleunt_NOx.value) → OK


''' A-6. 슬러지 생산량, 반응 중 MLSS 및 MLVSS 결정'''
# ===== DSP 변환 제안 =====
DSP.Biology.Act_Biomass = SingleValue("Activated microbial mass", 0, False, unit="kg/d")
DSP.Biology.Endogenous_respiration_Biomass = SingleValue("Endogenous respiration biomass", 0, False, unit="kg/d")
DSP.Biology.Nonbiodegradable_SS = SingleValue("Nonbiodegradable SS", 0, False, unit="kg/d")
DSP.Biology.nbVSS_Mass = SingleValue("nbVSS_Mass", 0, False, unit="kg/d")
DSP.Biology.PxVSS = SingleValue("PxVSS", 0, False, unit="kg/d")
DSP.Biology.PxTSS = SingleValue("PxTSS", 0, False, unit="kg/d")
DSP.Biology.Xvss_V = SingleValue("Xvss_V", 0, False, unit="kg VSS")
DSP.Biology.Xtss_V = SingleValue("Xtss_V", 0, False, unit="kg SS")
DSP.Biology.VSS_TSS_Ratio = SingleValue("VSS_TSS_Ratio", 0, False, unit="-")

DSP.Biology.Act_Biomass.value = DSP.Water_Quality.Influent_q * DSP.Kinetics.yield_hetero_design_temp * (DCN.influents.bod * DSP.Design_Parameters.BDCOD_ratio - DSP.Biology.S) / (1+ DSP.Biology.SRT_designed * DSP.Kinetics.kd_hetero_design_temp) / 1000
DSP.Biology.Endogenous_respiration_Biomass.value = DSP.Kinetics.fd_hetero_design_temp * DSP.Kinetics.kd_hetero_design_temp * DSP.Water_Quality.Influent_q * DSP.Kinetics.yield_hetero_design_temp * (DCN.influents.bod.value * DSP.Design_Parameters.BDCOD_ratio - DSP.Biology.S) * DSP.Biology.SRT_designed /1000/ (1+DSP.Kinetics.kd_hetero_design_temp*DSP.Biology.SRT_designed)
DSP.Biology.Nonbiodegradable_SS.value = DSP.Water_Quality.Influent_q * DSP.Kinetics.yn_auto_design_temp * DSP.Biology.Infleunt_NOx / (1+ DSP.Kinetics.kdn_auto_design_temp*DSP.Biology.SRT_designed)/1000
DSP.Biology.nbVSS_Mass.value = DSP.Water_Quality.Influent_q * DSP.Biology.Influent_nbVSS / 1000
DSP.Biology.PxVSS.value = DSP.Biology.Act_Biomass + DSP.Biology.Endogenous_respiration_Biomass + DSP.Biology.Nonbiodegradable_SS + DSP.Biology.nbVSS_Mass
DSP.Biology.PxTSS.value = (DSP.Biology.Act_Biomass + DSP.Biology.Endogenous_respiration_Biomass + DSP.Biology.Nonbiodegradable_SS)/0.85 + DSP.Biology.nbVSS_Mass + DSP.Water_Quality.Influent_q*(DCN.influents.ss.value - DSP.Biology.Influent_VSS)/1000
DSP.Biology.Xvss_V.value = DSP.Biology.PxVSS * DSP.Biology.SRT_designed
DSP.Biology.Xtss_V.value = DSP.Biology.PxTSS * DSP.Biology.SRT_designed
DSP.Biology.VSS_TSS_Ratio.value = DSP.Biology.Xvss_V / DSP.Biology.Xtss_V
#print(DSP.Biology.Act_Biomass) → OK
#print(DSP.Biology.Endogenous_respiration_Biomass.value) → OK
#print(DSP.Biology.Nonbiodegradable_SS.value) → OK
#print(DSP.Biology.nbVSS_Mass.value) → OK
#print(DSP.Biology.PxVSS.value) → OK
#print(DSP.Biology.PxTSS.value) → OK
#print(DSP.Biology.Xvss_V.value) → OK
#print(DSP.Biology.Xtss_V.value) → OK
#print(DSP.Biology.VSS_TSS_Ratio.value) → OK

# 잉여슬러지 발생량
DSP.Sludge.Sludge_production_q = SingleValue("Sludge_production_q", 0, False, unit="㎥/d")
DSP.Operation.Sludge_discharge_time = SingleValue("Sludge discharge time", 0, False, unit="min")
DSP.Reactor.MLSS_Sustain_Reactor_Req_Vol = SingleValue("MLSS_Sustain_Reactor_Req_Vol", 0, False, unit="㎥")
DSP.Reactor.Final_Req_Vol = SingleValue("Final_Req_Vol", 0, False, unit="㎥")

DSP.Sludge.Sludge_production_q.value = DSP.Biology.PxTSS * 1000 / DSP.Sludge.Xs
DSP.Operation.Sludge_discharge_time = (DCP.Operation_Cycle.Sludge/60)* DSP.Operation.Number_of_Cycle_Per_day * 60
DSP.Reactor.MLSS_Sustain_Reactor_Req_Vol = DSP.Biology.Xtss_V * 1000 / DSP.Sludge.Setting_MLSS
DSP.Reactor.Final_Req_Vol = max(DSP.Reactor.MLSS_Sustain_Reactor_Req_Vol.value, DSP.Reactor.Fill_ratio_Reactor_Req_Vol.value)

#print(DSP.Reactor.MLSS_Sustain_Reactor_Req_Vol.value) → OK
#print(DSP.Reactor.Final_Req_Vol.value) → OK


# ★ 슬러지의 ibod, sbod 부하를 계산하기 위해
# 유입수의 Inert, Soluble 비율을 활용하였습니다.
DCP.BOD.inertbod_ratio=RangedValue("Inert Ratio", 64, True, 0, 99,unit="%") #BOD Inert비율
DCP.BOD.Soluble_Ratio=RangedValue("Soluble Ratio", 100-DCP.BOD.inertbod_ratio.value, False, 1, 99,unit="%") #BOD Soluble비율
DCP.BOD.Soluble_Ratio=100-DCP.BOD.inertbod_ratio

# 슬러지 부하량(kg/d)
DCN.effluents.sludge.ssload = DSP.Biology.PxTSS.value
DCN.effluents.sludge.bodload = DCN.effluents.sludge.ssload* 1.42/1.72
DCN.effluents.sludge.ibodload = DCN.effluents.sludge.bodload * 0.3
DCN.effluents.sludge.sbodload = DCN.effluents.sludge.sbodload * 0.7
DCN.effluents.sludge.codload = DCN.effluents.sludge.bodload * 0.75
DCN.effluents.sludge.tocload = DCN.effluents.sludge.bodload * 0.75
DCN.effluents.sludge.tnload= DSP.Biology.PxVSS * 0.12  # 수정
DCN.effluents.sludge.tpload = DCN.influents.tpload - DCN.effluents.water.tpload

# 슬러지 농도(mg/L)
DCN.effluents.sludge.q = DSP.Sludge.Sludge_production_q.value
DCN.effluents.sludge.bod = DCN.effluents.sludge.bodload / DSP.Sludge.Sludge_production_q * 1000 
DCN.effluents.sludge.ibod = DCN.effluents.sludge.ibodload / DSP.Sludge.Sludge_production_q * 1000 
DCN.effluents.sludge.sbod = DCN.effluents.sludge.sbodload / DSP.Sludge.Sludge_production_q * 1000 
DCN.effluents.sludge.cod = DCN.effluents.sludge.codload / DSP.Sludge.Sludge_production_q * 1000
DCN.effluents.sludge.toc = DCN.effluents.sludge.tocload / DSP.Sludge.Sludge_production_q * 1000
DCN.effluents.sludge.ss = DCN.effluents.sludge.ssload / DSP.Sludge.Sludge_production_q * 1000
DCN.effluents.sludge.tn = DCN.effluents.sludge.tnload/ DSP.Sludge.Sludge_production_q * 1000
DCN.effluents.sludge.tp = DCN.effluents.sludge.tpload / DSP.Sludge.Sludge_production_q * 1000


# 위에서 계산된 유출수의 농도 재계산(유량값이 달라짐)
DCN.effluents.water.q.value = DCN.influents.q - DCN.effluents.sludge.q

DCN.effluents.water.bod = DCN.effluents.water.bodload / DCN.effluents.water.q * 1000
DCN.effluents.water.ibod = DCN.effluents.water.ibodload / DCN.effluents.water.q * 1000
DCN.effluents.water.sbod = DCN.effluents.water.sbodload / DCN.effluents.water.q * 1000
DCN.effluents.water.cod = DCN.effluents.water.codload / DCN.effluents.water.q * 1000
DCN.effluents.water.toc = DCN.effluents.water.tocload / DCN.effluents.water.q * 1000
DCN.effluents.water.ss = DCN.effluents.water.ssload / DCN.effluents.water.q * 1000
DCN.effluents.water.tn = DCN.effluents.water.tnload / DCN.effluents.water.q * 1000
DCN.effluents.water.tp = DCN.effluents.water.tpload / DCN.effluents.water.q * 1000




# 4. 유출수질 관련 변수들
DSP.Effluent_Quality.Effluent_NO3 = SingleValue("Effluent NO3", 10, False, unit="mg/L", remark="유출수 질산성질소")
DSP.Effluent_Quality.Effluent_NH4 = SingleValue("Effluent NH4", 1, False, unit="mg/L", remark="유출수 암모니아성질소")
DSP.Effluent_Quality.Effluent_orgN = SingleValue("Effluent orgN", 1, False, unit="mg/L", remark="유출수 유기질소")
DSP.Water_Quality.Delta_BOD = SingleValue("Delta_BOD", 200, False, unit="mg/L")

DSP.Effluent_Quality.Effluent_NO3 = DCN.effluents.water.tn - DCP.ETC.EffluentOrgN - DCP.ETC.EffluentNH4
#print(DSP.Effluent_Quality.Effluent_NO3)
#print(DCP.ETC.EffluentOrgN)
#print(DCP.ETC.EffluentNH4)
DSP.Effluent_Quality.Effluent_NH4 = DCP.ETC.EffluentNH4.value
DSP.Water_Quality.Delta_BOD = DCN.influents.bod - DCN.effluents.water.bod    

# 5. 기타 계산된 변수들
DSP.Calculated.Effluent_TN = SingleValue("Effluent TN", 12, False, unit="mg/L", remark="유출수 총질소")
DSP.Calculated.Effluent_TN = DCN.effluents.water.tn.value

# 6. 슬러지 관련 변수들
DSP.Sludge.Setting_MLSS = SingleValue("Setting MLSS", 3000, False, unit="mg/L", remark="설정 MLSS", string_format="N2")
DSP.Sludge.Setting_MLSS = DCP.Sludge.MLSS.value

''' A-7. 반응조 용량 결정 - DSP 전용 계산 체계 '''
STC.flowtank = StructureValue(
    name="SBR tank",
    code_key_list=[StructureType.CONCRETE_SQUARE],
    code_key=StructureType.CONCRETE_SQUARE,
    tank_number_list=[2, 4, 6, 8],  # 구조물 지수 목록, 첫번째 지수가 tank_number 기본값으로 등록
    water_level= 5,
    height= 6,
    required_capacity=DSP.Reactor.Final_Req_Vol.value,
    inputs=DSP.flowtank)

STC.flowtank.required_capacity = DSP.Reactor.Final_Req_Vol.value

DSP.flowtank.water_level_after = SingleValue(".", 5, False, unit=".", remark=".") #반응조 배출 후 수위
DSP.flowtank.water_level_after.value = STC.flowtank.water_level.value - 2

#print(STC.flowtank.W)  #→ NO ★
#print(STC.flowtank.L) #→ NO ★
#print(STC.flowtank.water_level) #→ NO ★
#print(STC.flowtank.tank_number) #→ OK
#print(STC.flowtank.applied_capacity) #→ NO ★

''' A-8. 설계검토(MLSS, F/M, HRT) '''
# 2. DSP 변수들 정의
DSP.Design_Check.Operational_MLSS = SingleValue("Operational MLSS", 1, False, unit="mg/L", remark="운전 MLSS", string_format="N2")
DSP.Design_Check.Operational_MLVSS = SingleValue("Operational MLVSS", 1, False, unit="mg/L", remark="운전 MLVSS", string_format="N2")
DSP.Design_Check.FM_ratio = SingleValue("FM ratio", 1, False, unit="-", remark="F/M 비율")
DSP.Design_Check.Designed_HRT = SingleValue("Designed HRT", 0, False, unit="hr", remark="설계 HRT")
DSP.Design_Check.Designed_Fillratio = SingleValue("Designed Fillratio", 0, False, unit="-", remark="설계 충전비율")
                        
DSP.Design_Check.Operational_MLSS.value = round(DSP.Biology.Xtss_V *1000 / STC.flowtank.applied_capacity)
DSP.Design_Check.Operational_MLVSS.value =round(DSP.Design_Check.Operational_MLSS * DSP.Biology.VSS_TSS_Ratio)
DSP.Design_Check.FM_ratio.value = DSP.Water_Quality.Influent_q * (DSP.Water_Quality.Delta_BOD) / (STC.flowtank.applied_capacity*DSP.Design_Check.Operational_MLVSS)
DSP.Design_Check.Designed_HRT.value =  STC.flowtank.applied_capacity / (DSP.Water_Quality.Influent_q / 24)
DSP.Design_Check.Designed_Fillratio.value =DSP.Operation.Fillvolume / STC.flowtank.applied_capacity

#print(DSP.Design_Check.Operational_MLSS.value) → ▲
#print(DSP.Design_Check.Operational_MLVSS.value) → ▲
#print(DSP.Design_Check.FM_ratio.value) → OK
#print(DSP.Design_Check.Designed_HRT.value) → ▲
#print(DSP.Design_Check.Designed_Fillratio.value) → ▲


''' A-10. 질소 Balance '''
# 2. DSP 변수들 정의
DSP.Nitrogen_Balance.Xn = SingleValue("Xn", 0, False, unit="mg/L", remark="질산화미생물 농도")
DSP.Nitrogen_Balance.NH4_conc_for_nitrification = SingleValue("NH4_conc_for_nitrification", 0, False, unit="mg NOx/L", remark="질산화용 NH4-N 농도")
DSP.Nitrogen_Balance.Vf_NOx = SingleValue("Vf_NOx", 0, False, unit="kg/fill", remark="주기당 NH4-N 부하량") 

#NH4 Loading Before Fill
DSP.Nitrogen_Balance.Xn = (DSP.Water_Quality.Influent_q *DSP.Kinetics.yn_auto_design_temp*DSP.Biology.Infleunt_NOx*DSP.Biology.SRT_designed)/(1+DSP.Kinetics.kdn_auto_design_temp*DSP.Biology.SRT_designed)/STC.flowtank.required_capacity
DSP.Nitrogen_Balance.NH4_conc_for_nitrification = DSP.Water_Quality.Infleunt_TN-DSP.Effluent_Quality.Effluent_NH4-(0.12*(DSP.Biology.Act_Biomass + DSP.Biology.Endogenous_respiration_Biomass + DSP.Biology.Nonbiodegradable_SS)/DSP.Water_Quality.Influent_q * 1000)
DSP.Nitrogen_Balance.Vf_NOx = (DSP.Operation.Fillvolume/STC.flowtank.tank_number)*DSP.Nitrogen_Balance.NH4_conc_for_nitrification/1000
#print(DSP.Nitrogen_Balance.Xn.value) → ▲
#print(DSP.Nitrogen_Balance.NH4_conc_for_nitrification.value) → OK
#print(DSP.Nitrogen_Balance.Vf_NOx.value)  → OK


''' A-12. 질산화율(SNR), 탈질율(SDNR) '''
# 2. DSP 변수들 정의
DSP.Nitrogen_Process.Nitrified_TN = SingleValue("Nitrified_TN", 0, False, unit="kg/d", remark="질산화된 총질소")
DSP.Nitrogen_Process.Denitrified_TN = SingleValue("Denitrified_TN", 0, False, unit="kg/d", remark="탈질된 총질소")
DSP.Nitrogen_Process.total_MLVSS_in_reactor = SingleValue("total MLVSS in reactor", 0, False, unit="kgMLVSS", remark="반응조 내 총 MLVSS")
DSP.Nitrogen_Process.Total_Aeration_Time = SingleValue("Total Aeration Time", 0, False, unit="hr", remark="총 포기시간")
DSP.Nitrogen_Process.Total_Anoxic_Time = SingleValue("Total Anoxic Time", 0, False, unit="hr", remark="총 무산소시간")
DSP.Nitrogen_Process.Designed_SNR = SingleValue("Designed SNR", 0, False, unit="gNH3-N/gMv/d", remark="설계 질산화율")
DSP.Nitrogen_Process.Designed_SDNR = SingleValue("Designed SDNR", 0, False, unit="gNOx-N/gMv/d", remark="설계 탈질율")

DSP.Nitrogen_Process.Nitrified_TN.value = DSP.Nitrogen_Balance.NH4_conc_for_nitrification * DSP.Water_Quality.Influent_q / 1000
DSP.Nitrogen_Process.Denitrified_TN.value = (DSP.Nitrogen_Balance.NH4_conc_for_nitrification - DSP.Effluent_Quality.Effluent_NO3) * DSP.Water_Quality.Influent_q / 1000
DSP.Nitrogen_Process.total_MLVSS_in_reactor.value = DSP.Design_Check.Operational_MLVSS/1000 * STC.flowtank.required_capacity
DSP.Nitrogen_Process.Total_Aeration_Time.value = DSP.Operation.Aeration_time_per_cycle / 60 * DSP.Operation.Number_of_Cycle_Per_day
DSP.Nitrogen_Process.Total_Anoxic_Time.value = DSP.Operation.Anoxic_time_per_cycle / 60 * DSP.Operation.Number_of_Cycle_Per_day
DSP.Nitrogen_Process.Designed_SNR.value = DSP.Nitrogen_Process.Nitrified_TN / DSP.Nitrogen_Process.total_MLVSS_in_reactor / (DSP.Nitrogen_Process.Total_Aeration_Time / 24)
DSP.Nitrogen_Process.Designed_SDNR.value = DSP.Nitrogen_Process.Denitrified_TN / DSP.Nitrogen_Process.total_MLVSS_in_reactor / (DSP.Nitrogen_Process.Total_Anoxic_Time / 24)
#print(DSP.Nitrogen_Process.Nitrified_TN.value)  → OK
#print(DSP.Nitrogen_Process.Denitrified_TN.value)  → OK
#print(DSP.Nitrogen_Process.total_MLVSS_in_reactor.value) → ▲
#print(DSP.Nitrogen_Process.Total_Aeration_Time.value)  → OK
#print(DSP.Nitrogen_Process.Total_Anoxic_Time.value)  → OK
#print(DSP.Nitrogen_Process.Designed_SNR.value)  → OK
#print(DSP.Nitrogen_Process.Designed_SDNR.value)  → OK


# 3. DCP에 저장
DCP.Aeration.total_time = SingleValue("Total_Aeration_Time", DSP.Nitrogen_Process.Total_Aeration_Time, False, "hr")
# 제거 BOD 당 필요한 산소량(0.5~0.7)
DCP.Aeration.A=RangedValue("A",0.6, True,0.5,0.7, unit="kgO2/kgBOD", remark="Required O2 / Removed BOD")
# 탈질에 의해 소비된 BOD량
DCP.Aeration.K=RangedValue("K",2.86, True, unit="kgBOD/kgN", remark="BOD consumed by Denitrifcation")
# Unit MLVSS 당 내생호흡에 의한 산소소비량(0.05~0.15)
DCP.Aeration.B=RangedValue("B",0.1, True,0.05,0.15, unit="kgO2/kgMLVSS/d", remark="Consumed O2 per MLVSS due to Endogenous Respiration")
# 질산화 반응에 따라 소비된 산소량
DCP.Aeration.C=RangedValue("C",4.57, True, unit="kgO2/kgN", remark="Consumed O2 Per Nitrificaiton")
# 청수에 대한 산소전달률
DCP.Aeration.Ea=RangedValue("Ea",18, True, unit="%", remark="OTE of Clean Water")
# 송풍량 여유율
DCP.Aeration.Safety=RangedValue("Safety Factor",0, True, unit="%", remark="Safety Factor of Gs")
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
DSP.Aeration.OD1.value = A * ((DSP.Water_Quality.Delta_BOD.value * DSP.Water_Quality.Influent_q.value / 1000) - DSP.Nitrogen_Process.Denitrified_TN * K)
#print(DSP.Aeration.OD1.value)   → OK

B = DCP.Aeration.B
DSP.Aeration.Va = STC.flowtank.required_capacity * (DSP.Operation.Aeration_time_per_cycle * DSP.Operation.Number_of_Cycle_Per_day / 24 / 60)
DSP.Aeration.MLVSS_Mass = DSP.Design_Check.Operational_MLVSS / 1000
DSP.Aeration.OD2.value = B * DSP.Aeration.Va * DSP.Aeration.MLVSS_Mass
#print(DSP.Aeration.Va.value) → ▲
#print(DSP.Aeration.MLVSS_Mass.value) → OK
#print(DSP.Aeration.OD2.value) → OK

C = DCP.Aeration.C
DSP.Aeration.OD3.value = C * DSP.Nitrogen_Process.Nitrified_TN
#print(DSP.Aeration.OD3.value) → OK


# 3. AOR 계산 (DSP 변수들만 사용)
DSP.Aeration.AOR = SingleValue("AOR", 0, False, unit="kgO2/d", remark="실제 산소요구량")
DSP.Aeration.AOR.value = DSP.Aeration.OD1 + DSP.Aeration.OD2 + DSP.Aeration.OD3 + DSP.Aeration.OD4
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
DSP.Aeration.Cs.value = np.interp(DSP.Water_Quality.Temp_Condition.value, temperatures, oxygen_levels)
DSP.Aeration.alpha.value = math.exp(-0.082 * DSP.Design_Check.Operational_MLSS / 1000)
DSP.Aeration.Cs_correction_Factor.value = 1 + 0.5 * STC.flowtank.water_level / 10.24
#print(DSP.Aeration.Cs_correction_Factor.value)→ ▲

DSP.Aeration.SOR.value = DSP.Aeration.AOR * Csw * DSP.Aeration.Cs_correction_Factor / (DSP.Aeration.alpha * 1.024**(DSP.Water_Quality.Temp_Condition.value - 20) * (DSP.Aeration.beta * DSP.Aeration.Cs * DSP.Aeration.Cs_correction_Factor - DSP.Aeration.Ca)) * (760 / DSP.Aeration.Atmospheric_Pressure)
print(DSP.Aeration.SOR.value) 

Density_of_air = 1.2923
Ow = 0.2315
DSP.Aeration.Gs.value = DSP.Aeration.SOR / (OTE/100*Density_of_air*Ow) * (293/273) / (DSP.Nitrogen_Process.Total_Aeration_Time*60) * (1+Aeration_SF/100)

# 5. DCP에 DSP 변수들 저장
DCP.Aeration.OD1=RangedValue("OD1", DSP.Aeration.OD1.value, False, unit="kgO2/day", remark="Required O2 to Oxidate BOD")
DCP.Aeration.OD2=RangedValue("OD2", DSP.Aeration.OD2.value, False, unit="kgO2/day", remark="Required O2 for Endogenous Respiration [kgO2/day]")
DCP.Aeration.OD3=RangedValue("OD3", DSP.Aeration.OD3.value, False, unit="kgO2/day", remark="Required O2 for nitrification")
DCP.Aeration.OD4=RangedValue("OD4", DSP.Aeration.OD4.value, False, unit="kgO2/day", remark="O2 in Effluent Flow")
DCP.Aeration.AOR=RangedValue("AOR", DSP.Aeration.AOR.value, False, unit="kgO2/day")
DCP.Aeration.SOR=RangedValue("SOR", DSP.Aeration.SOR.value, False, unit="kgO2/day")
DCP.Aeration.Gs=RangedValue("Gs", DSP.Aeration.Gs.value, False, unit="㎥-air/min", remark="Blower Flow (Total Requirment)")

#print(DCP.Aeration.OD1.value)
#print(DCP.Aeration.OD2.value)

DCP.Alk_Chemical.required=RangedValue("Required Alk",148, True, unit="mg/L as CaCO3")
DCP.Alk_Chemical.influent=RangedValue("Influent Alk",250, True, unit="mg/L as CaCO3")
DCP.Alk_Chemical.additional=RangedValue("Additional Alk",0, True, unit="mg/L as CaCO3")

DCP.CH3OH_Chemical.required=RangedValue("Required Carbon",158, True, unit="mg/L")
DCP.CH3OH_Chemical.influent=RangedValue("Influent BOD",207, True, unit="mg/L")
DCP.CH3OH_Chemical.additional=RangedValue("Additional Carbon",0, True, unit="mg/L")
DCP.CH3OH_Chemical.conc=RangedValue("CH3OH Conc",99, True, unit="%")

# ===== DSP 전용 DCR 저장 =====
# DSP 변수들을 사용한 DCR 저장
DCR.MLSS= RangedValue("MLSS", DSP.Design_Check.Operational_MLSS.value, False, 2000,4000,unit="mg/L", remark="MLSS of Designed Reactor", string_format="N2")
DCR.MLVSS= RangedValue("MLVSS", DSP.Design_Check.Operational_MLVSS.value, False, 1500,3000,unit="mg/L", remark="MLVSS of Designed Reactor", string_format="N2")
DCR.MLSSpMLVSS= RangedValue("MLVSS/MLSS", DSP.Biology.VSS_TSS_Ratio.value, False, 0.6,0.8,unit="-")
DCR.SRT= RangedValue("SRT", DSP.Biology.SRT_designed.value, False, 12,24,unit="d")
DCR.SNR= RangedValue("SNR", DSP.Nitrogen_Process.Designed_SNR.value, False, 0.04, 0.07, unit="gNH3-N/gMv/d", string_format="N2")
DCR.SDNR= RangedValue("SDNR", DSP.Nitrogen_Process.Designed_SDNR.value, False, 0.05,0.15,unit="gNO3-N/gMv/d")
DCR.HRT= RangedValue("HRT", DSP.Design_Check.Designed_HRT.value, False, 12,30,unit="hr")
DCR.FM= RangedValue("F/M ratio", DSP.Design_Check.FM_ratio.value, False, 0.05,0.3,unit="kgBOD/kgMLVSS/d", string_format="N2")
DCR.Fill= RangedValue("Fill Fraction", DSP.Design_Check.Designed_Fillratio*100, False, unit="%")

DCR.MLSS.value = DSP.Design_Check.Operational_MLSS.value
DCR.MLVSS.value = DSP.Design_Check.Operational_MLVSS.value
DCR.MLSSpMLVSS.value = DSP.Biology.VSS_TSS_Ratio.value
DCR.SRT = DSP.Biology.SRT_designed.value
DCR.SNR = DSP.Nitrogen_Process.Designed_SNR.value
DCR.SDNR = DSP.Nitrogen_Process.Designed_SDNR.value
DCR.HRT = DSP.Design_Check.Designed_HRT.value
DCR.FM = DSP.Design_Check.FM_ratio.value
DCR.Fill = DSP.Design_Check.Designed_Fillratio*100

'''기계 작성 예시'''
# 1. 생물반응조 송풍기
DEP.Air_Blower.SOR_O2_per_day = SingleValue("SOR", DSP.Aeration.SOR.value, False, unit="kgO2/d", remark = "지당 표준 산소요구량(SOR)", string_format="N2")
DEP.Air_Blower.T_C = SingleValue("Temperature", DSP.Water_Quality.Temp_Condition.value, False, unit="℃", remark = "설계 수온")
DEP.Air_Blower.EA_percent = SingleValue("EA Percent", 18.00, True, unit="%", remark = "산소전달율")
DEP.Air_Blower.Aeration_Depth = SingleValue("Aeration Depth", STC.flowtank.water_level.value, False, unit="m", remark = "폭기 수심")
DEP.Air_Blower.Operation_Time = SingleValue("Operation Time", 10, True, unit="hr", remark = "가동시간")
DEP.Air_Blower.total_dynamic_head = SingleValue("Total dynamic head", 10, False, unit="mmAq", remark = "전양정")
DEP.Air_Blower.Safety_Factor = SingleValue("Safety Factor", 0, True, unit="%", remark = "여유율")
DEP.Air_Blower.Pipe_length = SingleValue("Pipe length", 100.00, False, unit="m", remark = "총배관 상당길이")
DEP.Air_Blower.Safety_Factor_motor = SingleValue("Motor Efficiency", 10, True, unit="%", remark = "전동기 여유율")

DEP.Air_Blower.SOR_O2_per_day.value = DSP.Aeration.SOR.value
DEP.Air_Blower.T_C.value = DSP.Water_Quality.Temp_Condition.value
DEP.Air_Blower.Aeration_Depth.value = STC.flowtank.water_level.value


EQP.Air_Blower = EquipmentValue(
    name="생물반응조 송풍기",              # 장비 이름
    code_key_list=["M_AEB0101"],      # 장비 코드 그룹
    code_key="M_AEB0101",                     # 장비 코드
    normal_count = 2, 
    spare_count = 1,
    total_required_capacity=1,
    inputs=DEP.Air_Blower,                        # 계산식 입력값들
    structure=STC.flowtank                        # 구조물 정보
)

EQP.Air_Blower.normal_count = STC.flowtank.tank_number
EQP.Air_Blower.spec2 = EQP.Air_Blower.applied_capacity
DSP.Air_Blower.result_A = SingleValue("max_capacity_m3_min", 156.0, False, unit="m3/min", remark = ".", string_format="F2")
DSP.Air_Blower.result_A.value = EQP.Air_Blower.outputs.get("max_capacity_m3_min",SingleValue("max_capacity_m3_min", 156.0, False, unit="m3/min", remark = ".", string_format="F2"))
DSP.Air_Blower.result_B = SingleValue("discharge_pressure_mmAq", 156.0, False, unit="mmaq", remark = ".", string_format="F2")
DSP.Air_Blower.result_B.value = EQP.Air_Blower.outputs.get("discharge_pressure_mmAq",SingleValue("discharge_pressure_mmAq", 156.0, False, unit="mmaq", remark = ".", string_format="F2"))
EQP.Air_Blower.unit_required_capacity = f"{DSP.Air_Blower.result_A.value}m3/min {DSP.Air_Blower.result_B.value} mmAq"


# 배관 관경 및 유속 산정
DSP.Air_Blower.Pump_flowrate = SingleValue("pump_flowrate", 1, False, "m3/min")
pump_flowrate = EQP.Air_Blower.outputs.get("max_capacity_m3_min",SingleValue("max_capacity_m3_min", 1, False, unit="m3/h", remark = "토출유량"))
DSP.Air_Blower.Pump_flowrate.value = pump_flowrate

DCP.Air_Blower.fluid_velocity = RangedValue("송풍관 유속", 20, True, 15, 30,unit="m/s", remark= "Remark")
dia_breaks = np.array([15, 20, 25, 32, 40, 50, 65, 100, 125, 150, 200, 250, 300, 350])   # 관경 범위(mm)
dia_sizes = np.array([15, 20, 25, 32, 40, 50, 65, 100, 125, 150, 200, 250, 300, 350])    # 적용 관경(mm)

DSP.Air_Blower.FDCT_dia = SingleValue("", 1, False, unit="", remark = "")
DSP.Air_Blower.FDCT_dia.value = (146 * ( (DSP.Air_Blower.Pump_flowrate.value) / DCP.Air_Blower.fluid_velocity.value)**0.5)
print(DSP.Air_Blower.result_A.value)

Determined_dia = next((size for brk, size in zip(dia_breaks, dia_sizes) if DSP.Air_Blower.FDCT_dia.value <= brk), dia_sizes[-1])

EQP.Air_Blower.size.value = Determined_dia

DSP.Air_Blower.fluid_velocity = SingleValue("", 1, False, unit="m/s", remark = "")
DSP.Air_Blower.fluid_velocity.value = (146**2) * DSP.Air_Blower.result_A.value /(EQP.Air_Blower.size.value**2) #m/s (배관 관경 적용으로 인해 변경된 값)

DCR.Blower_pipe = SingleValue("Blower Pipe", EQP.Air_Blower.size.value, False, unit="A", remark = ".")
DCR.Blower_pipe.value = EQP.Air_Blower.size.value
print("EQP.Air_Blower.size", EQP.Air_Blower.size.value)


#EQP.Air_Blower.pipe_length = 13.6
###여기서 부터는 양정계산 내용!
# Δhf = f*(V²/ 2g), f=(0.04+1/(1000×D))*L/D
DSP.Air_Blower.darcy_friction_factor_pipe = SingleValue(".", 0.02, True, unit=".", remark = ".") #unitless (K 값)
DSP.Air_Blower.length = SingleValue(".", EQP.Air_Blower.pipe_length*1, False, unit=".", remark = ".") #m () ==>>> 3D에서 받아와야할 값#################################################################
DSP.Air_Blower.length.value = EQP.Air_Blower.pipe_length.value
DSP.Air_Blower.Headloss_of_pipe = SingleValue("직관 손실", 1, False, unit="-", remark = "-")
DSP.Air_Blower.Headloss_of_pipe.value = ((DSP.Air_Blower.darcy_friction_factor_pipe.value*(DSP.Air_Blower.length.value/(EQP.Air_Blower.size.value/1000)))*(DSP.Air_Blower.fluid_velocity**2/(2*9.8)))

# 사일런서 손실
DSP.Air_Blower.Headloss_of_silencer = SingleValue("사일런서 손실", 300, False, unit="-", remark = "-")

# 포기기손실
DSP.Air_Blower.Headloss_of_aerator = SingleValue("포기기 손실", 300, False, unit="-", remark = "-")

##위는 Darcy 공식,,, 압송일때는 Hazen Willams 식을 써야할지도...?
##그리고 자연유하는 Manning 식을 이용
#앨보 국부손실 양정 손실 계산서
DSP.Air_Blower.darcy_friction_factor_elbow = SingleValue(".", 0.75, True, unit=".", remark = ".") #unitless (K 값)
DSP.Air_Blower.Number_of_elbow = SingleValue(".", EQP.Air_Blower.elbow_count*1, False, unit=".", remark = ".") #unitless (K 값) ==>>> 3D에서 받아와야할 값#################################################################
DSP.Air_Blower.Number_of_elbow.value = EQP.Air_Blower.elbow_count.value
DSP.Air_Blower.Headloss_of_fitting = SingleValue(".", 300, True, unit=".", remark = ".")

#전체 양정손실
DSP.Air_Blower.Totalheadloss = SingleValue(".", 15, True, unit=".", remark = ".")
DSP.Air_Blower.Totalheadloss.value = round(DSP.Air_Blower.Headloss_of_pipe.value + 
                                        DSP.Air_Blower.Headloss_of_fitting.value + 
                                        DSP.Air_Blower.Headloss_of_silencer.value+
                                        DSP.Air_Blower.Headloss_of_aerator.value+
                                        DEP.Air_Blower.Aeration_Depth.value*1000,3)
DEP.Air_Blower.total_dynamic_head.value = DSP.Air_Blower.Totalheadloss.value


# 2. 생물반응조 수중포기기
DEP.Aeration_Device.SOR_O2_per_day = SingleValue("SOR", DSP.Aeration.SOR.value, False, unit="kgO2/d", remark = "지당 표준 산소요구량(SOR)")
DEP.Aeration_Device.Aeration_Depth = SingleValue("Aeration Depth", STC.flowtank.water_level.value, False, unit="m", remark = "폭기 수심")
DEP.Aeration_Device.Operation_time = SingleValue("Operation Time", DSP.Operation.Number_of_Cycle_Per_day * DCP.Operation_Cycle.Aeration / 60, False, unit="hr", remark = "가동시간")
DEP.Aeration_Device.Number_of_Tank = SingleValue("Tank number", STC.flowtank.tank_number, False, unit="EA", remark = "조 수량")
DEP.Aeration_Device.W = SingleValue("width", STC.flowtank.W.value, False, remark = "조 너비")
DEP.Aeration_Device.L = SingleValue("length", STC.flowtank.L.value, False, remark = "조 길이")
DEP.Aeration_Device.He = SingleValue("water level", STC.flowtank.height.value, False, remark = "조 높이")

DEP.Aeration_Device.SOR_O2_per_day = DSP.Aeration.SOR.value
DEP.Aeration_Device.Aeration_Depth =STC.flowtank.water_level.value
DEP.Aeration_Device.Operation_time.value =DSP.Operation.Number_of_Cycle_Per_day * DCP.Operation_Cycle.Aeration / 60
STC.flowtank.W.value = STC.flowtank.W.value
STC.flowtank.L.value = STC.flowtank.L.value
DEP.Aeration_Device.He.value = STC.flowtank.height.value

# EquipmentValue 생성 (StructureValue에서 계산된 상세값 활용)
EQP.Aeration_Device = EquipmentValue(
    name="생물반응조 수중포기기",           # 장비 이름
    code_key_list=["M_AQR05"],              # 장비 코드 그룹
    code_key="M_AQR05",                         # 장비 코드
    normal_count = 2, 
    spare_count = 0,
    total_required_capacity=1,
    inputs=DEP.Aeration_Device,                   # 계산식 입력값들
    structure=STC.flowtank                       # 구조물 정보
)
EQP.Aeration_Device.normal_count = STC.flowtank.tank_number
EQP.Aeration_Device.spec2 = EQP.Aeration_Device.applied_capacity
DSP.Aeration_Device.result_A = SingleValue("o2_transfer_rate_kgO2_h", 156.0, False, unit="kgO2/hr", remark = ".", string_format="F2")
DSP.Aeration_Device.result_A.value = EQP.Aeration_Device.outputs.get("o2_transfer_rate_kgO2_h",SingleValue("o2_transfer_rate_kgO2_h", 156.0, False, unit="kgO2/hr", remark = ".", string_format="F2"))
EQP.Aeration_Device.unit_required_capacity = f"{DSP.Aeration_Device.result_A.value}kgO2/hr"
EQP.Aeration_Device.size = 100


# 3. 상등수 배출장치
DEP.Floating_Decanter.Inflow_Flowrate = SingleValue("Decanter Flowrate", DCN.effluents.water.q.value, False, unit="㎥/d", remark = "일 배출량")
DEP.Floating_Decanter.Discharge_Time = SingleValue("Discharge Time", DCP.Operation_Cycle.Discharge.value / 60, False, unit="hr/Cycle", remark = "배출 시간")
DEP.Floating_Decanter.Number_of_Drives = SingleValue("Drives number", DSP.Operation.Number_of_Cycle_Per_day.value, False, unit="Cycle/d", remark = "일 운전 횟수")
DEP.Floating_Decanter.Safety_Factor = SingleValue("Safety Factor", 0, True, unit="%", remark = "여유율")

DEP.Floating_Decanter.Inflow_Flowrate.value = DCN.effluents.water.q.value
DEP.Floating_Decanter.Discharge_Time.value = DCP.Operation_Cycle.Discharge.value / 60
DEP.Floating_Decanter.Number_of_Drives.value = DSP.Operation.Number_of_Cycle_Per_day.value

EQP.Floating_Decanter = EquipmentValue(
    name="상등수 배출장치",
    code_key_list=["M_FDC01"],
    code_key="M_FDC01",
    normal_count = 2, 
    spare_count = 0,
    total_required_capacity=1,
    inputs= DEP.Floating_Decanter,
    structure=STC.flowtank
)

EQP.Floating_Decanter.normal_count = STC.flowtank.tank_number
EQP.Floating_Decanter.spec2 = EQP.Floating_Decanter.applied_capacity
DSP.Floating_Decanter.result_A = SingleValue("max_capacity_m3_h", 2, False, unit="m3/대", remark = "")
DSP.Floating_Decanter.result_A.value = EQP.Floating_Decanter.outputs.get("max_capacity_m3_h",SingleValue("max_capacity_m3_h", 156.0, False, unit="m3/min", remark = ".", string_format="F2"))
EQP.Floating_Decanter.unit_required_capacity = f"{DSP.Floating_Decanter.result_A.value}m3/hr"

# 4. ★추가★ 밸브
DEP.Valve.Determined_diameter = SingleValue("diameter", 250, False, unit="A", remark = "직경")
DEP.Valve.Determined_diameter.value = EQP.Floating_Decanter.outputs.get("decanter_diameter",SingleValue("decanter_diameter", 250, False, unit="A", remark = "직경"))

# 배관 관경 및 유속 산정
DSP.Floating_Decanter.Pump_flowrate = SingleValue("pump_flowrate", 1, False, "m3/min")
pump_flowrate = EQP.Floating_Decanter.outputs.get("max_capacity_m3_h",SingleValue("max_capacity_m3_h", 4.0, False, unit="m3/h", remark = "토출유량"))
DSP.Floating_Decanter.Pump_flowrate.value = pump_flowrate / 60

print(pump_flowrate)

DCP.Floating_Decanter.fluid_velocity = RangedValue("슬러지저류조 유출펌프 배관 유속", 2.0, True, 1.0, 3.5,unit="m/s", remark= "Remark" )
dia_breaks = np.array([15, 20, 25, 32, 40, 50, 65, 100, 125, 150, 200, 250, 300, 350])   # 관경 범위(mm)
dia_sizes = np.array([15, 20, 25, 32, 40, 50, 65, 100, 125, 150, 200, 250, 300, 350])    # 적용 관경(mm)

DSP.Floating_Decanter.FDCT_dia = SingleValue("", 1, False, unit="", remark = "")
DSP.Floating_Decanter.FDCT_dia.value = (146 * ( (DSP.Floating_Decanter.Pump_flowrate) / DCP.Floating_Decanter.fluid_velocity.value)**0.5)

Determined_dia1 = next((size for brk, size in zip(dia_breaks, dia_sizes) if DSP.Floating_Decanter.FDCT_dia <= brk), dia_sizes[-1])

EQP.Floating_Decanter.size = SingleValue("", 1, False, unit="", remark = "")
EQP.Floating_Decanter.size.value = Determined_dia1

DSP.Floating_Decanter.fluid_velocity = SingleValue("", 1, False, unit="", remark = "")
DSP.Floating_Decanter.fluid_velocity.value = (146**2) * DSP.Floating_Decanter.Pump_flowrate /(EQP.Floating_Decanter.size**2)  #m/s (배관 관경 적용으로 인해 변경된 값)

DCR.decanter_pipe = SingleValue("Decanter Pipe", EQP.Floating_Decanter.size.value, False, unit="A", remark = ".")
DCR.decanter_pipe.value = EQP.Floating_Decanter.size.value
print("디캔터 파이프 직경", DCR.decanter_pipe.value)


###여기서 부터는 수리계산 내용!
# Δhf = f*(V²/ 2g), f=(0.04+1/(1000×D))*L/D
DSP.Floating_Decanter.darcy_friction_factor_pipe = SingleValue(".", 0.018, True, unit=".", remark = ".") #unitless (K 값)
DSP.Floating_Decanter.length = SingleValue(".", EQP.Floating_Decanter.pipe_length*1, False, unit=".", remark = ".") #m () ==>>> 3D에서 받아와야할 값#################################################################
DSP.Floating_Decanter.length.value = EQP.Floating_Decanter.pipe_length.value
DSP.Floating_Decanter.Headloss_of_pipe = SingleValue("직관 손실", 1, False, unit="-", remark = "-")
DSP.Floating_Decanter.Headloss_of_pipe.value = (0.04+1/(EQP.Floating_Decanter.size.value))*DSP.Floating_Decanter.length.value/(EQP.Floating_Decanter.size.value/1000)*(DSP.Floating_Decanter.fluid_velocity.value**2/(2*9.8))

#유출손실수두
DSP.Floating_Decanter.Headloss_of_effluent = SingleValue("유출 손실", 1, False, unit="-", remark = "-")
DSP.Floating_Decanter.Headloss_of_effluent.value =1*(DSP.Floating_Decanter.fluid_velocity.value**2/(2*9.8))

#유입손실수두
DSP.Floating_Decanter.Headloss_of_influent = SingleValue("유출 손실", 1, False, unit="-", remark = "-")
DSP.Floating_Decanter.Headloss_of_influent.value =0.5*(DSP.Floating_Decanter.fluid_velocity.value**2/(2*9.8))

##위는 Darcy 공식,,, 압송일때는 Hazen Willams 식을 써야할지도...?
##그리고 자연유하는 Manning 식을 이용
#앨보 국부손실 양정 손실 계산서
DSP.Floating_Decanter.darcy_friction_factor_elbow = SingleValue(".", 0.75, True, unit=".", remark = ".") #unitless (K 값)
DSP.Floating_Decanter.Number_of_elbow = SingleValue(".", EQP.Floating_Decanter.elbow_count*1, False, unit=".", remark = ".") #unitless (K 값) ==>>> 3D에서 받아와야할 값#################################################################
DSP.Floating_Decanter.Number_of_elbow.value = EQP.Floating_Decanter.elbow_count.value 
DSP.Floating_Decanter.Headloss_of_elbow = SingleValue(".", 2, True, unit=".", remark = ".")
DSP.Floating_Decanter.Headloss_of_elbow.value = DSP.Floating_Decanter.darcy_friction_factor_elbow.value * DSP.Floating_Decanter.Number_of_elbow.value / (DSP.Floating_Decanter.fluid_velocity.value)**2 / (2*9.81)
#전체 양정손실
DSP.Floating_Decanter.Totalheadloss = SingleValue(".", 15, True, unit=".", remark = ".")
DSP.Floating_Decanter.Totalheadloss.value = round(DSP.Floating_Decanter.Headloss_of_pipe.value + 
                                        DSP.Floating_Decanter.Headloss_of_elbow.value + 
                                        DSP.Floating_Decanter.Headloss_of_effluent.value+
                                        DSP.Floating_Decanter.Headloss_of_influent.value,3)

DSP.flowtank.headloss_pipe = DSP.Floating_Decanter.Totalheadloss
DSP.flowtank.headloss_pipe.value = DSP.Floating_Decanter.Totalheadloss.value

#print("Decanter velocity", DSP.Floating_Decanter.fluid_velocity.value)
#print("Decanter size", EQP.Floating_Decanter.size)
#print("Decanter pipe lenght", DSP.Floating_Decanter.length.value)
#print("Head loss Pipe lenght", DSP.Floating_Decanter.Headloss_of_pipe)
#print("Head loss total", DSP.Floating_Decanter.Totalheadloss)


# 4. 밸브
EQP.Valve = EquipmentValue(
    name="밸브",
    code_key_list=["M_VAV0201"],
    code_key="M_VAV0201",
    normal_count = 2, 
    spare_count = 0,
    total_required_capacity=1,
    inputs= DEP.Valve,
    structure=STC.flowtank)

EQP.Valve.normal_count = STC.flowtank.tank_number
EQP.Valve.spec2 = EQP.Valve.applied_capacity
DSP.Valve.result_A = SingleValue("diameter_mm", 200.0, False, unit="mm", remark = ".")
DSP.Valve.result_A.value = EQP.Valve.outputs.get("diameter_mm",SingleValue("diameter_mm", 200.0, False, unit="mm", remark = "."))
EQP.Valve.unit_required_capacity = f"{DSP.Valve.result_A.value}mm"
EQP.Valve.size.value = DSP.Valve.result_A.value

print("밸브 관경", EQP.Valve.size.value)

# 5. ★추가★ 공법제어반
DEP.Control_Panel.Inflow_Flowrate = SingleValue("Flowrate", DCN.influents.q.value, False, unit="ton/d", remark = "유입량")
DEP.Control_Panel.Inflow_Flowrate.value = DCN.influents.q.value
EQP.Control_Panel = EquipmentValue(
    name="공법제어반",
    code_key_list=["M_CTR0102"],
    code_key="M_CTR0102",
    normal_count = 1, 
    spare_count = 0,
    total_required_capacity=1,
    inputs= DEP.Control_Panel,
    structure=STC.flowtank)

EQP.Control_Panel.spec2 = EQP.Control_Panel.applied_capacity
EQP.Control_Panel.unit_required_capacity = f"자동제어반"


# 6. 잉여슬러지 배출펌프
DEP.Sludge_Discharge_Pump.Inflow_Flowrate= SingleValue("Inflow Flowrate", DSP.Sludge.Sludge_production_q.value, False, unit="㎥/d", remark = "유입량")
DEP.Sludge_Discharge_Pump.Solid_Concenctration = SingleValue("Solid Concenctration", DSP.Sludge.Pump_inflow_solid_conc.value, False, unit="%", remark = "고형물 농도")
DEP.Sludge_Discharge_Pump.Operation_Time = SingleValue("Operation Time", 0.3, True, unit="hr", remark = "가동시간")
DEP.Sludge_Discharge_Pump.Specific_Gravity_Influent = SingleValue("Specific Gravity(Influent)", 1.0, True, unit="ton/㎥", remark = "비중")
DEP.Sludge_Discharge_Pump.Safety_Factor = SingleValue("Safety Factor", 0, True, unit="%", remark = "여유율")
DEP.Sludge_Discharge_Pump.Total_Dynamic_Head = SingleValue("Total Dynamic Head", 10.00, False, unit="m", remark = "실양정")
DEP.Sludge_Discharge_Pump.Pipe_length = SingleValue("Pipe length", 50.00, False, unit="m", remark = "총배관 상당길이")
DEP.Sludge_Discharge_Pump.Pump_Efficiency = SingleValue("Pump Efficiency", 37.6, True, unit="%", remark = "펌프 효율")

DEP.Sludge_Discharge_Pump.Inflow_Flowrate = DSP.Sludge.Sludge_production_q.value
DEP.Sludge_Discharge_Pump.Solid_Concenctration = DSP.Sludge.Pump_inflow_solid_conc.value

EQP.Sludge_Discharge_Pump = EquipmentValue(
    name="잉여슬러지 배출펌프",
    code_key_list=["M_PMP0601"],      # DropboxValue(), False,
    code_key="M_PMP0601",                        # 실제 기계 코드명
    normal_count = 2, 
    spare_count = 1,
    total_required_capacity=1,
    inputs= DEP.Sludge_Discharge_Pump,
    structure=STC.flowtank )

EQP.Sludge_Discharge_Pump.spec2 = EQP.Sludge_Discharge_Pump.applied_capacity
DSP.Sludge_Discharge_Pump.result_A = SingleValue("max_capacity_m3_min", 156.0, False, unit="m3/min", remark = ".", string_format="F2")
DSP.Sludge_Discharge_Pump.result_A.value = EQP.Sludge_Discharge_Pump.outputs.get("max_capacity_m3_min",SingleValue("max_capacity_m3_min", 156.0, False, unit="m3/min", remark = ".", string_format="F2"))
DSP.Sludge_Discharge_Pump.result_B = SingleValue("total_dynamic_head", 156.0, False, unit="mH", remark = ".", string_format="F2")
DSP.Sludge_Discharge_Pump.result_B.value = EQP.Sludge_Discharge_Pump.outputs.get("total_dynamic_head",SingleValue("total_dynamic_head", 156.0, False, unit="mH", remark = ".", string_format="F2"))
EQP.Sludge_Discharge_Pump.unit_required_capacity = f"{DSP.Sludge_Discharge_Pump.result_A.value}m3/min {DSP.Sludge_Discharge_Pump.result_B.value} mH"

# 배관 관경 및 유속 산정
DSP.Sludge_Discharge_Pump.Pump_flowrate = SingleValue("pump_flowrate", 1, False, "m3/min")
pump_flowrate = EQP.Sludge_Discharge_Pump.outputs.get("max_capacity_m3_min",SingleValue("max_capacity_m3_min", 4.0, False, unit="m3/h", remark = "토출유량"))
DSP.Sludge_Discharge_Pump.Pump_flowrate.value = pump_flowrate.value 

DCP.Sludge_Discharge_Pump.fluid_velocity = RangedValue("슬러지저류조 유출펌프 배관 유속", 2.0, True, 1.0, 3.5,unit="m/s", remark= "Remark" )
dia_breaks = np.array([15, 20, 25, 32, 40, 50, 65, 100, 125, 150, 200, 250, 300, 350])   # 관경 범위(mm)
dia_sizes = np.array([15, 20, 25, 32, 40, 50, 65, 100, 125, 150, 200, 250, 300, 350])    # 적용 관경(mm)

DSP.Sludge_Discharge_Pump.FDCT_dia = SingleValue("", 1, False, unit="", remark = "")
DSP.Sludge_Discharge_Pump.FDCT_dia.value = (146 * ( (DSP.Sludge_Discharge_Pump.Pump_flowrate.value) / DCP.Sludge_Discharge_Pump.fluid_velocity)**0.5)

Determined_dia2 = next((size for brk, size in zip(dia_breaks, dia_sizes) if DSP.Sludge_Discharge_Pump.FDCT_dia <= brk), dia_sizes[-1])

EQP.Sludge_Discharge_Pump.size.value = Determined_dia2

DSP.Sludge_Discharge_Pump.fluid_velocity = SingleValue("", 1, False, unit="", remark = "")
DSP.Sludge_Discharge_Pump.fluid_velocity.value = (146**2) * DSP.Sludge_Discharge_Pump.Pump_flowrate /(EQP.Sludge_Discharge_Pump.size**2) #m/s (배관 관경 적용으로 인해 변경된 값)

DCR.Pump_pipe = SingleValue("Sludge Pump Pipe", EQP.Sludge_Discharge_Pump.size.value, False, unit="A", remark = ".")
DCR.Pump_pipe = EQP.Sludge_Discharge_Pump.size.value
print("슬러지 펌프 관경", DCR.Pump_pipe.value)


#EQP.Sludge_Discharge_Pump.pipe_length = 13.6
###여기서 부터는 양정계산 내용!
# Δhf = f*(V²/ 2g), f=(0.04+1/(1000×D))*L/D
DSP.Sludge_Discharge_Pump.darcy_friction_factor_pipe = SingleValue(".", 0.031, True, unit=".", remark = ".") #unitless (K 값)
DSP.Sludge_Discharge_Pump.darcy_friction_factor_pipe.value = (0.03+1)/(EQP.Sludge_Discharge_Pump.size.value * 1000)
DSP.Sludge_Discharge_Pump.length = SingleValue(".", EQP.Sludge_Discharge_Pump.pipe_length*1, False, unit=".", remark = ".") #m () ==>>> 3D에서 받아와야할 값#################################################################
DSP.Sludge_Discharge_Pump.length.value = EQP.Sludge_Discharge_Pump.pipe_length.value
DSP.Sludge_Discharge_Pump.Headloss_of_pipe = SingleValue("직관 손실", 1, False, unit="-", remark = "-")
DSP.Sludge_Discharge_Pump.Headloss_of_pipe.value = ((DSP.Sludge_Discharge_Pump.darcy_friction_factor_pipe.value*(DSP.Sludge_Discharge_Pump.length.value/(EQP.Sludge_Discharge_Pump.size/1000)))*(DSP.Sludge_Discharge_Pump.fluid_velocity.value**2/(2*9.8)))

#실양정 (Delta Ha)(단위가 뭘로 3D에서 넘어오는지 확인필요함)
DSP.Sludge_Discharge_Pump.Delta_Ha = SingleValue("배관실양정손실", EQP.Sludge_Discharge_Pump.pipe_max_height - EQP.Sludge_Discharge_Pump.pipe_min_height, False, unit="-", remark = "-")
DSP.Sludge_Discharge_Pump.Delta_Ha.value = EQP.Sludge_Discharge_Pump.pipe_max_height.value - EQP.Sludge_Discharge_Pump.pipe_min_height.value

#피팅손실
DSP.Sludge_Discharge_Pump.Headloss_of_fitting = SingleValue(".", 1, True, unit=".", remark = ".")
#전체 양정손실
DSP.Sludge_Discharge_Pump.Totalheadloss = SingleValue(".", 15, True, unit=".", remark = ".")
DSP.Sludge_Discharge_Pump.Totalheadloss.value = round(DSP.Sludge_Discharge_Pump.Headloss_of_pipe.value + 
                                        DSP.Sludge_Discharge_Pump.Headloss_of_fitting.value + 
                                        DSP.Sludge_Discharge_Pump.Delta_Ha.value,3)

DEP.Sludge_Discharge_Pump.Total_Dynamic_Head.value = DSP.Sludge_Discharge_Pump.Totalheadloss.value


#print("펌프손실", DEP.Sludge_Discharge_Pump.Total_Dynamic_Head)

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

TankTypeTable = StandardTable(tank_type_decision_table)

if STC.flowtank.code_key == StructureType.CONCRETE_SQUARE.value:
    STC.flowtank.layout_type = TankTypeTable.get_value(int(STC.flowtank.tank_number))[0]
    STC.flowtank.layout_type_number = STC.flowtank.tank_number
else:
    STC.flowtank.layout_type = StructureLayoutType.None_TYPE


# P&ID 매핑
MAP.con1_name = f"SBR reactor"
MAP.con1_qty = f"{STC.flowtank.tank_number}"

MAP.aqr1_name = f"{EQP.Aeration_Device.name}"
MAP.aqr1_spec1 =f"{EQP.Aeration_Device.spec1.value}"
MAP.aqr1_spec2 = f"{EQP.Aeration_Device.applied_capacity}"
MAP.aqr1_qty = f"{EQP.Aeration_Device.qty.value}"

MAP.fdc1_name = f"{EQP.Floating_Decanter.name}"
MAP.fdc1_spec1 = f"{EQP.Floating_Decanter.spec1.value}"
MAP.fdc1_spec2 =f"{EQP.Floating_Decanter.applied_capacity}"
MAP.fdc1_qty = f"{EQP.Floating_Decanter.qty.value}"

MAP.vav1_name = f"{EQP.Valve.name}"
MAP.vav1_spec1 =f"{EQP.Valve.spec1.value}"
MAP.vav1_spec2 =f"{EQP.Valve.applied_capacity}"
MAP.vav1_qty =  f"{EQP.Valve.qty.value}"

MAP.pmp1_name = f"{EQP.Sludge_Discharge_Pump.name}"
MAP.pmp1_spec1 =f"{EQP.Sludge_Discharge_Pump.spec1.value}"
MAP.pmp1_spec2 =f"{EQP.Sludge_Discharge_Pump.applied_capacity}"
MAP.pmp1_qty = f"{EQP.Sludge_Discharge_Pump.qty.value}"

MAP.aeb1_name = f"{EQP.Air_Blower.name}"
MAP.aeb1_spec1 =f"{EQP.Air_Blower.spec1.value}"
MAP.aeb1_spec2 =f"{EQP.Air_Blower.applied_capacity}"
MAP.aeb1_qty = f"{EQP.Air_Blower.qty.value}"

MAP.ctr1_name = f"{EQP.Control_Panel.name}"
MAP.ctr1_spec1 =f"{EQP.Control_Panel.spec1.value}"
MAP.ctr1_spec2 = f"자동제어반"
MAP.ctr1_qty = f"{EQP.Control_Panel.qty.value}"

MAP.s_ep_size = f"{EQP.Sludge_Discharge_Pump.size.value}A"
MAP.s_ep_bm = f"STS"
MAP.a_ehp_size = f"{EQP.Air_Blower.size.value}A"
MAP.a_ehp_bm = f"SPP"
MAP.a_ep_size = f"150A"
MAP.a_ep_bm = f"SPP"
MAP.t_ep_size = f"{EQP.Floating_Decanter.size.value}A"
MAP.t_ep_bm = f"STS"
MAP.u_ep_size = f"32A"
MAP.u_ep_bm = f"STS"

DSP.flowtank.level_result =  SingleValue(".", 3.65, True, unit=".", remark = ".") #STC.flowtank.level_result["head_loss"]
DSP.flowtank.hydraulic_waterlevel_result = SingleValue("hydraulic_waterlevel_result", DSP.flowtank.level_result.value ,False,unit="m",remark="수리계산 수위 결과",string_format="F2")
HWL.Waterlevel1 = SingleValue("1.반응조 배출 후 수위(EL.m)", DSP.flowtank.hydraulic_waterlevel_result.value + (STC.flowtank.water_level.value - 2) + STC.flowtank.elevation_level.value, False)
HWL.Waterlevel2 = SingleValue("1.1 직관에 의한 수두손실(m)", DSP.Floating_Decanter.Headloss_of_pipe.value, False)
HWL.Waterlevel3 = SingleValue("1.2 곡관 손실(m)", DSP.Floating_Decanter.Headloss_of_elbow, False)
HWL.Waterlevel4 = SingleValue("1.3 유입 손실(m)", DSP.Floating_Decanter.Headloss_of_influent.value, False)
HWL.Waterlevel5 = SingleValue("1.4 유출 손실(m)", DSP.Floating_Decanter.Headloss_of_effluent.value, False)

DSP.flowtank.hydraulic_waterlevel_result.value = DSP.flowtank.level_result.value
HWL.Waterlevel1.value = DSP.flowtank.hydraulic_waterlevel_result.value + (STC.flowtank.water_level.value - 2) + STC.flowtank.elevation_level.value
HWL.Waterlevel2.value = DSP.Floating_Decanter.Headloss_of_pipe.value
HWL.Waterlevel3.value = DSP.Floating_Decanter.Headloss_of_elbow.value
HWL.Waterlevel4.value =  DSP.Floating_Decanter.Headloss_of_influent.value
HWL.Waterlevel5.value =  DSP.Floating_Decanter.Headloss_of_effluent.value

DCN.effluents.water.info = InfoValue("ABC")
DCN.effluents.water.info.bm = "STS"
DCN.effluents.water.info.size = f"{int(EQP.Floating_Decanter.size.value)}A"
DCN.effluents.water.info.comp = EQP.Floating_Decanter.name
DCN.effluents.water.info.raw = RawType.WATER

DCN.effluents.sludge.info = InfoValue("AB")
DCN.effluents.sludge.info.bm = "STS"
DCN.effluents.sludge.info.size = f"{int(EQP.Sludge_Discharge_Pump.size.value)}A"
DCN.effluents.sludge.info.comp = EQP.Sludge_Discharge_Pump.name
DCN.effluents.sludge.info.raw = RawType.SLUDGE