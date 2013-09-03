clipm
=====

简易密码管理 工具
-----------------

使用python2.7 编写的一个简易的密码管理工具 基于命令行

依赖`python-gnupg` debian用户可以直接源内安装

使用方法
--------
<br \>
### 初始化
第一次使用需要初始化数据库 及 建立key


``python clipm.py init xx@gmail.com eleveni386``

xx@gmail.com `密钥标识`
<br \>
ZWxldmVuaTM4Ng==   `密钥key`

后面很多操作都需要使用到, 所以请保存好.

### 插入一条记录

有了一个数据库我们就可以插入一条记录了比如

``python clipm.py insert title=数据库服务器 username=root password='!@#SDKJF' remark=这是一个测试记录' email=xx@gmail.com``

使用`insert`方法, 仅有`email`参数是必须的, 其余的参数都可以为空, `email`参数用于加密 密码

### 查看记录

有了记录之后,我们可以用list方法来查看

``python clipm.py list``

### 修改记录

当然也可以进行记录修改

``python clipm.py update password=newpassword title=数据库服务器 email=xx@gmail.com``

使用`update`方法的时候 有一点需要注意, 当进行密码修改的时候,一定不要忘记`email`参数了, 它是用来加密的呢.
当然如果不是修改密码, 那么email君可以消失了..

### 查看密码

现在可以来正式使用这个工具,为我服务了.

``python clipm.py 数据库服务器 ZWxldmVuaTM4Ng==``

!@#SDKJF

<<<<<<< HEAD
### 查看现有密钥

    python clipm.py listkey

    /home/eleven/.mypwd/pubring.gpg
    -------------------------------
    pub     BE478AEF1E089F7B        2013-08-18
    uid                     <eleven.i386@gmail.com>
    sec     BE478AEF1E089F7B        2013-08-18


### 导入现有密钥

`python clipm.py importkey your keyfile path`

### 更新记录

2013-09-03

增加密钥列表 listkey

增加现有密钥导入功能 importkey

### 释疑
这里我用明文key的方式来解密数据库内的密码, 本来这是一种很不安全的方法, 但是我为了结合tmux方法,就没有采用交互式key输出
如有需求的,可以改写Search函数, 采用base64或者其他加密方法加密key, 或者直接使用交互式, 看君所需了.

=======
最后考虑了下, 还是给key加一个简单的加密吧, 就用base64 意思意思下就可以了, 起码让人第一眼看不出真实key是多少<br />
>>>>>>> 94f9d21c02b645452434af45ea902e6302bb8ce6
欢迎各路女汉纸,男同志来我的blog看哦, http://eleveni386.7axu.com

