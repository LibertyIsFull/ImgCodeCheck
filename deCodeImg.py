#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ImgCodeCheck 图片验证码识别API

功能：
- 支持本地图片验证码识别
- 支持网络图片验证码识别
- 支持Base64编码图片验证码识别
- 提供Web API服务

依赖：
- ddddocr==1.5.6
- Pillow>=10.0.0
"""

# 导入必要的库
from wsgiref.simple_server import make_server  # 用于创建WSGI服务器
from urllib import parse, request             # 用于URL解析和网络请求
import ddddocr                                 # 验证码识别库
import sys, getopt, re, base64                 # 系统工具库



def getImgBytes(imgParam):
    """
    获取图片字节数据
    
    参数:
        imgParam: str - 图片参数，可以是URL、本地文件路径或Base64编码的图片数据
    
    返回:
        bytes - 图片的字节数据
    """
    # 如果参数是URL
    if re.match(r'^http', imgParam) is not None:
        resp = request.urlopen(imgParam)        # 发送网络请求
        img_bytes = bytearray(resp.read())       # 读取响应数据
    # 如果参数是本地图片文件路径
    elif re.search(r'(\.jpg|\.jpeg|\.png|\.gif)$', imgParam) is not None:
        with open(imgParam, 'rb') as f:
            img_bytes = f.read()                 # 读取本地文件
    # 如果参数是Base64编码的图片数据
    else:
        # 移除Base64前缀（如果存在）
        imgParam = re.sub(r'^data:image/\w+;base64,', '', imgParam)
        img_bytes = base64.b64decode(imgParam)   # Base64解码
    return img_bytes

def deCodeImg(imgBytes):
    """
    识别图片中的验证码
    
    参数:
        imgBytes: bytes - 图片的字节数据
    
    返回:
        str - 识别到的验证码字符串
    
    异常:
        Exception - 当识别过程中出现错误时抛出
    """
    try:
        ocr = ddddocr.DdddOcr()               # 创建OCR实例
        res = ocr.classification(imgBytes)     # 调用分类方法识别验证码
        return res                             # 返回识别结果
    except Exception as e:
        print(f"OCR decoding error: {str(e)}")  # 打印错误信息
        raise                                  # 重新抛出异常

def app(environ, start_response):
    """
    WSGI应用程序，处理HTTP请求
    
    参数:
        environ: dict - WSGI环境变量
        start_response: callable - 用于设置响应状态和头信息
    
    返回:
        list - 响应体的字节数据列表
    """
    # 设置响应状态和头信息
    start_response('200 OK', [
        ('Content-Type', 'text/html'),              # 设置内容类型为HTML
        ('Access-Control-Allow-Origin', '*')        # 允许跨域请求
    ])
    
    # 只处理根路径的请求
    if environ["PATH_INFO"] == "/":
        params = parse.parse_qs(environ["QUERY_STRING"])  # 解析查询参数
        
        # 如果没有提供img参数，返回帮助信息
        if "img" not in params:
            return [b'--- DeCodeImg Server Started ---<br>Powered by hoothin<br>Usage: http://<hostname>:<port>/?img=<image_data><br>image_data can be local path, URL or base64 encoded data']
        
        # 获取action参数，默认为getCode
        action = "getCode"
        if "action" in params.keys():
            action = params["action"][0]
        
        # 处理getCode动作
        if action == "getCode":
            try:
                # 识别验证码
                result = deCodeImg(getImgBytes(params["img"][0]))
                return [str.encode(result)]           # 返回识别结果
            except:
                return [b'Image data is incorrect!']  # 图片数据错误
    
    # 其他路径返回1
    return [b'1']


def main(argv):
    """
    程序入口函数，处理命令行参数
    
    参数:
        argv: list - 命令行参数列表（不包含程序名称）
    """
    # 默认配置
    port = 416           # 默认服务端口
    makeServer = False   # 默认不启动服务
    imgParam = ""        # 默认没有图片参数
    
    try:
        # 解析命令行参数
        opts, args = getopt.getopt(argv, "hi:mp:", ["ifile=", "makeServer", "port="])
    except getopt.GetoptError:
        # 参数解析错误，显示帮助信息
        print('Usage:')
        print('  Local recognition: deCodeImg.py -i <imgParam>')
        print('  Start server: deCodeImg.py -m -p <port>')
        sys.exit(2)
    
    # 处理解析后的参数
    for opt, arg in opts:
        if opt == '-h':
            # 显示帮助信息
            print('Usage:')
            print('  Local recognition: deCodeImg.py -i <imgParam>')
            print('  Start server: deCodeImg.py -m -p <port>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            # 本地识别模式
            imgParam = arg
            result = deCodeImg(getImgBytes(imgParam))  # 识别图片
            print(result)                                # 输出结果
            sys.exit()
        elif opt in ("-m", "--makeServer"):
            # 启动服务模式
            makeServer = True
        elif opt in ("-p", "--port"):
            # 设置服务端口
            port = int(arg)
    
    # 根据模式执行相应操作
    if makeServer:
        # 启动Web服务
        print(f'--- DeCodeImg Server Started ---')
        print(f'Powered by hoothin')
        print(f'Available endpoints:')
        print(f'  http://127.0.0.1:{port}/?img=<local_path>')
        print(f'  http://127.0.0.1:{port}/?img=<url>')
        print(f'  http://127.0.0.1:{port}/?img=<base64_data>')
        
        # 创建并启动WSGI服务器
        httpd = make_server('', port, app)
        httpd.serve_forever()  # 持续运行服务
    elif imgParam == "":
        # 没有提供任何参数，显示帮助信息
        print('--- DeCodeImg ---')
        print('Use -h to view help')


# 程序入口点
if __name__ == "__main__":
    main(sys.argv[1:])  # 传入命令行参数