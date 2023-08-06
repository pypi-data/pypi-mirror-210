import threading, _thread
import requests
import json
import time

class library():

  def __init__(self, license_key, email, debug=False):
    checkValidation = threading.Thread(target=self.validate, args=[license_key, email, debug])
    checkValidation.start()

  def validate(self, license_key, email, debug):
    while (True):
      try:
        validation = requests.get(
          f"https://licensing.sr.flipr.ai/api/actions/validate/",
          headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
          },
          data=json.dumps({
            "email": f"{email}",
            "key": f"{license_key}"
          })
        )
        validation_code = validation.json()
        if debug:
          print(f"[{validation.status_code}] Response >> Status:", validation_code)

        if (validation.status_code != '200'):
          if (validation.status_code/400 == 1):
            _thread.interrupt_main()

          invalid_code =  validation_code == "SUSPENDED" or \
                          validation_code == "INVALID"   or \
                          validation_code == "EXPIRED"   or \
                          validation_code == "USER_SCOPE_MISMATCH"

          if invalid_code:
            _thread.interrupt_main()
            if validation_code == "SUSPENDED":
              raise Exception("License is suspended. Please contact the library administrator.\n")
            if validation_code == "INVALID":
              raise Exception("Invalid License Key. Please recheck license_key.\n")
            if validation_code == "EXPIRED":
              raise Exception("License Key has been expired.\n")
            if validation_code == "USER_SCOPE_MISMATCH":
              raise Exception("Incorrect email id. Verify email id.\n")
        # time.sleep(60*60*24)        # 1 day
        time.sleep(10)              # Every 10 secs

      except requests.ConnectionError:
        _thread.interrupt_main()
        raise Exception("License validation request could not be made. Please make sure you are connected to the internet.\n")


  def some_other_process(self):
    counter = 0;
    while True:
      time.sleep(1)
      print(f"Main thread: {counter}")
      counter+=1

