from googletrans import Translator
translator = Translator()

out=translator.translate("आप कैसे हैं",dest="en")
print(out.text)