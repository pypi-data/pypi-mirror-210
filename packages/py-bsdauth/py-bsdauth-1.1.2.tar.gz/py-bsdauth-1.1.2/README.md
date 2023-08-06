# py-bsdauth

- Python interface to OpenBSD's BSD Auth
- Currently only implements auth_userokay(3) passwd authentication style.

### Note
- Your application must be in the 'auth' group to call auth_userokay(3):

```sh
usermod -G auth <yourdaemonuser>
```
 
Usage:
```sh
>>> from bsdauth.bsdauth import UserOkay
>>> u='user1'
>>> pw='goodpassword'
>>> uo=UserOkay(u,pw)
>>> uo.login()
True
>>> pw='badpassword'
>>> uo = UserOkay(u,pw)
>>> uo.login()
False
>>> ur='baduser'
>>> pw='goodpassword'
>>> uo = UserOkay(ur,pw)
>>> uo.login()
False
>>> exit()
```
