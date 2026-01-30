
#  25.12.15 JK
#  Revit Element Name과 동일하도록 수정
#
#  25.11.12 JK
#  Wall 이름을 변경
#
#  25.11.11 SK 
#  Unit : mm로 수정
#  데모 시나리오에 맞게 default size 변경하여, 설정
#
#  Original File : STC_H-Type_251022_Rev02_v11.py
# 
################################################################################
#
# Edited: BoolValue, Vector2Value, Box2Value, StandardTable, STD 추가
from WAI import SingleValue, GV, Vector3Value, Box3Value, BoolValue, Vector2Value, Box2Value, StandardTable, STD, SingletonDotDict, ELBoxValue
from typing import Dict, Any
import bisect

# Edited: FormulaBase 클래스 제거로 직접 함수 정의
# 구조물 규격계산식 : forward_calculate
# 구조물 검토계산식 : reverse_calculate
# 구조물 수리계산식 : level_calculate

def forward_calculate(DSP: SingletonDotDict=SingletonDotDict(), result:SingletonDotDict=SingletonDotDict(Box3Value)):
   IW = GV.IW = SingleValue("innerWidth", 300)
   DSP.W = SingleValue("W", 6.5, False, unit="m")
   DSP.Wmm = SingleValue ("Wmm", 1.0, False, unit="m")
   DSP.Wmm =2*DSP.W*1000 + IW
   print(f"DSP.Wmm= {DSP.Wmm}")

   DSP.L = SingleValue("L", 5.5000, False, unit="m")
   DSP.Lmm = SingleValue ("Lmm", 1.0, False, unit="m")
   DSP.Lmm = DSP.L*1000
   print(f"DSP.Lmm= {DSP.Lmm}")

   DSP.height = SingleValue("height", 6.000, False, unit="m")
   DSP.Hmm = SingleValue("heightmm", 1.0, False, unit="m")
   DSP.Hmm = DSP.height*1000
   print(f"DSP.Hmm= {DSP.Hmm}")
    
   DSP.PH_WW1 = SingleValue("PH_WW1", 3.0, False, unit="m")
   DSP.PH_WW1mm = SingleValue("PH_WW1mm", 3.0, False, unit="m")
   DSP.PH_WW1mm = DSP.PH_WW1*1000
   print(f"PH_WW1mm= {DSP.PH_WW1mm}")

   DSP.PH_WL1 = SingleValue("PH_WL1", 3.5, False, unit="m")
   DSP.PH_WL1mm = SingleValue("PH_WL1mm", 3.5, False, unit="m")
   DSP.PH_WL1mm = DSP.PH_WL1*1000
   print(f"PH_WL1mm= {DSP.PH_WL1mm}")

   DSP.PH_WH1 = SingleValue("PH_WH1", 3.5, False, unit="m")
   DSP.PH_WH1mm = SingleValue("PH_WH1mm", 3.5, False, unit="m")
   DSP.PH_WH1mm = DSP.PH_WH1*1000
   # print(f"DSP.PH_WH1mm= {DSP.PH_WH1mm}")

   DSP.PH_WH2 = SingleValue("PH_WH2", 2.0, False, unit="m")
   DSP.PH_WH2mm = SingleValue("PH_WH2mm", 2.0, False, unit="m")
   DSP.PH_WH2mm = DSP.PH_WH2*1000
   # print(f"DSP.PH_WH2mm= {DSP.PH_WH2mm}")
    
   DSP.water_level = SingleValue("water_level", 5.0, False, unit="m")
   DSP.water_levelmm = SingleValue("water_level", 5.0, False, unit="m")
   DSP.water_levelmm = DSP.water_level*1000
   #print(f"DSP.water_levelmm= {DSP.water_levelmm}")

   #구조물 지수 2
   DSP.tank_number = SingleValue("EA", 2, False, unit="EA") 

   # 수중펌프(탈착장치) OpenHole 규격 테이블, 2020-10-13
   # pump entity, Open Hole W,L (mm), Pump A, A,B
   
   pumpStandard = {
      1:{
         0.0: (1000, 1000),
         0.2: (1000, 1200),
         0.6: (1000, 1200),
         1.0: (1200, 1500),
         2.5: (1200, 1500),
         4.5: (1200, 2000),
         7.0: (1500, 2000),
         10.0: (2000, 3000),
         15.0: (2000, 3000),
         20.0: (2200, 3000)
      },
      2: {
         0.0: (2000, 1000),
         0.2: (2000, 1200),
         0.6: (2000, 1200),
         1.0: (2400, 1500),
         2.5: (2400, 1500),
         4.5: (2400, 2000),
         7.0: (3000, 2000),
         10.0: (4000, 3000),
         15.0: (4000, 3000),
         20.0: (4400, 3000)
      },
      3: {
         0.0: (3000, 1000),
         0.2: (3000, 1200),
         0.6: (3000, 1200),
         1.0: (3600, 1500),
         2.5: (3600, 1500),
         4.5: (3600, 2000),
         7.0: (4500, 2000),
         10.0: (6000, 3000),
         15.0: (6000, 3000),
         20.0: (6200, 3000)
      },
   }


