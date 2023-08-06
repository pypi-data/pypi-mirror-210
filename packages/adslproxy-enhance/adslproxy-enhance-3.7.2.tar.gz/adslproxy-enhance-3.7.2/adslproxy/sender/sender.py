import re
import time
import requests
from requests.exceptions import ConnectionError, ReadTimeout
from adslproxy.settings import *
import platform
from loguru import logger
from retrying import retry, RetryError
import hashlib
from urllib.parse import urlencode

if platform.python_version().startswith('2.'):
    import commands as subprocess
elif platform.python_version().startswith('3.'):
    import subprocess
else:
    raise ValueError('python version must be 2 or 3')


def generate_url_signature(payload, key):
    payload['timestamp'] = int(time.time())
    qs = ''
    for i in sorted(payload.items()):
        qs += f'{i[0]}{i[1]}'
    qs += key
    print(qs)
    payload['signature'] = hashlib.md5(qs.encode('utf-8')).hexdigest()
    return urlencode(payload)


class Sender(object):
    """
    拨号并发送到 Redis
    """

    def extract_ip(self):
        """
        获取本机IP
        :param ifname: 网卡名称
        :return:
        """
        (status, output) = subprocess.getstatusoutput('ifconfig')
        if not status == 0: return
        pattern = re.compile(DIAL_IFNAME + '.*?inet.*?(\d+\.\d+\.\d+\.\d+).*?netmask', re.S)
        result = re.search(pattern, output)
        if result:
            # 返回拨号后的 IP 地址
            return result.group(1)

    def test_proxy(self, proxy):
        """
        测试代理，返回测试结果
        :param proxy: 代理
        :return: 测试结果
        """
        try:
            response = requests.get(TEST_URL, proxies={
                'http': 'http://' + proxy,
                'https': 'http://' + proxy
            }, timeout=TEST_TIMEOUT)
            if response.status_code == 200:
                return True
        except (ConnectionError, ReadTimeout):
            return False

    @retry(retry_on_result=lambda x: x is not True, stop_max_attempt_number=10)
    def remove_proxy(self):
        """
        移除代理
        :return: None
        """
        logger.info(f'Removing {CLIENT_NAME}...')
        try:
            payload = {
                'client_name': CLIENT_NAME
            }

            qs = generate_url_signature(payload, API_SIGNATURE_KEY)

            url = f"{API_URL}/remove?{qs}"
            res = requests.get(url)
            if res.ok:
                logger.info(f'Result is {res.text} Removed {CLIENT_NAME} successfully')
                logger.info(f'Removed {CLIENT_NAME} successfully')
                return True
            else:
                logger.info(f'Result is {res.text} Removed {CLIENT_NAME} failed')
                return False
        except Exception as e:
            logger.info(f'Remove {CLIENT_NAME} failed')

    def set_proxy(self, proxy):
        """
        设置代理
        :param proxy: 代理
        :return: None
        """
        payload = {
            'client_name': CLIENT_NAME,
            'client_ip': proxy
        }

        qs = generate_url_signature(payload, API_SIGNATURE_KEY)
        url = f"{API_URL}/update?{qs}"
        res = requests.get(url)
        if res.ok:
            logger.info(f'Result is {res.text} Set {CLIENT_NAME} successfully')
            return True
        else:
            logger.info(f'Result is {res.text} Removed {CLIENT_NAME} failed')
            return False

    def loop(self):
        """
        循环拨号
        :return:
        """
        while True:
            logger.info('Starting dial...')
            self.run()
            time.sleep(DIAL_CYCLE)

    def run(self):
        """
        拨号主进程
        :return: None
        """
        logger.info('Dial started, remove proxy')
        try:
            self.remove_proxy()
        except RetryError:
            logger.error('Retried for max times, continue')
        # 拨号
        (status, output) = subprocess.getstatusoutput(DIAL_BASH)
        if not status == 0:
            logger.error('Dial failed')
        # 获取拨号 IP
        ip = self.extract_ip()
        if ip:
            logger.info(f'Get new IP {ip}')
            if PROXY_USERNAME and PROXY_PASSWORD:
                proxy = '{username}:{password}@{ip}:{port}'.format(username=PROXY_USERNAME,
                                                                   password=PROXY_PASSWORD,
                                                                   ip=ip, port=PROXY_PORT)
            else:
                proxy = '{ip}:{port}'.format(ip=ip, port=PROXY_PORT)
            time.sleep(10)
            if self.test_proxy(proxy):
                logger.info(f'Valid proxy {proxy}')
                # 将代理放入数据库
                self.set_proxy(proxy)
                time.sleep(DIAL_CYCLE)
            else:
                logger.error(f'Proxy invalid {proxy}')
        else:
            # 获取 IP 失败，重新拨号
            logger.error('Get IP failed, re-dialing')
            self.run()


def send(loop=True):
    sender = Sender()
    sender.loop() if loop else sender.run()


if __name__ == '__main__':
    send()
