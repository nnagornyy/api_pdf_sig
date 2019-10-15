from urllib import response

from acrobat import Acrobat;
import os, datetime

# src = os.path.abspath("C:\\util\\test_sing.pdf")
# sig = os.path.abspath("C:\\util\\sig.pfx")
# password = "15926"
#
#
# acrobat = Acrobat(src)
#
# # if acrobat.singExist():
# #     print("место под подпись найдено, удалим его")
# #     acrobat.remove_sing_placeholder()
# #     print("удалили =)")
# # else:
# #     print("место под подпись не найдено, добавим")
# #     acrobat.add_sing_placeholder()
# #     print("добавили подпись")
# # acrobat.sing_exist()
# response = acrobat.sing_document(sig, password)
# if not response == True:
#     print(response.get('message'))
# #acrobat.finish()
path = os.path.abspath(os.path.join('upload'))
now = datetime.datetime.now()
for r, d, f in os.walk(path):
    for file in f:
        file_date = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join('upload', file)))
        delta = now - file_date
        if(delta.seconds / 60 > 20):
            print('удалим '+ file)
