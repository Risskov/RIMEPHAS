import snowboydecoder
import speech_recognition as sr
import re

class Speech():
    def __init__(self, threadevent):
        self.Interrupted = False
        self.no_detected = False
        self.yes_detected = False
        self.timeout = 0.
        self.threadevent = threadevent
        
    ########## Functions for Snowboy keyword detection - used when not connected to internet ##########
    def signal(self):
        self.interrupted = True

    def interrupt_callback(self):
        self.timeout += 0.03
        if self.threadevent.is_set():
            return True
        if self.timeout > 5:
            print("Timeout happened")
            return True
        return self.interrupted

    # Callback function for detected "yes"
    def detected_callback1(self):
        print("callback 1")
        self.signal()
        self.yes_detected = True
        
    # Callback function for detected "no"
    def detected_callback2(self):
        print("callback 2")
        self.signal()
        self.no_detected = True

    def listen_for_two_cmds(self, cmd1, cmd2):
        self.interrupted = False
        self.timeout = 0.
        detector = snowboydecoder.HotwordDetector(
            [f"resources/models/{cmd1}.pmdl",f"resources/models/{cmd2}.pmdl"], sensitivity=[0.5,0.5])
        detector.start(detected_callback=[self.detected_callback1, self.detected_callback2],
                   interrupt_check=self.interrupt_callback,
                   sleep_time=0.03)
        detector.terminate()
        print("Terminated")
        
    ########## Function for Google Speech Recognition - used when connected to internet ###########
    def google_in(self, lang):
        r = sr.Recognizer()
        r.pause_threshold = 0.5
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            print("Say something!")
            try:
                audio = r.listen(source, timeout=3, phrase_time_limit=2)
            except sr.WaitTimeoutError:
                return "Timeout"
            else:
                try:
                    out = r.recognize_google(audio, language=lang)
                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))
                else:
                    return out
            return "Error"
        
    # Search for keywords in string from Google SR
    def findWholeWord(self, w):
        return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

    ########## Speech recognition main function ##########
    def speech_in(self, cmd1, cmd2, language, isOnline):
        self.yes_detected = False
        self.no_detected = False
        if cmd1 == "yes" and language == "da-DK":
            cmdList1 = ["ja", "gerne", "jo", "ok"]
            cmdList2 = ["nej", "ellers tak"]
        elif cmd1 == "yes" and language == "en-US":
            cmdList1 = [cmd1, "please", "ok", "alright", "why not", "yeah", "i guess", "sure"]
            cmdList2 = [cmd2, "don't"]
        else:
            cmdList1 = [cmd1]
            cmdList2 = [cmd2]
        if not isOnline:
            self.listen_for_two_cmds(cmd1, cmd2)
        else:    
            gin = self.google_in(language)
            for cmd in cmdList1:
                if self.findWholeWord(cmd)(gin):
                    self.yes_detected = True
                    return
            for cmd in cmdList2:
                if self.findWholeWord(cmd)(gin):
                    self.no_detected = True
                    return

