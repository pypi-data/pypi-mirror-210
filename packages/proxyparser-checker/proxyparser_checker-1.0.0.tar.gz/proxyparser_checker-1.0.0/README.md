# ProxyParser

**ProxyParser** is a library for checking/parsing proxies.

```python
>>> from ProxyParser import ProxyParser
>>> 
>>> working_proxies = []
>>> proxies = ProxyParser.parseProxy()
>>> 
>>> for proxy in proxies:
>>>    if ProxyParser.checkProxy(proxy):
>>>       working_proxies.append(proxy)
>>> print("Working proxies:")
>>> print(working_proxies)
Working proxies:
['101.132.25.152:5678', '120.196.188.21:9091']
```

## Installing ProxyParser

ProxyParser is available on PyPi:
```console
$ python -m pip install Proxy-Parser
```

[**GitHub**](https://github.com/TurboKoT1/ProxyParser)