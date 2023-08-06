"""
open ai 의 rest api를 사용하는 python sample 입니다.

25회 전후에서 choice 오류가 발생하면 reset을 해서 다시 대화 해야 합니다.
reset 방법은 채팅 본분에 reset 이라고 보내면 파일로 저장하고 대화가 초기화 됩니다.
    api_key : 개인별로 발급받아야 합니다.
    messages : 사용자의 질문과 AI의 응답이 계속 누적되어 기록되어 있습니다.
               아래와 같은 데이터로 저장되어 있습니다.
             [
              {"role": "user","content": "질문1"},
              {"role": "assistant", "content" : "응답1"},
              {"role": "user","content": "질문2"},
             ]
    i: 화면에 라인넘버를 표시합니다. 0부터 시작합니다.
by hw,jung, 2023/05/14, 맘대로 수정 삭제해서 사용할 수 있습니다.
"""

import requests
from datetime import datetime

url = "https://chatgpt-api.shn.hk/v1" # proxy 사이트
     #"https://api.openai.com/v1/chat/completions" # 공식 사이트
api_key = "6TbQXMy1pezgM4LaFbBT3BlbkFJ5cMaadE7RpYRypc37SBf" # API Key
messages = []
i = 0

def savechat(messages):
    """
    파일로 저장하는 함수로 다음과 같다.
    
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    filename = f"messages_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        for i, message in enumerate(messages):
            linemessage = message['content']
            linemessage.replace('\\n', '\n')
            f.write(f"{i}: {linemessage}\n")
    """
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    filename = f"messages_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        for i, message in enumerate(messages):
            linemessage = message['content']
            linemessage.replace('\\n', '\n')
            f.write(f"{i}: {linemessage}\n")

def playchat(amessage, pref=''):
    """
    채팅하는 함수로 다음과 같다.
    
    global api_key, messages, i
    api_key = pref + api_key
    
    if amessage == 'reset':
        savechat(messages)
        messages = []
        i = 0
        return '이전 대화를 파일로 저장하고, 다시 대화를 시작합니다..'
    
    messages.append({"role": "user","content": amessage})

    response = requests.post(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": "gpt-3.5-turbo", 
                  "messages": messages,
                 },
            )
    output = response.json()["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content" : output})
    i += 2
    return  print('[', i-2, ']', amessage, '\n[', i-1, ']', output)
    """
    global api_key, messages, i
    api_key = pref + api_key
    
    if amessage == 'reset':
        savechat(messages)
        messages = []
        i = 0
        return '이전 대화를 파일로 저장하고, 다시 대화를 시작합니다..'
    
    messages.append({"role": "user","content": amessage})

    response = requests.post(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": "gpt-3.5-turbo", 
                  "messages": messages,
                 },
            )
    output = response.json()["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content" : output})
    i += 2
    return  print('[', i-2, ']', amessage, '\n[', i-1, ']', output)
    