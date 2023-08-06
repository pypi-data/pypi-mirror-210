from setuptools import setup
setup(name='mahdix',
version='0.1.1.3',
description='this is a simple pip modul and test',
long_description='''
#pip install mahdix
# ne python model 
#----[USE]-------
# GET id is create date fb = mahdix.getyearid(cid);# cid = '100000000023456'
# print Sumthiong = mahdix.p('YOUR TXT')
# GET NOW TIME = mahdix.time()
# os.system = mahdix.sysT('YOUR COMmAND')
# GET 7 diges random number = mahdix.random7()
# GET 8 diges random number = mahdix.random8()
# GET 9 diges random number = mahdix.random9()
# GET 1 to2 diges random number = mahdix.random1_2()
# GET 1 to3 diges random number = mahdix.random1_3()
# GET 1 to4 diges random number = mahdix.random1_4()
# GET 10 diges random number = mahdix.random10()
# ----[GENERATE TXT LOGO] ------
from mahdix import makelogo
logo = makelogo(text='Mahdi')
print(logo)
# -----[some functing]-------
# request.get = mahdix.rqg   <Call this modul "mahdix.rqg">
# request.post = mahdix.rqp  <Call this modul "mahdix.rqp">
# random.randint = rr <Call this modul "mahdix.rc">
# random.choice = rc   <Call this modul "mahdix.rc">
# base64.decode = bsdc <Call this modul "mahdix.bsdc">
# base64.encode = bsec <Call this modul "mahdix.bsec">
#---[coloure]------
# RED = mahdix.RED
# GREEN = mahdix.GREEN
# YELLOW = mahdix.YELLOW
# BLUE=mahdix.BLUE
# ORANGE =mahdix.ORANGE
# LI_BLUE = '\033[1;34m'
# LI_MAGENTA = '\033[1;35m'
# LI_CYAN = '\033[1;36m'
# LI_WHITE = '\033[1;37m'
# Background colors
# BG_BLACK = '\033[40m'
# BG_RED = '\033[41m'
# BG_GREEN = '\033[42m'
#---- <<<There are more cloure are added>>------

#<<<<You can use as fucntion your caoud make extra ordanary>>>
# exp;
# import mahdix as M
# M.P('mahdi')
# if YOUr helpfull You can try it.... Iam a little boy So Try to Do somthing>>>>>''',
package=['mahdit','os','requests','base64','random','sys'],
install_requires=[])
