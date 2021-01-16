from m5stack import *
from m5ui import *
from uiflow import *
import espnow
import wifiCfg
import hat


axp.setLDO2Volt(2.8)
setScreenColor(0x000000)

hat_roverc0 = hat.get(hat.ROVERC)

label0 = M5TextBox(1, 48, "Status", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label1 = M5TextBox(1, 62, "Controls", lcd.FONT_Default, 0xFFFFFF, rotate=0)

titlebar = M5Title(title="text", x=3, fgcolor=0xFFFFFF, bgcolor=0x5b5b5b)

paired = False
addr = None
data = None

def main():
  wifiCfg.wlan_ap.active(True)
  wifiCfg.wlan_sta.active(True)

  espnow.init()
  espnow.recv_cb(receive_msg)

  label0.setText(str('broadcasting'))

  timerSch.run('UpdateBattery', 1000, 0x00) 
  timerSch.run('SendDiscoveryBroadcast', 1000, 0x00)

  try:
    while True:
      pass
  except KeyboardInterrupt:
    print('Got ctrl-c')
    # Explicitly stop timers (threads) here.
    timerSch.stop('SendDiscoveryBroadcast')

@timerSch.event('UpdateBattery')
def tUpdateBattery():
  titlebar.setTitle(str("%.1fv %.0fma"%(float(axp.getBatVoltage()), float(axp.getBatCurrent()))))
  pass

@timerSch.event('SendDiscoveryBroadcast')
def tSendDiscoveryBroadcast():
  global paired
  if paired == False:
    espnow.broadcast(data=str(espnow.get_mac_addr()))
    pass
  else:
    timerSch.stop('SendDiscoveryBroadcast')
    pass

def receive_msg(_):
  global addr, data, paired
  addr, _, data = espnow.recv_data(encoder='byte')

  if paired == False:
    paired = True
    label0.setText(str('connected'))
    print('paired')
    pass
  else:
    #TODO: control actual motors to move Rover
    set_speed(data[0], data[1], data[2])

    pass

def set_speed(Vtx, Vty, Wt):
  Wt = 100 if ( Wt > 100 )  else  Wt
  Wt = -100 if ( Wt < -100 ) else Wt

  Vtx = 100 if ( Vtx > 100 )  else  Vtx
  Vtx = -100 if ( Vtx < -100 ) else Vtx
  Vty = 100 if ( Vty > 100 )  else  Vty
  Vty = -100 if ( Vty < -100 ) else Vty

  Vtx = (Vtx *  (100- abs(Wt)) / 100) if ( Wt != 0 ) else Vtx
  Vty = (Vty *  (100- abs(Wt)) / 100) if ( Wt != 0 ) else Vty

  Vtx = Vtx - 100
  Vty = Vty - 100
  Wt = Wt -100 

  print("x:"+str(Vtx)+"y:"+str(Vty)+"z:"+str(Wt))
  hat_roverc0.SetSpeed(Vtx, Vty, Wt)

main()
