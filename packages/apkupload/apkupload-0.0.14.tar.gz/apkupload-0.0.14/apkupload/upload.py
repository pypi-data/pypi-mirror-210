import configargparse
import argparse
import base64
import hashlib
import hmac
import json
import os
import requests
import time
import urllib.parse
from datetime import datetime
from androguard.core.bytecodes.apk import APK
# 解析输入的参数

content_template = """

* 应用名称：{name}
* 应用包名：{package}
* 更新说明：
{changelog}
{apk_info}
* 历史版本：[戳这里]({url})
![图片]({image})
"""

apk_info_template = """
* MD5：{md5}
* 版本名称：[{version_name}]({download_url})
* 版本号：{version_code}
* 包大小：{size}
----------------------------
"""


def parse():
    p = configargparse.ArgParser(
        config_file_parser_class=configargparse.YAMLConfigFileParser)
    p.add('--config', required=True, is_config_file=True)
    p.add('--version_code', required=False)
    p.add('--version_code_suffix', required=False)
    p.add('--version_name', required=False, nargs="+")
    p.add('--delete', required=True,type=bool)
    p.add('--send', required=True,type=bool)
    p.add('--files', required=False,nargs="+")
    p.add('--name', required=False)
    p.add('--base', required=True)
    p.add('--input', required=False)
    p.add('--output', required=False)
    p.add('--key', required=False)
    p.add('--password', required=False)
    p.add('--url', required=True)
    p.add('--upload_url', required=True)
    p.add('--secret', required=True)
    p.add('--token', required=True)
    p.add('--user', required=True)
    p.add('--repository', required=True)
    p.add('--github', required=True)
    p.add('--workflow', required=True, )
    p.add('--changelog', required=True, nargs="+")
    p.add('--at', required=True, nargs="+")
    p.add('--image', required=True)
    p.add('--retry_count', required=True)
    return p.parse_args()


def generate_apk_name(output, name, version_name):
    now = datetime.strftime(datetime.now(), "%m_%d_%H%M")
    return f"{output}/{name}_{version_name}_{now}.apk"


def build_json(name, version_name, version_code, md5, size, changelog, base, path, download_url,package):
    return {
        "name": name,
        "version_name": version_name,
        "version_code": version_code,
        "url": download_url,
        "date": datetime.now().strftime("%Y-%m-%d %H时%M分%S秒"),
        "changelog": changelog,
        "md5": md5,
        "size": size,
        "file": path,
        "base": base,
        "package":package
    }


def build_web(user, repository, workflow, headers, content):
    print(">>>> build web <<<<")
    body = {"ref": "main", "inputs": {"content": json.dumps(content)}}
    r = requests.post(
        f"https://api.github.com/repos/{user}/{repository}/actions/workflows/{workflow}/dispatches",
        headers=headers,
        json=body
    )
    print(r.status_code)


def change_version(input, version_code, version_name):
    """修改版本号"""
    result = ""
    print(">>>> change version <<<<")
    with open(input + "/apktool.yml", 'r') as f:
        lines = f.readlines()
        for line in lines[:-2]:
            result += line
        result += "  versionCode: '{version_code}'\n".format(
            version_code=version_code)
        result += "  versionName: " + version_name
    with open(input + "/apktool.yml", "w") as f:
        f.write(result)


def build_apk(output, input, key, password):
    """打包"""
    unalign = output + "/unalign.apk"
    unsign = output + "/unsign.apk"
    sign = output + "/sign.apk"
    print(">>>> building apk <<<<")
    os.system(
        'apktool b -o {unalign} {decode}'.format(unalign=unalign, decode=input))
    print(">>>> aligning apk <<<<")
    os.system(
        'zipalign -f 4 {unalign} {unsign}'.format(unalign=unalign, unsign=unsign))
    print(">>>> signing apk <<<<")
    os.system('apksigner sign --ks {key} --ks-pass pass:{password} --out {sign} {unsign}'.format(
        key=key, password=password, sign=sign, unsign=unsign))
    return sign