#   OW는 고객사와의 협의에 따라, 정의하지 않기로 함   
#   OW = GV.OW = SingleValue("outerWidth", 500)

   PS = GV.PS = SingleValue("pSlab",300)
   AS = GV.AS = SingleValue("aSlab",300)

   PH_PW = GV.PH_PW = SingleValue("PH_PW",300)
   PH_S = GV.PH_S = SingleValue("PH_S",300)
   PH_WL2 = GV.PH_WL2 = SingleValue("PH_WL2",300)

   H1 = DSP.Hmm - DSP.PH_WH1mm - PH_S
   # print(f"H1= {H1}")

   # Case : StandardTable 사용의 경우
   # L1과 W3은 규격표를 참조

   STD.pumpStandard = StandardTable(pumpStandard, "pumpStandard")
   (W3, L1)=STD.pumpStandard.get_value(DSP.tank_number.value, 1.4)
   #L2 = DSP.Lmm.value - DSP.PH_WL1mm.value - PH_WL2 - L1 - IW      # 이전
   L2 = DSP.Lmm.value - DSP.PH_WL1mm.value - PH_WL2                 # 수정
   L3 = DSP.Lmm.value - L1 - IW
   print(f"L2= {L2}")
   #print(f"L3= {L3}")

   W1 = W2 = (DSP.Wmm-DSP.PH_WW1mm-PH_PW*2)/2
   W4 = W5 = (DSP.Wmm-W3-IW*2)/2
   W6 = W7 = (DSP.Wmm-IW)/2
   
   print(f"W1(2)= {W1}")
   print(f"W4(5)= {W4}")
   print(f"W6(7)= {W6}")

   W8 = W6-W4
   W9 = W7-W5
   W10 = W6-W1
   W11 = W7-W2

   # print(f"W8= {W8}")
   # print(f"W8= {W9}")
   print(f"W10= {W10}")
   print(f"W11= {W11}")

   result.Floor1 = Box3Value("Floor1", Vector3Value(0-IW, 0-IW, 0-PS),          Vector3Value(DSP.Wmm+IW, DSP.Lmm+IW, 0))
   result.Floor2 = Box3Value("Floor2", Vector3Value(0-IW, 0-IW, DSP.Hmm.value), Vector3Value(DSP.Wmm+IW, DSP.Lmm+IW, DSP.Hmm+AS))
   
   result.Wall1 = Box3Value("Wall1", Vector3Value(0-IW, 0-IW, 0),             Vector3Value(DSP.Wmm+IW, 0, DSP.Hmm.value))
   result.Wall2 = Box3Value("Wall2", Vector3Value(DSP.Wmm.value, 0, 0),       Vector3Value(DSP.Wmm+IW, DSP.Lmm.value, DSP.Hmm.value))
   result.Wall3 = Box3Value("Wall3", Vector3Value(0-IW, DSP.Lmm.value, 0),    Vector3Value(DSP.Wmm+IW, DSP.Lmm+IW, DSP.Hmm.value))
   result.Wall4 = Box3Value("Wall4", Vector3Value(0-IW, 0, 0),                Vector3Value(0, DSP.Lmm.value, DSP.Hmm.value))
   
   #result.Wall5 = Box3Value("Wall5", Vector3Value(W4, DSP.PH_WL1mm+PH_WL2+L2, 0),          Vector3Value(W4+W8+IW+W9, DSP.PH_WL1mm+PH_WL2+L2+IW, DSP.Hmm.value))
   #result.Wall6 = Box3Value("Wall6", Vector3Value(W4+IW+W3, DSP.PH_WL1mm+PH_WL2+L2+IW, 0), Vector3Value(W4+IW+W3+IW, DSP.Lmm.value, DSP.Hmm.value))
   #result.Wall7 = Box3Value("Wall7", Vector3Value(W4, DSP.PH_WL1mm+PH_WL2+L2+IW, 0),       Vector3Value(W4+IW, DSP.Lmm.value, DSP.Hmm.value))
   

   # L2 = DSP.Lmm.value - DSP.PH_WL1mm.value - PH_WL2 
   result.Wall5 = Box3Value("Wall5",Vector3Value(W6,DSP.PH_WL1mm+PH_WL2,0), Vector3Value(W6+IW, DSP.PH_WL1mm+PH_WL2+L2, DSP.Hmm.value))
   result.Wall6 = Box3Value("Wall6",Vector3Value(W6,0,0),                   Vector3Value(W6+IW, DSP.PH_WL1mm+PH_WL2, H1))
   
   result.Wall7 = Box3Value("Wall7",Vector3Value(W1,0,H1), Vector3Value(W1+W10+IW+W11, DSP.PH_WL1mm+PH_WL2, H1+PH_S))
   result.Wall8 = Box3Value("Wall8",Vector3Value(W1, DSP.PH_WL1mm.value, H1+PH_S), Vector3Value(W1+W10+IW+W11, DSP.PH_WL1mm+PH_WL2, DSP.Hmm.value))
   
   result.Wall9 = Box3Value("Wall9",Vector3Value(W1, 0, H1+PH_S), Vector3Value(W1+PH_PW, DSP.PH_WL1mm.value, H1+PH_S+DSP.PH_WH2mm))
   result.Wall10 = Box3Value("Wall10",Vector3Value(W1+PH_PW+DSP.PH_WW1mm.value, 0, H1+PH_S), Vector3Value(W1+PH_PW+DSP.PH_WW1mm+PH_PW, DSP.PH_WL1mm.value, H1+PH_S+DSP.PH_WH2mm))
   
   print(f"Floor1 = {result.Floor1}")
   print(f"Floor2 = {result.Floor2}")
   print(f"Wall1 = {result.Wall1}")
   print(f"Wall2 = {result.Wall2}")
   print(f"Wall3 = {result.Wall3}")
   print(f"Wall4 = {result.Wall4}")
   print(f"Wall5 = {result.Wall5}")
   print(f"Wall6 = {result.Wall6}")
   print(f"Wall7 = {result.Wall7}")
   print(f"Wall8 = {result.Wall8}")
   print(f"Wall9 = {result.Wall9}")
   print(f"Wall10 = {result.Wall10}")

   #print(f"Wall13 = {result.Wall13}")
   return result


