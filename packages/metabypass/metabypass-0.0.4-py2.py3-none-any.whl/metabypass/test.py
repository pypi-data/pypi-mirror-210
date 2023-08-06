from solver import *
# from metabypass import MetaBypass
import time
CLIENT_ID = '292'  # ****CHANGE HERE WITH YOUR VALUE*******
CLIENT_SECRET = 'nA1SVOQEmEJgphyCScORGYO3lv5phUEairkZTXMX'  # ****CHANGE HERE WITH YOUR VALUE*******
EMAIL = 'deepmind.shj12@gmail.com'  # ****CHANGE HERE WITH YOUR VALUE*******
PASSWORD = 'sh123456'  # ****CHANGE HERE WITH YOUR VALUE*******
# CLIENT_ID = '292'  # ****CHANGE HERE WITH YOUR VALUE*******
# CLIENT_SECRET = 'yD3LuTOUefIBsczQK2RxgoUN3aV6aK9R9JSmnPvi'  # ****CHANGE HERE WITH YOUR VALUE*******
# EMAIL = 'abbas.habibnejad.j@gmail.com'  # ****CHANGE HERE WITH YOUR VALUE*******
# PASSWORD = '11941072'  # ****CHANGE HERE WITH YOUR VALUE*******
solver=MetaBypass(CLIENT_ID,CLIENT_SECRET,EMAIL,PASSWORD)

site_url = "https://venesh.ir/web/"  # ****CHANGE HERE WITH YOUR VALUE*******
site_key = "6LfPFI0UAAAAABnuilqLhBJA8LCwziOXnt0NNPaU"  # ****CHANGE HERE WITH YOUR VALUE*******

# rev2_response = solver.reCAPTCHAV2(url=site_url, site_key=site_key)
# print(rev2_response)
captcha_rsponse = solver.image_captcha('C:\\Users\\shiva\\Downloads\\captcha_label\\captcha\\4.jpg',numeric=3,min_len=2,max_len=3)
print(captcha_rsponse)