def send_to_dingding(name, url, changelog, apk_info, secret, token, at, image,package):
    print(">>>> send to dingding <<<<")
    content = content_template.format(
        name=name,package=package, changelog=changelog, apk_info=apk_info, url=url, image=image)
    atMobiles = []
    for i in at:
        atMobiles.append(i)
    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc,
                         digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    url2 = f'https://oapi.dingtalk.com/robot/send?access_token={token}&timestamp=' + \
        timestamp + '&sign=' + sign
    h = {'Content-Type': 'application/json; charset=utf-8'}
    body = {"at": {"isAtAll": True},
            "msgtype": "markdown", "markdown": {"text": content, "title": "更新日志"}
            }
    r = requests.post(url2, headers=h, data=json.dumps(body))
    


def upload(upload_url,file, count, retry_count,delete):
    print(">>>> uploading <<<<")
    count += 1
    files = {'file': open(file, 'rb')}
    response = requests.post(upload_url, files=files)
    url = ""
    print(response.status_code)
    if (response.status_code == 200 or response.status_code == 201):
        url = response.json()["data"]
        print(f">>>>上传成功<<<< url = {url}")
        if delete:
            os.remove(file)
    else:
        print(
            f">>>>上传失败 code = {response.status_code} message = {response.json()} count = {count}<<<")
        if (count < retry_count):
            url = upload(upload_url,file, count, retry_count,delete)
    return url


def main():
    args = parse()
    version_code_suffix = args.version_code_suffix
    version_name_list = args.version_name
    version_code = args.version_code
    base = args.base
    send = args.send
    name = args.name
    files = args.files
    delete = args.delete
    input = args.input
    output = args.output
    key = args.key
    password = args.password
    secret = args.secret
    url = args.url
    upload_url = args.upload_url
    token = args.token
    changelog = args.changelog
    changelog = [f"> - {item}" for item in changelog]
    changelog = "\n".join(changelog)
    github = args.github
    workflow = args.workflow
    at = args.at
    user = args.user
    repository = args.repository
    image = args.image
    headers = {"Accept": "application/vnd.github.v3+json",
               "Authorization": f"token {github}"}
    retry_count = int(args.retry_count)
    apk_info = ""
    content = []
    os.system('rm -rf ' + input + "/build")
    if files == None:
        for version_name in version_name_list: 
            new_version_code = version_code       
            if (version_code_suffix=="True"):
                suffix = version_name.split("_")[0].split(".")[-1]
                new_version_code = f"{version_code}{suffix}"
            print(f"version_code = {new_version_code} version_name = {version_name}")
            change_version(input, new_version_code, version_name)
            sign = build_apk(output, input, key, password)
            md5 = hashlib.md5(open(sign, 'rb').read()).hexdigest()
            size = str(os.path.getsize(sign))+"字节"
            apk = APK(sign)
            if(name==None):
                name = apk.get_app_name()
            package = apk.get_package()
            _version_name = apk.get_androidversion_name()
            _version_code = apk.get_androidversion_code()
            apk = generate_apk_name(output, name, _version_name)
            os.makedirs(os.path.dirname(apk), exist_ok=True)
            os.rename(sign, apk)
            download_url = upload(upload_url,apk, 0, retry_count,delete)
            path = datetime.now().strftime("%Y%m%d%H%M")
            content.append(build_json(name,  _version_name,
                        _version_code, md5, size,  changelog, base, path, download_url,package))
            apk_info += apk_info_template.format(name=name, download_url=download_url,
                                                md5=md5, version_name=_version_name, version_code=_version_code, size=size)
    else:
        for file in files:
            if not os.path.exists(file):
                print(f"文件不存在 {file}")
                continue
            apk = APK(file)
            if(name==None):
                name = apk.get_app_name()
            package = apk.get_package()
            _version_name = apk.get_androidversion_name()
            _version_code = apk.get_androidversion_code()
            md5 = hashlib.md5(open(file, 'rb').read()).hexdigest()
            size = str(os.path.getsize(file))+"字节"
            download_url = upload(upload_url,file, 0, retry_count,delete)
            path = datetime.now().strftime("%Y%m%d%H%M")
            content.append(build_json(name,  _version_name,
                        _version_code, md5, size,  changelog, base, path, download_url,package))
            apk_info += apk_info_template.format(name=name, download_url=download_url,
                                                md5=md5, version_name=_version_name, version_code=_version_code, size=size)
    build_web(user, repository, workflow, headers, content)
    if send:
        send_to_dingding(name, url, changelog, apk_info,
                         secret, token, at, image,package)


if __name__ == "__main__":
    main()
