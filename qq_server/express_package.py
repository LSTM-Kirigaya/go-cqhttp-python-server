import random

class ExpressionPackage:
    Snicker = 'http://pic.qt6.com/up/2021-4/2021041311263544392.jpg'
    Annoying = 'https://rss.sfacg.com/web/account/images/avatars/app/2006/05/f5fdaa0b-174e-4a14-9630-c8047bb9c4fd.jpg'
    Casual = 'https://pica.zhimg.com/80/v2-df8232d6b1ea3449cab094a9c5b6273c_1440w.png'
    
    common_lib = [
        'https://img2.tapimg.com/bbcode/images/5e415da57508a9ba5596a8600f498a16.png',
        'https://img2.tapimg.com/bbcode/images/dd7fd855f718c375fd0b8614278481b8.png',
        'https://img2.tapimg.com/bbcode/images/1e9fe72af6a37772c294db44cf8c508b.png',
        'https://img2.tapimg.com/bbcode/images/299bd8f6924cc807f4e18b140c8ab7bb.jpg',
        'https://img2.tapimg.com/bbcode/images/ba28d3fcbbd04e314560ac0f2b498f9c.jpg',
        'https://img2.tapimg.com/bbcode/images/65c6ecb7376a23b8f1cf67e2d3fb36c1.jpg',
        'https://i0.hdslb.com/bfs/article/1a3cdb48933c9f8de59af1cc64ddcdf1d5372038.gif',
        'https://i0.hdslb.com/bfs/article/66e2d9735c1b3311d6a3c9d517d4694d158c8ddf.gif',
        'https://i0.hdslb.com/bfs/article/349153826676bb5d5c44e7e23ae32989de36e5d2.gif'
    ]

    error_lib = [
        'https://rss.sfacg.com/web/account/images/avatars/app/2006/05/f5fdaa0b-174e-4a14-9630-c8047bb9c4fd.jpg',
        'https://img2.tapimg.com/bbcode/images/8e45ec4a183fc31c4e5607e8e58c8482.png',
        'https://img2.tapimg.com/bbcode/images/299bd8f6924cc807f4e18b140c8ab7bb.jpg',
        'https://img2.tapimg.com/bbcode/images/96b356a8901dc301c8d55b541ffcbef0.jpg',
        'https://i0.hdslb.com/bfs/article/8371943096268c8cedef65a952f51bb16076e854.gif',
        'https://i0.hdslb.com/bfs/article/1a3cdb48933c9f8de59af1cc64ddcdf1d5372038.gif',
        'https://i0.hdslb.com/bfs/article/20be7f97e920aa311b1f73496643207bacc7b540.gif',
        'https://i0.hdslb.com/bfs/article/fccd4c6d83d3cbc61ddd64afa1ee6444ef1c5df3.gif'
    ]
    def random_common_image_url(self) -> str:
        return random.choice(self.common_lib)
    
    def random_error_image_url(self) -> str:
        return random.choice(self.error_lib)

    @property
    def common_url(self):
        return self.random_common_image_url()
    
    @property
    def error_url(self):
        return self.random_error_image_url()
        
    @property
    def random_url(self):
        images = self.error_lib + self.common_lib
        return random.choice(images)
    
    @property
    def common_cq_code(self):
        url = self.common_url
        return self.get_cq_code(url)
    
    @property
    def error_cq_code(self):
        url = self.error_url
        return self.get_cq_code(url)
    
    @property
    def random_cq_code(self):
        url = self.random_url
        return self.get_cq_code(url)
    
    def get_cq_code(self, url: str):
        return '[CQ:image,file={}]'.format(url)

express_package = ExpressionPackage()