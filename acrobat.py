import win32com.client, win32com.client.makepy, os, winerror, errno, re, pythoncom, base64
from win32com.client.dynamic import ERRORS_BAD_CONTEXT
from collections import namedtuple


def format_path_for_js(path):
    return '/' + path.replace(':\\', '/').replace('\\','/')


class Acrobat:

    error = False
    file_load = False

    def __init__(self, file_src=""):

        pythoncom.CoInitialize()
        ERRORS_BAD_CONTEXT.append(winerror.E_NOTIMPL)

        self.input_file_name = file_src
        self.pdDoc = win32com.client.DispatchEx('AcroExch.PDDoc')\

        if not os.path.exists(file_src):
            file_src = os.path.abspath(os.path.join('example.pdf'))

        print("открываем pdf "+file_src)

        self.pdDoc.Open(file_src)

        self.jObject = self.pdDoc.GetJSObject()

    def add_sing_placeholder(self):
        inch = 72;
        box = self.jObject.getPageBox();
        lbox = list(box);
        lbox[0] = box[0] + 0.5 * inch;
        lbox[2] = lbox[0] + 2 * inch;
        lbox[1] = lbox[1] - 0.5 * inch;
        lbox[3] = lbox[1] - 0.5 * inch;
        box = tuple(lbox);
        print("Добавили место для подписи")
        return self.jObject.addField("Sig_pdf", "signature", 0, box);

    def remove_sing_placeholder(self):
        self.jObject.removeField("Sig_pdf");
        self.jObject.ResetForm();

    def sing_placeholder_exist(self):
        if self.jObject.getField("Sig_pdf"):
            return True
        else:
            return False

    def sing_document(self, pfx_path, password):
        placeholder = self.get_sig_placeholder()
        if not placeholder:
            placeholder = self.add_sing_placeholder()
        elif self.sing_exist():
            print('Подпись уже есть')
            return {'status': 'error', 'message': 'подпись уже существует'}

        print("Используем файл для подписи" + pfx_path)
        print("Используем пароль сертификта "+password)
        path_pfx_js = format_path_for_js(pfx_path)

        self.jObject.AddSignature(path_pfx_js, password, placeholder, "Adobe.PPKLite")

        if self.sing_exist():
            print("Подписали документ!")
            return True
        else:
            print("Не удалось подписать документ")
            return {'status': 'error', 'message': 'Не удалось подписать документ'}


    def get_sig_placeholder(self):
        return self.jObject.getField('Sig_pdf')

    def sing_exist(self):
        placeholder = self.jObject.getField('Sig_pdf')
        sig_info = placeholder.signatureInfo()
        if len(sig_info.certificates) == 0:
            return False
        else:
            return True

    def create_new_sert(self, name, email, org, password, path_root):

        print('Имя для генерации: '+name)
        print('Организация для генерации: '+org)
        print('Email для генерации: '+email)
        print('Пароль для генерации: '+password)

        path = os.path.abspath(os.path.join(path_root, 'upload', org+'.pfx'))
        path_crt = path.replace('.pfx', '.cer');
        path_crt_js = format_path_for_js(path_crt)

        print("Временный файл для pfx " + path)
        print("Временный файл для cer " + path_crt)

        self.jObject.CreateNewCert(name, email, org, password, path)

        print("pfx создан!!!")

        ppklite = self.jObject.security.getHandler("Adobe.PPKLite");
        ppklite.login(password, path);

        ids = ppklite.digitalIDs;
        oCert=ids.oEndUserSignCert;
        self.jObject.security.exportToFile(oCert, path_crt_js);
        print("cer создан!!!")

        with open(path, 'rb') as pfx_file:
            pfx_data = pfx_file.read()

        with open(path_crt, 'rb') as cer_file:
            cer_data = cer_file.read()

        cert_data = {
            'pfx': base64.b64encode(pfx_data).decode("utf-8"),
            'cer': base64.b64encode(cer_data).decode("utf-8"),
            'SerialNumber': oCert.serialNumber,
            'SHA1': oCert.SHA1Hash,
            'MD5': oCert.MD5Hash,
            'X509': oCert.Binary,
            'ValidityEnd': oCert.privateKeyValidityEnd,
            'ValidityStart': oCert.privateKeyValidityStart,
        }
        print("base64 сертификатов получены и записаны в ответ")
        # delete file
        os.remove(path)
        os.remove(path_crt)
        print("Временные файлы удалены!")
        return cert_data

    def finish(self, save_to=""):
        save_path = self.input_file_name
        if save_to:
            save_path = save_to

        res = self.pdDoc.Save(1, save_path)
        if res:
            print("Файл сохранен в " + save_path)
        else:
            print("Файл не сохранен, акробату не удалось сохранить файл, проверте права на запись ")
