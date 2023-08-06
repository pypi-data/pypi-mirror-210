
def debug_text():
    print('this is modules/requests_ __init__.py')

def debug_import():
    try:
        import requests
        return True
    except Exception as e:
        print(e)
        return False

# TODO : requests 모듈에 관련해서 추가할만한 함수 생각해보기

def request(url):
    """ url을 받아서 json 형태로 반환하는 함수 """
    import requests

    response = requests.get(url)

    return response.json()