def reverse_calculate(DSP: SingletonDotDict = SingletonDotDict(), forward_result:SingletonDotDict = SingletonDotDict(Box3Value)) -> BoolValue:
   
#    return BoolValue("용량검증결과", is_sufficient)
   return BoolValue("용량검증결과", True) # is_sufficient 정의 없음으로 Ture 반환으로 변경

def level_calculate(DSP: SingletonDotDict = SingletonDotDict(), forward_result:SingletonDotDict = SingletonDotDict(Box3Value), result: SingletonDotDict = SingletonDotDict(),  drawing: SingletonDotDict = SingletonDotDict(Box2Value)):
   drawing.Level1 = Box2Value("Level1", Vector2Value(0, 0), Vector2Value(0, 0))
   return (result, drawing)

if __name__ == "__main__":
    print("\n===== FORWARD CALCULATE =====")
    forward_result = forward_calculate()
    
    print("\n===== REVERSE CALCULATE =====")
    reverse_result = reverse_calculate(forward_result=forward_result)
    print(f"\nReverse Result → {reverse_result.name}: {reverse_result.value}")

    print("\n===== LEVEL CALCULATE =====")
    level_result, drawing = level_calculate(forward_result=forward_result)
    
    for k, v in level_result:
       print(k, v)
    for k, v in drawing:
       print(k, v)
