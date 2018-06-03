import sys,os
sys.path.insert(0, "/Users/codywu/shadows/github2/WebWhatsapp-Wrapper")
# set Chrom Driver Path
os.environ["PATH"] = os.environ["PATH"] + ":/Users/codywu/shadows/github/whatsapp_api/WebWhatsAPI/"

# set Selenium module Path
sys.path.insert(0, "/Library/Python/2.7/site-packages/selenium-3.8.0-py2.7.egg/")
sys.path.insert(0, "/Library/Python/2.7/site-packages/")

import time
from webwhatsapi import WhatsAPIDriver
from webwhatsapi.objects.message import Message
import threading
from Queue import Queue
from datetime import datetime
from threading import RLock

from selenium.webdriver.common import service

print("Bot started")

inputMessages  = Queue()
keepPolling    = True
driverLock     = RLock()

def messagePolling(drv):
  try:
    while keepPolling:
      time.sleep(1)

      print("[Polling Thread] Checking for incoming messages")
      with driverLock:
        for contact in drv.get_unread():
          for message in contact.messages:
            # only text message has content displayed, audio/image only has type displayed
            if isinstance(message, Message):
              inputMessages.put((contact.chat, message))
  except Exception as e:
    print("[Polling Thread] exception caught in messagePolling thread: {0}".format(e))

  print("[Polling Thread] MessagePolling thread exit now")

def newMessageCallback(chat, message):
  print("From [{0} / {1}] at {2}: {3}".format(message.sender.push_name, message.sender.formatted_name, message.timestamp, message.safe_content))
  with driverLock:
    chat.send_message("thanks for your message '{0}' at {1}".format(message.safe_content, message.timestamp))
  # add other logic here

def timerCallback(drv):
  print("timer callback")
  # add other logic here
  with driverLock:
    c = drv.get_chat_from_phone_number("11234567890")
    #if c:
    #  c.send_message("I love max at {0}".format(str(datetime.now())))

def main():
  # start new chrom under the script's control
  driver = WhatsAPIDriver(client="chrome", chrome_options=[])
  print("Waiting for QR")
  driver.wait_for_login()

  print("Whatsapp Bot started ...")
  time.sleep(3)

  startLoop = True

  contacts = driver.get_contacts()
  print("contacts={0}".format(contacts))

  backgroundThread = None
  try:
    backgroundThread = threading.Thread(target=messagePolling, args=(driver,))
    backgroundThread.start()
  except Exception as e:
    print("caught exception in early stage: {0}".format(e))
    startLoop = False

  if startLoop:
    try:
      tLast = time.time()

      while True:
        # check new messages, 10 messages at most
        numProcessed = 0
        while (not inputMessages.empty()) and numProcessed < 10:
          m = inputMessages.get()
          newMessageCallback(m[0], m[1])
          numProcessed += 1

        # periodic timer callback, every 10 seconds
        if time.time() > tLast + 10:
          timerCallback(driver)
          tLast = time.time()
    except KeyboardInterrupt:
      print("keyboard interrupt caught")
    except Exception as e:
      print("unknown exception caught: {0}".format(e))

  else:
    print("skip starting main loop")

  KeepPolling = False
  if backgroundThread:
    backgroundThread.join()
    print("background polling thread joined")

if __name__ == "__main__":
  main()
