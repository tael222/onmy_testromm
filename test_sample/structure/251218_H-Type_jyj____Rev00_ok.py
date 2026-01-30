#  25.12.18 JK
#  floating, hydraulic_waterlevel_ph
#  reverse calculate에서 Wall5, Wall11 주석처리
#
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
from WAI import SingleValue, GV, Vector3Value, Box3Value, BoolValue, Vector2Value, Box2Value, StandardTable, STD, SingletonDotDict
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
   #print(f"DSP.Wmm= {DSP.Wmm}")

   DSP.L = SingleValue("L", 5.5000, False, unit="m")
   DSP.Lmm = SingleValue ("Lmm", 1.0, False, unit="m")
   DSP.Lmm = DSP.L*1000
   # print(f"DSP.Lmm= {DSP.Lmm}")

   DSP.height = SingleValue("height", 6.000, False, unit="m")
   DSP.Hmm = SingleValue("heightmm", 1.0, False, unit="m")
   DSP.Hmm = DSP.height*1000
   # print(f"DSP.Hmm= {DSP.Hmm}")
    
   DSP.PH_WW1 = SingleValue("PH_WW1", 3.0, False, unit="m")
   DSP.PH_WW1mm = SingleValue("PH_WW1mm", 3.0, False, unit="m")
   DSP.PH_WW1mm = DSP.PH_WW1*1000
   # print(f"PH_WW1mm= {DSP.PH_WW1mm}")

   DSP.PH_WL1 = SingleValue("PH_WL1", 3.5, False, unit="m")
   DSP.PH_WL1mm = SingleValue("PH_WL1mm", 3.5, False, unit="m")
   DSP.PH_WL1mm = DSP.PH_WL1*1000
   # print(f"PH_WL1mm= {DSP.PH_WL1mm}")

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

   L2 = DSP.Lmm.value - DSP.PH_WL1mm.value - PH_WL2 - L1 - IW
   L3 = DSP.Lmm.value - L1 - IW
   # print(f"L2= {L2}")
   # print(f"L3= {L3}")

   W1 = W2 = (DSP.Wmm-DSP.PH_WW1mm-PH_PW*2)/2
   W4 = W5 = (DSP.Wmm-W3-IW*2)/2
   W6 = W7 = (DSP.Wmm-IW)/2
   
   # print(f"W1= {W1}")
   # print(f"W4= {W4}")
   #print(f"W6= {W6}")

   W8 = W6-W4
   W9 = W7-W5
   W10 = W6-W1
   W11 = W7-W2

   # print(f"W8= {W8}")
   # print(f"W8= {W9}")
   # print(f"W10= {W10}")
   # print(f"W11= {W11}")

   result.Floor1 = Box3Value("Floor1", Vector3Value(0-IW, 0-IW, 0-PS),          Vector3Value(DSP.Wmm+IW, DSP.Lmm+IW, 0))
   result.Floor2 = Box3Value("Floor2", Vector3Value(0-IW, 0-IW, DSP.Hmm.value), Vector3Value(DSP.Wmm+IW, DSP.Lmm+IW, DSP.Hmm+AS))
   
   result.Wall1 = Box3Value("Wall1", Vector3Value(0-IW, 0-IW, 0),             Vector3Value(DSP.Wmm+IW, 0, DSP.Hmm.value))
   result.Wall2 = Box3Value("Wall2", Vector3Value(DSP.Wmm.value, 0, 0),       Vector3Value(DSP.Wmm+IW, DSP.Lmm.value, DSP.Hmm.value))
   result.Wall3 = Box3Value("Wall3", Vector3Value(0-IW, DSP.Lmm.value, 0),    Vector3Value(DSP.Wmm+IW, DSP.Lmm+IW, DSP.Hmm.value))
   result.Wall4 = Box3Value("Wall4", Vector3Value(0-IW, 0, 0),                Vector3Value(0, DSP.Lmm.value, DSP.Hmm.value))
   
   result.Wall5 = Box3Value("Wall5", Vector3Value(W4, DSP.PH_WL1mm+PH_WL2+L2, 0),          Vector3Value(W4+W8+IW+W9, DSP.PH_WL1mm+PH_WL2+L2+IW, DSP.Hmm.value))
   result.Wall6 = Box3Value("Wall6", Vector3Value(W4+IW+W3, DSP.PH_WL1mm+PH_WL2+L2+IW, 0), Vector3Value(W4+IW+W3+IW, DSP.Lmm.value, DSP.Hmm.value))
   result.Wall7 = Box3Value("Wall7", Vector3Value(W4, DSP.PH_WL1mm+PH_WL2+L2+IW, 0),       Vector3Value(W4+IW, DSP.Lmm.value, DSP.Hmm.value))
   
   result.Wall8 = Box3Value("Wall8",Vector3Value(W6,DSP.PH_WL1mm+PH_WL2,0), Vector3Value(W6+IW, DSP.PH_WL1mm+PH_WL2+L2, DSP.Hmm.value))
   result.Wall9 = Box3Value("Wall9",Vector3Value(W6,0,0),                   Vector3Value(W6+IW, DSP.PH_WL1mm+PH_WL2, H1))
   
   result.Wall10 = Box3Value("Wall10",Vector3Value(W1,0,H1), Vector3Value(W1+W10+IW+W11, DSP.PH_WL1mm+PH_WL2, H1+PH_S))
   result.Wall11 = Box3Value("Wall11",Vector3Value(W1, DSP.PH_WL1mm.value, H1+PH_S), Vector3Value(W1+W10+IW+W11, DSP.PH_WL1mm+PH_WL2, DSP.Hmm.value))
   
   result.Wall12 = Box3Value("Wall12",Vector3Value(W1, 0, H1+PH_S), Vector3Value(W1+PH_PW, DSP.PH_WL1mm.value, H1+PH_S+DSP.PH_WH2mm))
   result.Wall13 = Box3Value("Wall13",Vector3Value(W1+PH_PW+DSP.PH_WW1mm.value, 0, H1+PH_S), Vector3Value(W1+PH_PW+DSP.PH_WW1mm+PH_PW, DSP.PH_WL1mm.value, H1+PH_S+DSP.PH_WH2mm))

   #print(f"Wall1 = {result.Wall1}")
   #print(f"Wall2 = {result.Wall2}")
   #print(f"Wall3 = {result.Wall3}")
   #print(f"Wall4 = {result.Wall4}")
   #print(f"Wall5 = {result.Wall5}")
   #print(f"Wall6 = {result.Wall6}")
   #print(f"Wall7 = {result.Wall7}")
   #print(f"Wall8 = {result.Wall8}")
   #print(f"Wall9 = {result.Wall9}")
   #print(f"Wall10 = {result.Wall10}")
   #print(f"Wall11 = {result.Wall11}")
   #print(f"Wall12 = {result.Wall12}")
   #print(f"Wall13 = {result.Wall13}")
   return result

