from m5stack import *
from m5ui import *
import espnow
import wifiCfg
import hat

joy_pos = None
paired = False
addr = None
data = None

setScreenColor(0x000000)
axp.setLDO2Volt(2.8)
hat_joyc0 = hat.get(hat.JOYC)

label0 = M5TextBox(22, 48, "Text", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label1 = M5TextBox(22, 62, "Text", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label2 = M5TextBox(22, 76, "Text", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label3 = M5TextBox(22, 90, "Text", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label4 = M5TextBox(22, 104, "Unpaired", lcd.FONT_Default, 0xFFFFFF, rotate=0)
titlebar = M5Title(title="text", x=3, fgcolor=0xFFFFFF, bgcolor=0x5b5b5b)

def main():
  hat_joyc0.SetLedColor(0x3232ff)
  
  wifiCfg.wlan_ap.active(True)
  wifiCfg.wlan_sta.active(True)
  espnow.init()
  espnow.recv_cb(receive_msg)

  timerSch.run('UpdatePosition', 10, 0x00)
  timerSch.run('UpdateBattery', 1000, 0x00) 

@timerSch.event('UpdatePosition')
def tUpdatePosition():
  global joy_pos

  joy_pos = [hat_joyc0.GetX(0), hat_joyc0.GetY(0), hat_joyc0.GetX(1), hat_joyc0.GetY(1)]

  label0.setText(str(joy_pos[0]))
  label1.setText(str(joy_pos[1]))
  label2.setText(str(joy_pos[2]))
  label3.setText(str(joy_pos[3]))

  if paired == True:
    #TODO: Add msg type code, and check at receiver.
    espnow.send(id=1, data=bytes(joy_pos))
  pass

@timerSch.event('UpdateBattery')
def tUpdateBattery():
  titlebar.setTitle(str("%.1fv %.0fma"%(float(axp.getBatVoltage()), float(axp.getBatCurrent()))))
  pass

def receive_msg(_):
  global addr, data, paired
  addr, _, data = espnow.recv_data(encoder='str')
  label4.setText(str(data))

  if paired == False:
    #TODO: check if is this a mac address?
    espnow.add_peer(str(data), id=1)
    espnow.send(id=1, data=str('connected'))
    paired = True
    label4.setText(str('paired'))
    pass
  else:
    pass



main()