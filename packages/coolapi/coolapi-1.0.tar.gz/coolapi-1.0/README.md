# 项目描述

简单好用的异步 web 框架。

# 安装

```
pip install coolapi
```

# Bug提交、功能提议

您可以通过 [Github-Issues](https://github.com/lcctoor/lccpy/issues)、[微信](https://raw.githubusercontent.com/lcctoor/me/main/author/WeChatQR-max.jpg)、[技术交流群](https://raw.githubusercontent.com/lcctoor/me/main/lccpy/WechatReadersGroupQR-original.jpg) 与我联系。

# 关于作者

作者：许灿标

邮箱：lcctoor@outlook.com

[主页](https://github.com/lcctoor/me#readme) | [微信](https://raw.githubusercontent.com/lcctoor/me/main/author/WeChatQR-max.jpg) | [微信公众号](https://raw.githubusercontent.com/lcctoor/me/main/lccpy/WechatSubscribeQR-max.jpg) | [Python技术微信交流群](https://raw.githubusercontent.com/lcctoor/me/main/lccpy/WechatReadersGroupQR-original.jpg)

开源项目：[让 Python 更简单一点](https://github.com/lcctoor/lccpy#readme)

# 教程

##### 导入

```python
import asyncio
from coolapi import handler, creat_server
```

##### 一个最简单的例子

```python
class LoginHandler(handler):
    urls = ['/login/?']
    # url必须以'/'开头
    # '?'是正则表达式语法, 相当于 urls = ['/login', '/login/']

    async def get(self):
        return self.write('You are accessing the get method of login')
  
    async def post(self):
        return self.write('You are accessing the post method of login')

async def main():
    handlers = [LoginHandler]
    http_server = creat_server(handlers=handlers, port=5050)  # 启动http异步任务
    await asyncio.sleep(float('inf'))  # float('inf')表示无穷大

asyncio.run(main())

# 此时可在浏览器访问：
# http://localhost:5050/login
# http://localhost:5050/login/
```

##### 设置 cookie

```python
class PersonalHandler(handler):
    urls = ['/personal/?']

    async def get(self):
        self.set_cookie(name='username', value='tony')
        return self.write('Welcome to the personal center!')
```

##### 重定向

```python
def judge_login(self):
    ...

class PersonalHandler(handler):
    urls = ['/personal/?']

    async def get(self):
        if judge_login(self):
            return self.write('Welcome to the personal center!')
        else:
            return self.redirect('/login')  # 重定向到login
```

##### 常用的视图操作

| 功能         | 代码                                           |
| ------------ | ---------------------------------------------- |
| 返回响应     | return self.write('......')                    |
| 设置cookie   | self.set_cookie(name='username', value='tony') |
| 获取cookie   | self.get_cookie(name='username')               |
| 重定向       | return self.redirect('/login')                 |
| 获取访客ip   | ip = self.get_ip( )                            |
| 获取请求数据 | body = self.get_body( )                        |

##### 使用通配路由

```python
class ArticleHandler(handler):
    urls = ['/article/(\d+)/([a-z0-9]+)/?']

    async def get(self, userid, article_id):
        text = f"The article you are reading is '{article_id}' written by {userid}"
        return self.write(text)

# 运行后可在浏览器访问：
# http://localhost:5050/article/641872/r9mf44
# http://localhost:5050/article/740357/8d1h6d
# ...
```

```python
class DocumentionHandler(handler):
    urls = ['/documention/python([\d.]+)/?']

    async def get(self, version):
        text = f"You are reading the documentation for Python{version}"
        return self.write(text)

# 运行后可在浏览器访问：
# http://localhost:5050/documention/python3
# http://localhost:5050/documention/python3.9
# ...
```

##### 启动 http 服务

```python
class LoginHandler(handler):
    urls = ['/login/?']
    async def get(self):
        return self.write('You are accessing the get method of login')

class ArticleHandler(handler):
    ...

async def main():
    http_server = creat_server(
      
        handlers = [LoginHandler, ArticleHandler],  # 要注册的视图类
      
        port = 5050,  # 端口, 默认为80
      
        static_path = None,  # 静态文件服务, 默认为None
      
        debug = False,  # 启用调试模式, 默认为False
      
        # 支持更多参数, 可参考 https://www.tornadoweb.org/en/stable/web.html#tornado.web.Application
    )
  
    await asyncio.sleep(float('inf'))  # float('inf')表示无穷大

asyncio.run(main())
```

##### 更多用法

coolapi 是对 tornado 的二次封装，其中：

1、coolapi.handler（视图类）继承自 [tornado.web.RequestHandler](https://www.tornadoweb.org/en/stable/web.html#request-handlers)，可使用 tornado.web.RequestHandler 的任何功能。

2、creat_server 支持 [tornado.web.Application](https://www.tornadoweb.org/en/stable/web.html#tornado.web.Application) 的所有参数。

# 支持作者1元

coolapi 是一个免费的开源项目，由个人维护。

每个小的贡献，都是构成车轮的一份子，可以帮助保持车轮完美旋转。

![donationQR.jpg](https://raw.githubusercontent.com/lcctoor/me/main/donation/donationQR-1rmb-200x200.jpg)
