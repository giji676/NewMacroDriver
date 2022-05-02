import logging
logging.basicConfig(level=logging.INFO)

from obswebsocket import obsws, requests  # noqa: E402


class OBS:
    def __init__(self):
        self.host = "localhost"
        self.port = 4444
        self.password = "Tengo2004"

        self.ws = obsws(self.host, self.port, self.password)
        self.ws.connect()

    def micToggle(self):
        self.ws.call(requests.ToggleMute("Mic/Aux"))

    def desktopAudioToggle(self):
        self.ws.call(requests.ToggleMute("Desktop Audio"))

    def getSceneList(self):
        return (self.ws.call(requests.GetSceneList())).getScenes()

    def switchScene(self, scene):
        self.ws.call(requests.SetCurrentScene(scene))

    def startStreaming(self):
        self.ws.call(requests.StartStreaming())

    def stopStreaming(self):
        self.ws.call(requests.StopStreaming())

    def startRecording(self):
        self.ws.call(requests.StartRecording())

    def stopRecording(self):
        self.ws.call(requests.StopRecording())

    def pauseRecording(self):
        self.ws.call(requests.PauseRecording())

    def resumeRecording(self):
        self.ws.call(requests.ResumeRecording())

    def disconnect(self):
        self.ws.disconnect()
