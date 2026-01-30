# 25.11.25 JK
# S_CON02D에 신규 등록, H를 height로 변경
#
# 25.11.10 JK
# 데모 SBR 구조물 Drawing 되도록 초기값 변경
# W=8.7 m, L=8.7m, H=6.3m
#
# 25.11.03 Hi0
# D_TYPE
#
########################################

from WAI import SingleValue, GV, Vector3Value, Box3Value, BoolValue, Vector2Value, Box2Value, StandardTable, STD, SingletonDotDict
from typing import Dict, Any
import bisect

#공정용량계산서에서 공정에 소요되는 구조물의 용량을 가져오는건 어떻게 해야하지??일단 임의로 잡아야겠다.

def forward_calculate(DSP: SingletonDotDict=SingletonDotDict(), result:SingletonDotDict=SingletonDotDict(Box3Value)):

   DSP.W = SingleValue("W", 5.50, False, unit="m")    ## Unit = mm
   DSP.Wmm = SingleValue("W", 1.0, False, unit="mm")    ## Unit = mm
   DSP.Wmm = DSP.W*1000

   DSP.L = SingleValue("L", 8.70, False, unit="m")
   DSP.Lmm = SingleValue("L", 1.0, False, unit="mm")
   DSP.Lmm = DSP.L*1000
   
   DSP.height = SingleValue("height", 6.30, False, unit="m")
   DSP.heightmm = SingleValue("height", 1.0, False, unit="mm")
   DSP.heightmm = DSP.height.value*1000
   
   DSP.layout_type_number = SingleValue("EA", 2, False, unit="EA")
   
   IW = GV.IW = SingleValue("innerWidth", 300)
   
   # OW는 고객사와의 협의에 따라, 정의하지 않기로 함	
   # OW = GV.OW = SingleValue("outerWidth", 500)
   
   PS = GV.PS = SingleValue("pSlab", 300)
   AS = GV.AS = SingleValue("aSlab", 300)

   # Type D Wall 정의
   result.Wall1 = Box3Value("Wall1", Vector3Value(0-IW.value, 0-IW.value, 0-PS.value),         Vector3Value(DSP.Wmm.value+IW.value, DSP.Lmm.value+IW.value, 0))
   result.Wall2 = Box3Value("Wall2", Vector3Value(0-IW.value, 0-IW.value, DSP.heightmm.value), Vector3Value(DSP.Wmm.value+IW.value, DSP.Lmm.value+IW.value, DSP.heightmm.value+AS.value))
   result.Wall3 = Box3Value("Wall3", Vector3Value(0-IW.value, 0-IW.value, 0),                  Vector3Value(DSP.Wmm.value+IW.value, 0, DSP.heightmm.value))
   result.Wall4 = Box3Value("Wall4", Vector3Value(DSP.Wmm.value, 0, 0),                        Vector3Value(DSP.Wmm.value+IW.value, DSP.Lmm.value, DSP.heightmm.value))
   result.Wall5 = Box3Value("Wall5", Vector3Value(0-IW.value, DSP.Lmm.value, 0),               Vector3Value(DSP.Wmm.value+IW.value, DSP.Lmm.value+IW.value, DSP.heightmm.value))
   
   # 25.11.10 JK
   # result.Wall6 = Box3Value("Wall6", Vector3Value(0-IW,0-IW,0), Vector3Value(0,DSP.Lmm,DSP.heightmm))를 Wall 6 (-IW,0,0), (0,L,H)로 변경
   result.Wall6 = Box3Value("Wall6", Vector3Value(0-IW.value, 0, 0),                           Vector3Value(0, DSP.Lmm.value , DSP.heightmm.value ))

   return result

def reverse_calculate(DSP: SingletonDotDict = SingletonDotDict(), forward_result:SingletonDotDict = SingletonDotDict(Box3Value)) -> BoolValue:
  
   # 25.11.25 JK
   DSP.water_level = SingleValue("water_level", 5.0, False, unit="m")
   DSP.water_levelmm = SingleValue("water_level", 5.0, False, unit="m")
   DSP.water_levelmm = DSP.water_level.value*1000

   DSP.tank_number = SingleValue("EA", 2, False, unit="EA") 
   DSP.required_capacity = SingleValue("required_capacity", 150, False, unit="㎥")

   IW = GV.IW = SingleValue("innerWidth", 300)
   
   #local coordinate
   forward_result.Wall4 = Box3Value("Wall4", Vector3Value(-5500.0,    0.0,  0.0), Vector3Value(5800.0, 8700.0, 6300.0))   # Right
   forward_result.Wall5 = Box3Value("Wall5", Vector3Value( -300.0, 8700.0,  0.0), Vector3Value(5800.0, 9000.0, 6300.0))   # Back
   forward_result.Wall6 = Box3Value("Wall6", Vector3Value( -300.0,    0.0,  0.0), Vector3Value(   0.0, 8700.0, 6300.0))   # Left
   
   # global coordinate
   inner_volume = Vector3Value("inner_volume", (forward_result.Wall4.min.x - forward_result.Wall6.max.x), (forward_result.Wall5.min.y - forward_result.Wall6.min.y), DSP.water_level.value)

   volume_m3 = (inner_volume.x/1000)*(inner_volume.y/1000)*DSP.water_levelmm.value
   
   # 용량 검증
   is_sufficient = volume_m3>=DSP.required_capacity.value

   return BoolValue("용량검증결과", is_sufficient)


def level_calculate(DSP: SingletonDotDict = SingletonDotDict(), forward_result:SingletonDotDict = SingletonDotDict(Box3Value), result:SingletonDotDict = SingletonDotDict(), drawing:SingletonDotDict = SingletonDotDict(Box2Value)):
   result.power = SingleValue("power", 100)
   drawing.Level1 = Box2Value("Level1", Vector2Value(0, 0), Vector2Value(0, 0))
   return result
