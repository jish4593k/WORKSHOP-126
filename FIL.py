import json
import httpx
from pygame import mixer
import os
import torch
import torch.nn as nn
from keras.models import Sequential
from keras.layers import Dense
from torch.autograd import Variable

# PyTorch Simple Neural Network
class SimpleNN(torch.nn.Module):
    def __init__(self, input_size, output_size):
        super(SimpleNN, self).__init__()
        self.linear = torch.nn.Linear(input_size, output_size)

    def forward(self, x):
        return self.linear(x)

# AI Chat class
class DocomoAIChat:
    def __init__(self, api_key):
        self.api_key = api_key
        self.app_id = self.get_app_id()
        self.tmp_filename = "tmp.aac"
        mixer.init()

        # Example PyTorch model
        self.pytorch_model = SimpleNN(input_size=10, output_size=5)
        
        # Example Keras model
        self.keras_model = Sequential()
        self.keras_model.add(Dense(8, input_dim=10, activation='relu'))
        self.keras_model.add(Dense(5, activation='softmax'))

    def get_app_id(self):
        # Obtain App ID for natural chatting
        endpoint = 'https://api.apigw.smt.docomo.ne.jp/naturalChatting/v1/registration'
        payload = {"APIKEY": self.api_key}
        headers = {"Content-type": "application/json;charset=UTF-8"}
        payload_json = {"botId": "Chatting", "appKind": "0"}

        response = httpx.post(endpoint, headers=headers, params=payload, data=json.dumps(payload_json))
        data = response.json()
        return data["appId"]

    def request_dialog_text(self, text):
        # Request dialog text using natural chatting API
        endpoint = 'https://api.apigw.smt.docomo.ne.jp/naturalChatting/v1/dialogue'
        headers = {"Content-type": "application/json;charset=UTF-8"}
        payload = {"APIKEY": self.api_key}
        payload_json = {
            "language": "ja-JP",
            "botId": "Chatting",
            "appId": self.app_id,
            "voiceText": text,
            "appRecvTime": "YYYY-MM-DD hh:mm:ss",
            "appSendTime": "YYYY-MM-DD hh:mm:ss"
        }

        response = httpx.post(endpoint, headers=headers, params=payload, data=json.dumps(payload_json))
        data = response.json()
        return data["systemText"]["expression"]

    def request_voice_data(self, text):
        # Request voice data using text-to-speech API
        endpoint = 'https://api.apigw.smt.docomo.ne.jp/crayon/v1/textToSpeech'
        headers = {"Content-type": "application/json;charset=UTF-8"}
        payload = {"APIKEY": self.api_key}
        payload_json = {
            "Command": "AP_Synth",
            "SpeakerID": "1",
            "StyleID": "1",
            "PowerRate": "5.00",
            "AudioFileFormat": "0",
            "TextData": text
        }

        response = httpx.post(endpoint, headers=headers, params=payload, data=json.dumps(payload_json))
        return response

    def play_audio(self):
        # Play audio using pygame mixer
        mixer.music.load(self.tmp_filename)
        mixer.music.play()
        while mixer.music.get_busy():
            pass

    def run(self):
        # Example PyTorch input and output
        pytorch_input = Variable(torch.randn(1, 10))
        pytorch_output = self.pytorch_model(pytorch_input)

        # Example Keras input and output
        keras_input = Variable(torch.randn(1, 10)).numpy()
        keras_output = self.keras_model.predict(keras_input)

        print("PyTorch Output:", pytorch_output)
        print("Keras Output:", keras_output)

        while True:
            user_input = input(">>")
            response_text = self.request_dialog_text(user_input)
            voice_response = self.request_voice_data(response_text)

            if voice_response.status_code == 200:
                with open(self.tmp_filename, 'wb') as fd:
                    fd.write(voice_response.content)

                print("AIちゃん: {0}".format(response_text))
                self.play_audio()
                os.remove(self.tmp_filename)

if __name__ == '__main__':
    # Replace 'YOUR API KEY' with your actual API key
    api_key = 'YOUR API KEY'
    ai_chat = DocomoAIChat(api_key)
    ai_chat.run()
