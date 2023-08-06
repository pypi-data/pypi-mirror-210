from main import DECA

deca = DECA().cuda()
tf_dummy = deca.data_preprocess('./assets/0003.png')
codedict, visdict = deca(tf_dummy)
"""
codedict
    - shape(b, 100)
    - tex(b, 50)
    - exp(b, 50)
    - pose(b, 6)
    - cam(b, 3)
    - light(b, 9, 3)
visdict
    - inputs(b 3 224 224)
    - shape_iamges(b 3 224 224)
    - shape_detail_images (b 3 224 224)
"""

resultdict = deca.data_postprocess(visdict)