# Type D에서 Copy
# 단순히 형식을 맞추기 위함
def reverse_calculate(DSP: SingletonDotDict = SingletonDotDict(), forward_result:SingletonDotDict = SingletonDotDict(Box3Value)) -> BoolValue:
   # 예: 목표 용량을 만족하는지 간단 검토 (실사용 시 내부 상태/모형과 비교)
   DSP.water_level = SingleValue("water_level", 5.0, False, unit="m")
   DSP.water_levelmm = SingleValue("water_level", 5.0, False, unit="m")
   DSP.water_levelmm = DSP.water_level*1000
   #print(f"DSP.water_levelmm= {DSP.water_levelmm}")

   #구조물 지수 2
   DSP.tank_number = SingleValue("EA", 2, False, unit="EA") 

   # DSP: StructureValue(구조물) 기본 정보 및 inputs값
   DSP.required_capacity = SingleValue("required_capacity", 150, False, unit="㎥")
   #print(f"DSP.required_capacity: {DSP.required_capacity.value}")

   # forward_result: 규격계산식 결과값
   # TODO: Box3Value는 IValueObject를 상속하지 않음 -> 업데이트

#   Wall5  = forward_result["Wall5"]
#   Wall11 = forward_result["Wall11"]
   Wall9  = forward_result["Wall9"]
   Wall3  = forward_result["Wall3"]
   
   # 글로벌 변수
   IW = GV.IW = SingleValue("innerWidth", 300)   # 내벽 두께
   PS = GV.PS = SingleValue("pSlab", 300)        # Floor 두께
   AS = GV.AS = SingleValue("aSlab", 300)        # Ceiling 두께

   # 내부 용량 계산을 위한 좌표
   #inner_left = Vector3Value("inner_left", forward_result.Wall1.min.x+IW, forward_result.Wall1.min.y+IW, forward_result.Wall1.min.z+PS)
   #inner_right = Vector3Value("inner_right", forward_result.Wall1.max.x-IW, forward_result.Wall1.min.y+IW, forward_result.Wall1.max.z)
   #inner_top = Vector3Value("inner_top", forward_result.Wall2.max.x-IW, forward_result.Wall2.min.y+IW, forward_result.Wall2.min.z)
   #inner_depth = Vector3Value("inner_depth", forward_result.Wall1.max.x-IW, forward_result.Wall1.max.y-IW, forward_result.Wall1.max.z)

   inner_bottom = Vector3Value("inner_length", Wall9.min.x, Wall3.min.y, 0)
   length = abs(inner_bottom.x - 0)
   width = abs(inner_bottom.y - 0)

   # 내부 용량 계산
   # x = inner_right.x - inner_left.x
   # y = inner_top.y - inner_right.y
   # z = inner_depth.z - inner_right.z
   #x = abs(inner_right.x - inner_left.x)
   #y = abs(inner_depth.y - inner_right.y)
   #z = abs(inner_top.z - inner_right.z)

   volume_m3 = length/1000*width/1000*DSP.water_levelmm/1000 * DSP.tank_number

   #print(f"length: {length}")
   #print(f"width: {width}")
   #print(f"volume_m3: {volume_m3}")
   # 용량 검증
   is_sufficient = volume_m3>=DSP.required_capacity.value

   return BoolValue("용량검증결과", is_sufficient)
   # X,Y,Z 값을 다시 공정계산서에 보내야함...(STC의 Applied Capacity값이 3D에서 변경된 값으로 반영되어야함.)

