# Allbaro

**Allbaro** 한국환경공단 올바로 시스템 스크래핑을 위한 파이썬 라이브러리

```python
>>> import datetime
>>> from allbaro import Allbaro
>>>
>>> allbaro = Allbaro()
>>>
>>> # 올바로 시스템 로그인
>>> allbaro.authenticate('올바로 시스템 아이디', '올바로 시스템 패스워드')
>>> # 인계서진행상황확인 - 인계서진행상황 정보 조회
>>> start_date = datetime.date(2023, 5, 1)
>>> end_date = datetime.date(2023, 5, 31)
>>>
>>> result_list = allbaro.handover_process_list(start_date, end_date)
```

<!--
[![Downloads](https://pepy.tech/badge/allbaro/month)](https://pepy.tech/project/allbaro)
[![Supported Versions](https://img.shields.io/pypi/pyversions/allbaro.svg)](https://pypi.org/project/allbaro)
[![Contributors](https://img.shields.io/github/contributors/psf/allbaro.svg)](https://github.com/psf/requests/graphs/contributors)


## Installing Requests and Supported Versions

Requests is available on PyPI:

```console
$ python -m pip install requests
```

Requests officially supports Python 3.7+.

## Supported Features & Best–Practices

Requests is ready for the demands of building robust and reliable HTTP–speaking applications, for the needs of today.

- Keep-Alive & Connection Pooling
- International Domains and URLs
- Sessions with Cookie Persistence
- Browser-style TLS/SSL Verification
- Basic & Digest Authentication
- Familiar `dict`–like Cookies
- Automatic Content Decompression and Decoding
- Multi-part File Uploads
- SOCKS Proxy Support
- Connection Timeouts
- Streaming Downloads
- Automatic honoring of `.netrc`
- Chunked HTTP Requests

## API Reference and User Guide available on [Read the Docs](https://requests.readthedocs.io)

[![Read the Docs](https://raw.githubusercontent.com/psf/requests/main/ext/ss.png)](https://requests.readthedocs.io)

## Cloning the repository

When cloning the Requests repository, you may need to add the `-c
fetch.fsck.badTimezone=ignore` flag to avoid an error about a bad commit (see
[this issue](https://github.com/psf/requests/issues/2690) for more background):

```shell
git clone -c fetch.fsck.badTimezone=ignore https://github.com/psf/requests.git
```

You can also apply this setting to your global Git config:

```shell
git config --global fetch.fsck.badTimezone ignore
```

---

[![Kenneth Reitz](https://raw.githubusercontent.com/psf/requests/main/ext/kr.png)](https://kennethreitz.org) [![Python Software Foundation](https://raw.githubusercontent.com/psf/requests/main/ext/psf.png)](https://www.python.org/psf)
-->