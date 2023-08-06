
"""
    Coder: @zcxw_sudo
"""

import requests
import sys
import json
import io


class Client:
    """
            API DOCUMENTATION: https://github.com/zcxw-code/GosuScreenAPI
    """

    def __init__(self, main_url: str, token: str):

        self.token = token
        self.main_url = main_url
        self.headers = {
            'user-agent': "GosuScreenAPI (Library)",
            'content-type': 'application/json'
        }

    def return_image(self, bytes_image: bytes, name: str):
        image = io.BytesIO(bytes_image)
        image.seek(0)
        image.name = name
        return image

    def get_qrcodepro(self, service: int, config: dict):
        """
        Параметр	Тип	Описание
        token	строка	Обязательный. Ваш ключ API
        service	число	Обязательный. ID сервиса, который будет генерироваться.
        config	dict	Обязательный. Параметры для qrcode

        Возвращает тип: io.BytesIO(image)

        При ошибке: application/json
        """
        try:
            data = {
                'token': self.token,
                'service': str(service),
                'config': config
            }
            response = requests.post(
                self.main_url + '/qrcodepro', data=json.dumps(data), headers=self.headers)
            if response.headers.get('Content-Type') == 'application/json':
                return response.json()
            else:
                return self.return_image(response.content, 'qrcode.png')
        except:
            return {'status': 'error', 'message': str(sys.exc_info()[1])}


    def get_qrcode(self, service: int, value: str):
        """
        Параметр	Тип	Описание
        token	строка	Обязательный. Ваш ключ API
        service	число	Обязательный. ID сервиса, который будет генерироваться.
        value	строка	Обязательный. Текст для кодирования. Любой текст

        Возвращает тип: io.BytesIO(image)

        При ошибке: application/json
        """
        try:
            data = {
                'token': self.token,
                'service': str(service),
                'value': value
            }
            response = requests.post(
                self.main_url + '/qrcode', data=json.dumps(data), headers=self.headers)
            if response.headers.get('Content-Type') == 'application/json':
                return response.json()
            else:
                return self.return_image(response.content, 'qrcode.png')
        except:
            return {'status': 'error', 'message': str(sys.exc_info()[1])}

    def get_screenshot(self, service: int, platform: str, config: dict):
        """
            Параметр	Тип	Описание
            token	строка	Обязательный. Ваш ключ API
            service	число	Обязательный. ID сервиса, который будет генерироваться.
            platform	строка	Обязательный. Нужная платформа телефона.
            config	json	Обязательный. Требуемые параметры для сервиса.


            Возвращает тип: io.BytesIO(image)

            При ошибке: application/json
        """
        try:
            data = {
                'token': self.token,
                'service': str(service),
                'platform': platform,
                'config': config
            }
            response = requests.post(
                self.main_url + '/screen', data=json.dumps(data), headers=self.headers)
            if response.headers.get('Content-Type') == 'application/json':
                return response.json()
            else:
                return self.return_image(response.content, 'screen.jpg')
        except:
            return {'status': 'error', 'message': str(sys.exc_info()[1])}