from WAI import SingleValue, Vector2Value, Box2Value, ELBoxValue, SingletonDotDict

def level_calculate(
    DSP: SingletonDotDict = SingletonDotDict(),
    forward_result: SingletonDotDict = SingletonDotDict(Box3Value),
    result: SingletonDotDict = SingletonDotDict(),
    drawing: SingletonDotDict = SingletonDotDict(Box2Value)
):

    DSP.height = SingleValue("height", 6.3000, False, unit="m")
    DSP.Hmm = SingleValue("heightmm", 1.0, False, unit="m")
    DSP.Hmm = DSP.height*1000

    DSP.water_level = SingleValue("water_level", 5.0, False, unit="m")
    DSP.water_levelmm = SingleValue("water_level", 5.0, False, unit="m")
    DSP.water_levelmm = DSP.water_level*1000

    DSP.pHWaterlevel = SingleValue("pHwater_level", 2.0, False, unit="m")
    DSP.pHWaterlevelmm = SingleValue("pHwater_level", 2.0, False, unit="m")
    DSP.pHWaterlevelmm = DSP.pHWaterlevel*1000
    
    DSP.influentsq = SingleValue("Q", 1317.1, False,"㎥/d")
    influentq_m_s = DSP.influentsq/24/60/60
    # DSP: StructureValue(구조물) 기본 정보 및 inputs값
    DSP.required_capacity = SingleValue("required_capacity", 2100, False, unit="m³")

    DSP.tank_number = SingleValue("EA", 2, False, unit="EA") 
    DSP.elevation_level = SingleValue("Elevation level", 5.0, editable=False, unit="m", display=False, summary=False, remark="Elevation level")

    # forward_result: 규격계산식 결과값
    Wall10 = forward_result["Wall10"]
    Wall12 = forward_result["Wall12"]        
        
   # 글로벌 변수
    IW = GV.IW = SingleValue("innerWidth", 300)   # 내벽 두께
    PS = GV.PS = SingleValue("pSlab", 300)        # Floor 두께
    AS = GV.AS = SingleValue("aSlab", 300)        # Ceiling 두께
    PH_S = GV.PH_S = SingleValue("PH_S",300)


    Wall12_coordinate = Vector3Value("weir_length",0, Wall12.max.y - Wall12.min.y, 0)
    weir_length = abs(Wall12_coordinate.y/1000) #mm -> m 로 변환
    Haedloss_ph = (influentq_m_s / (1.84 * weir_length)) ** (2/3) #Weir에 의한 월류 손실량
    Wall10_coordinate = Vector3Value("height of swing",0, 0, Wall10.max.z) #(그네 구조물의 위쪽 바닥면)
    Wall10_coordinate_2 = Vector3Value("weir_length",0, 0, Wall10.min.z) #(그네 구조물의 아래쪽 바닥면)    

    hydraulic_waterlevel_ph = round(Haedloss_ph + DSP.pHWaterlevel.value + Wall10_coordinate.z/1000,2) #m단위 (그네 구조물의 바닥면을 고려한 pH조정조의 수두손실량 + 수위량)
 
    # level_result: 수리계산 파라미터 결과값 (IValueObject)
    result.elevation = SingleValue("elevation", hydraulic_waterlevel_ph, False, unit="m") #수두손실 + pH조정조 높이 + pH조정조 He
    result.head_loss = SingleValue("head_loss", Haedloss_ph, False, unit="m") #수두손실량

    # level_drawing: 2D 드로잉 결과값 (Box2Value)
    #pH조정조 수리계통도
    drawing.Level1 = Box2Value("Level1", Vector2Value(0,DSP.elevation_level + Wall10_coordinate.z/1000 - PH_S/1000), Vector2Value(2, DSP.elevation_level +DSP.Hmm/1000+AS/1000)) #외부 m단위
    drawing.Level2 = Box2Value("Level2", Vector2Value(IW/1000, DSP.elevation_level + Wall10_coordinate.z/1000), Vector2Value(2-IW/1000, DSP.elevation_level + DSP.Hmm/1000)) #내부 m단위
    drawing.Level3 = ELBoxValue("Level3", Vector2Value(IW/1000, DSP.elevation_level + Wall10_coordinate.z/1000), Vector2Value(2-IW/1000, hydraulic_waterlevel_ph), elevation_level= hydraulic_waterlevel_ph) #Waterlevel m단위

    #유량조정조 수리계통도
    drawing.Level4 = Box2Value("Level4", Vector2Value(2,DSP.elevation_level - PS/1000), Vector2Value(7, DSP.elevation_level + DSP.Hmm/1000+AS/1000)) #외부 m단위
    drawing.Level5 = Box2Value("Level5", Vector2Value(IW/1000+2, DSP.elevation_level), Vector2Value(7-IW/1000, DSP.elevation_level + DSP.Hmm/1000)) #내부 m단위
    drawing.Level6 = ELBoxValue("Level6", Vector2Value(IW/1000+2, DSP.elevation_level), Vector2Value(7-IW/1000, DSP.elevation_level + DSP.water_level), elevation_level= hydraulic_waterlevel_ph) #Waterlevel m단위


    return (result, drawing)

#if __name__ == "__main__":
    #print("\n===== FORWARD CALCULATE =====")
    #forward_result = forward_calculate()
