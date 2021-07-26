    
class InteractionNode():
    def __init__(self, statemachine, speechNode, despenser, threadevent, isOnline):
        self.textList = []
        self.sm = statemachine
        self.threadevent = threadevent
        self.interactionWait = False
        self.sn = speechNode
        self.disp = dispenser
        self.isOnline = isOnline
    ########## Main interaction function going through interaction items to be executed ##########
    def interaction(self, *items, eyeDesign, lang):
        skip = False
        for item in items:
            if item == "nudge":
                speech_out(8+items[1])
            elif item == "30s":
                rand = 1
                if rand: speech_out(10)
                else: speech_out(11)
            elif item == "joke":
                speech_out(11+items[1])
                wait(2000)
                speech_out(12+items[1])
            elif item == "sanitizer":
                if len(items)<=1:
                    skip = interactionQuestion(0)
                else: skip = interactionQuestion(0)
            elif item == "video" and not skip:
                interactionQuestion(1)
            elif item == "monster":
                sn.speech_in(items[0], items[1], lang, isOnline)
                if sn.yes_detected:
                    eyeDesign = items[0]
                    sm.state = sm.NORMALSTATE
                elif sn.no_detected:
                    eyeDesign = items[1]
                    sm.state = sm.NORMALSTATE
            elif item == "novideo":
                skip = interactionQuestion(3)
            self.textList = []
            if self.threadevent.is_set(): break
        self.threadevent.clear()
        if self.interactionWait: sm.state = sm.WAITSTATE
        print("Flow ended")

    ########## Interaction function for two-way communication ##########
    def interactionQuestion(self, question, lang):
        if question == 3:
            novideo = True
            question = 0
        else: novideo = False
        skip = False
        lastNumberOfActivations = self.disp.numberOfActivations # reset this if multiple questions?
        speech_out(question)
        i = 0
        skipit = 0
        
        while not threadevent.is_set():
            listenthread = threading.Thread(target=self.sn.speech_in, args=("yes","no", lang, self.isOnline))
            listenthread.start()
            while listenthread.is_alive():
                if self.sn.yes_detected or self.sn.no_detected: break
                if self.disp.numberOfActivations != lastNumberOfActivations:
                    speech_out(10)
                    skipit = 1
                    break
            if skipit:
                skipit = 0
                break
            if sn.yes_detected:
                pygame.event.post(happyevent)
                speech_out(question+2)
                if question == 0:
                    if novideo:
                        iwait = 200
                        while iwait:
                            if self.disp.numberOfActivations != lastNumberOfActivations:
                                speech_out(10)
                                break
                            iwait -= 1
                            if iwait < 1:
                                break
                    else:
                        print("video")
                        wait(2000)
                    break
                else:
                    sm.state = VIDEOSTATE
                    wait(35000)
                    break
            elif sn.no_detected:
                speech_out(6)
                skip = True
                break
            elif question == 0 and self.disp.numberOfActivations != lastNumberOfActivations:
                if novideo:
                    speech_out(10)
                else: wait(2000)
                break
            elif question == 1:
                speech_out(6)
                break
            else:
                skip = True
                break
        print("Interaction ended")
        return skip
