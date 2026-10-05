from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

Builder.load_file("design.kv")


class CalculatorLayout(BoxLayout):

  def press_number(self, instance):
    basilan = instance.text
    mevcut_ekran = self.ids.screen.text

    if basilan == "AC":
      self.ids.screen.text = "0"


    elif basilan == "|<-":
      if len(mevcut_ekran) > 1:
        self.ids.screen.text = mevcut_ekran[:-1]  
      else:
        self.ids.screen.text = "0"  


    elif mevcut_ekran == "0":
      self.ids.screen.text = basilan


    else:
      self.ids.screen.text = mevcut_ekran + basilan



  def calculate(self, instance):
    try:
      sonuc = str(eval(self.ids.screen.text))
      if sonuc.endswith(".0"):
        sonuc = sonuc[:-2]

      self.ids.screen.text = sonuc
    except Exception:
      self.ids.screen.text = "Hata"


class Calculator(App):

  def build(self):
    return CalculatorLayout()


if __name__ == "__main__":
  Calculator().run()