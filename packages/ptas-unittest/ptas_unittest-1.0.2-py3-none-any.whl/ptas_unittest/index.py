import sys, requests, json, random, os, io
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
# from bs4 import BeautifulSoup as bs
# from urllib.request import urlopen
from PyQt5.uic import loadUi
from datetime import datetime


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
# def resource_path(relative_path):
#     """ Get absolute path to resource, works for dev and for PyInstaller """
#     try:
#         # PyInstaller creates a temp folder and stores path in _MEIPASS
#         base_path = sys._MEIPASS
#     except Exception:
#         base_path = os.path.abspath(".")

#     return os.path.join(base_path, relative_path)


API_UI = resource_path("API_UI.ui")
dialog = resource_path("dialog.ui")

Ui_MainWindow, QtBaseClass = uic.loadUiType(API_UI)
Ui_PopBox, QtSubClass = uic.loadUiType(dialog)

# form = resource_path("API_UI.ui")
# form_class = uic.loadUiType(form)[0]

from_class = uic.loadUiType(API_UI)[0]
from_dialog = uic.loadUiType(dialog)[0]
BASE_URL = ''
headers = []
user_info = []
status = []
api = ''
parameters = ''
parameters_id = ''
payload = ''
sequence = []
methods = []
url = ''
parameter_text = []
index = 0


