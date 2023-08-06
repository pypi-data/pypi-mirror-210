import requests

def go(content,type=0):
    url = 'https://www.heyus.cn/api/translate'
    headers = {
        'Content-Type': 'application/json',
    }

    # content = '请问为什么1+1=2？'
    # data = {'type':'999','message':content}
    data = {'type':type,'message':content}

    response = requests.post(url, headers=headers, json=data)
    return response.text.replace('\\n','\n')