class MyWindow(QMainWindow, from_class):
  def __init__(self):
    super().__init__()
    self.setupUi(self)

    self.set_api_url()

    self.btn_connect.clicked.connect(self.connect_api)
    self.btn_login.clicked.connect(self.login)
    self.btn_add_url.clicked.connect(self.click_add_seq)
    self.btn_start.clicked.connect(self.start_test)
    self.btn_clear_seq.clicked.connect(self.clear_list)
    self.btn_clear_payload.clicked.connect(self.clear_list)
    self.btn_clear_log.clicked.connect(self.clear_list)
    self.btn_clear_url.clicked.connect(self.clear_list)
    self.btn_add_parameter_id.clicked.connect(self.click_add)
    self.btn_add_company_id.clicked.connect(self.click_add)
    self.btn_random_seq.clicked.connect(self.random_sequence)
    self.btn_random_payload.clicked.connect(self.random_payload)

    self.parameters_list.itemClicked.connect(self.set_parameters_item)
    self.api_list.clicked.connect(self.click_list)
    self.method_list.clicked.connect(self.click_list)
    self.sequence_list.doubleClicked.connect(self.click_seq)
    # self.api_list.doubleClicked.connect(self.set_payload)


  # api server 파일 읽기
  def set_api_url(self):
    filename = 'list.txt'
    f = open(resource_path(filename)).read()
    buf = io.StringIO(f)
    lines = buf.readlines()
    lines = list(map(lambda s: s.strip(), lines))
    cnt = 0
    for i in range(len(lines)//3):
      i = cnt
      self.url_list.addItem(lines[i])
      cnt = i+3

  # api server 연결
  def connect_api(self):
    global BASE_URL
    BASE_URL = self.url_list.currentText()
    api_list = []
    parameter_list = []
    self.api_list.clear()
    self.parameters_list.clear()

    filename = 'list.txt'
    f = open(resource_path(filename)).read()
    buf = io.StringIO(f)
    lines = buf.readlines()
    lines = list(map(lambda s: s.strip(), lines))

    for i in range(len(lines)):
      api_url = lines[i]
      if api_url == BASE_URL:
        api_list = lines[i+1].split(',')
        parameter_list = lines[i+2].split(',')
        break
      else:
        i = i+3

    for api in api_list:
      self.api_list.addItem(api)
    for param in parameter_list:
      self.parameters_list.addItem(param)

  # 로그인
  def login(self):
    info = []
    user_id = self.user_id.text()
    user_password = self.user_password.text()
    if user_id == '' or user_password == '':
      self.set_error_code('No login data')
      return
    info.append(user_id)
    info.append(user_password)
    resp = self.get_access_token(info)

  # access token 가져오기
  def get_access_token(self, info):
    global headers
    global user_info
    global status
    
    data = {
      "user" : info[0],
      "password" : info[1]
    }
    url = BASE_URL + "auth"
  
    response = requests.post(url, json=data)
    
    if response.json()['result'] == 'Denied':
      self.set_result(response.status_code, 'POST', 'auth')
      return 

    access_token = response.json()["access_token"]
    company_id = response.json()["response"]["company_id"]
    company_type = response.json()["response"]["company_type"]
    status = response

    headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + access_token
    }
    user_info = {
      'company_id': company_id,
      'company_type': company_type
    }

    # self.set_status_code(status, 'GET', 'auth')
    # self.log_list.append('company_id='+str(company_id))
    self.set_result(response.status_code, 'POST', 'auth')

    return status

  # sequence add 버튼
  def click_add_seq(self):
    global url
    global sequence
    global methods
    global parameter_text
    
    if url == '' or self.method_text.text() == '': 
      self.set_error_code('No data')
      return
    sequence.append(url)
    methods.append(self.method_text.text()) 

    txt = self.method_text.text() + ' - ' + url
    self.sequence_list.addItem(txt)
    parameter_text.append(self.payload_text.toPlainText().replace('\n', ''))

    self.method_text.clear()
    self.api_url.clear()
    self.payload_text.clear()
    url = ''

  # parameter label set
  def set_parameters_item(self):
    global parameters
    parameters = self.parameters_list.currentItem().text()
    self.parameters_label.setText(parameters)

  # log 추가
  def set_status_code(self, resp, method, url):
    msg = '['+ str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '] ' + str(resp) + ' ' + method + ' ' + url
    self.log_list.append(msg)
  
  # error log
  def set_error_code(self, error):
    msg = '['+ str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '] ' + error
    self.log_list.append(msg)

  # test start 버튼
  def start_test(self):
    global methods
    global sequence
    global parameter_text
    response = ''
    success = 0
    fail = 0
    for i in range(len(methods)):
      params = parameter_text[i]
      if params != '':
        params = json.loads(params)

      if methods[i] == 'GET':
        response = requests.get(url=BASE_URL+sequence[i], headers=headers, params=params)
      elif methods[i] == 'POST':
        response = requests.post(url=BASE_URL+sequence[i], headers=headers, json=params)
      elif methods[i] == 'PUT':
        response = requests.put(url=BASE_URL+sequence[i], headers=headers, json=params)
      elif methods[i] == 'DELETE':
        response = requests.delete(url=BASE_URL+sequence[i], headers=headers, json=params)
      # self.set_status_code(response, methods[i], sequence[i])
      self.set_result(response.status_code, methods[i], sequence[i])
      print(response.text)
      if response.status_code == 200: 
        success += 1
      else:
        fail += 1
        if response.status_code == 204:
          self.log_list.append('No contents')
        else:
          self.log_list.append(response.text)
        break
    result = '[ Success=' + str(success) + ', Fail=' + str(fail) + ' ]\n'
    self.log_list.append(result)
    


  def set_result(self,status, method, url):
    msg = '['+ str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '] < ' + str(status) + ' > ' + method + '  ' + url
    self.log_list.append(msg)

  # clear 버튼
  def clear_list(self):
    global methods
    global sequence
    global payload
    global url
    global parameter_text

    name = self.sender().objectName()
    if name == 'btn_clear_seq':
      methods = []
      sequence = []
      parameter_text = []
      self.sequence_list.clear()
    elif name == 'btn_clear_payload':
      payload = ''
      self.payload_text.clear()
    elif name == 'btn_clear_log':
      self.log_list.clear()
    elif name == 'btn_clear_url':
      url = ''
      self.api_url.clear()

  # method & api list 클릭
  def click_list(self):
    global url
    name = self.sender().objectName()
    if name == 'api_list':
      url = url + '/' +self.api_list.currentItem().text()
      self.api_url.setText(url)
    elif name == 'method_list':
      method = self.method_list.currentItem().text()
      self.method_text.setText(method)

  # add 버튼
  def click_add(self):
    global url
    global parameters_id
    global parameters
    name = self.sender().objectName()
    if name == 'btn_add_company_id':
      if '?' in self.api_url.text():
        self.set_error_code('url format is invalid')
      elif self.company_id.text() == '':
        self.set_error_code('No data')
      else:
        url = url + '/' + self.company_id.text()
      self.api_url.setText(url)
      self.company_id.clear()
    elif name == 'btn_add_parameter_id':
      if self.parameters_list.currentItem() == None or self.parameters_id.text() == '':
        self.set_error_code('No Parameter')
      else:
        parameters = self.parameters_list.currentItem().text()
        parameters_id = self.parameters_id.text()
        if '?' in self.api_url.text():
          url = url + '&' + parameters + '=' + parameters_id
        else:
          url = url + '?' + parameters + '=' + parameters_id
        self.api_url.setText(url)
        self.parameters_id.clear()
  
  # payload 상세보기
  def click_seq(self):
    global parameter_text
    global index
    dialog = ParmeterDialog(self)
    index = self.sequence_list.currentRow()
    dialog.parameter_text.setText(parameter_text[index])
    dialog.exec()

  # random 버튼
  def random_sequence(self):
    global parameter_text
    global sequence
    global methods

    new_param = []
    new_seq = []
    new_mth = []

    enum_list = list(enumerate(sequence))
    random.shuffle(enum_list)
    list_of_lists = [list(t) for t in enum_list]
    
    for item in list_of_lists:
      original_index = item[0]
      new_param.append(parameter_text[original_index])
      new_seq.append(item[1])
      new_mth.append(methods[original_index])
      
    parameter_text = new_param
    sequence = new_seq
    methods = new_mth

    self.sequence_list.clear()

    for i in range(len(sequence)):
      txt = methods[i] + ' - ' + sequence[i]
      self.sequence_list.addItem(txt)
      
  def random_payload(self):
    method_info = self.method_text.text()
    self.payload_text.clear()
    if method_info == 'POST' or method_info == 'PUT':
      item = self.api_list.currentItem().text()

      filename = 'payload.txt'
      f = open(resource_path(filename)).read()
      buf = io.StringIO(f)
      lines = buf.readlines()
      lines = list(map(lambda s: s.strip(), lines))
      for i in range(len(lines)):
        info = lines[i].split('|')

        if info[0] == method_info and info[1] == item:
          self.payload_text.setPlainText(info[2])
    # else:
    #   self.payload_text.clear()


class ParmeterDialog(QDialog, from_dialog):
  def __init__(self, parent=None):
    super().__init__(parent)
    loadUi("dialog.ui", self)

    self.btn_cancel.clicked.connect(self.close)
    self.btn_save.clicked.connect(self.click_save)

  def close(self):
    self.accept()

  def click_save(self):
    global parameter_text
    global index

    parameter_text[index] = self.parameter_text.toPlainText()
    self.accept()

    
    

if __name__ == "__main__":
  app = QApplication(sys.argv)
  mywindow = MyWindow()
  mywindow.show()
  app.exec_()