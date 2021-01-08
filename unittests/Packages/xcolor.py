from plasTeX.Packages.xcolor import *

def test_colorparser_next():
    c = ColorParser()
    c.scan('1 2 3 4')
    assert c.next

def test_colorparser_empty():
    c = ColorParser()
    e = c.empty()
    assert e['element'] == ColorParser.Elements.empty

def test_colorparser_int():
    c = ColorParser()
    c.scan('5')
    e = c.int()
    assert e['element'] == ColorParser.Elements.int and e['value']==5

def test_colorparser_hex_int():
    c = ColorParser()
    c.scan('0000AB')
    e = c.int()
    assert e['element'] == ColorParser.Elements.int and e['value']==171

def test_colorparser_num():
    c = ColorParser()
    c.scan('5')
    e = c.num()
    assert e['element'] == ColorParser.Elements.int and e['value']==5
    c.scan('-5')
    e = c.num()
    assert e is None

def test_colorparser_dec():
    c = ColorParser()
    c.scan('-.1')
    e = c.dec()
    assert e['element'] == ColorParser.Elements.dec and e['value']==-0.1

def test_colorparser_div():
    c = ColorParser()
    c.scan('1.1')
    e = c.div()
    assert e['element'] == ColorParser.Elements.dec and e['value']==1.1
    c.scan('0')
    e = c.div()
    assert e is None

def test_colorparser_pct():
    c = ColorParser()
    c.scan('51.5')
    e = c.pct()
    assert e['element'] == ColorParser.Elements.dec and e['value']==51.5
    c.scan('100')
    e = c.pct()
    assert e['element'] == ColorParser.Elements.int and e['value']==100
    c.scan('0')
    e = c.pct()
    assert e['element'] == ColorParser.Elements.int and e['value']==0
    c.scan('-10')
    e = c.pct()
    assert e is None
    c.scan('110')
    e = c.pct()
    assert e is None

def test_colorparser_id():
    c = ColorParser()
    c.scan('colorname')
    e = c.id()
    assert e['element'] == ColorParser.Elements.id and e['id']=='colorname'
    c.scan('!-invalid-colorname')
    e = c.id()
    assert e is None

def test_colorparser_function():
    c = ColorParser()
    c.scan('wheel')
    e = c.function()
    assert e['element'] == ColorParser.Elements.id and e['id']=='wheel'
    c.scan('twheel')
    e = c.function()
    assert e['element'] == ColorParser.Elements.id and e['id']=='twheel'
    c.scan('invalid-function')
    e = c.function()
    assert e is None

def test_colorparser_dot():
    c = ColorParser()
    c.scan('.')
    e = c.dot()
    assert e['element'] == ColorParser.Elements.id and e['id']=='.'
    c.scan('!')
    e = c.dot()
    assert e is None

def test_colorparser_named():
    c = ColorParser()
    c.scan('named')
    e = c.named()
    assert e['element'] == ColorParser.Elements.named
    c.scan('not-named')
    e = c.named()
    assert e is None

def test_colorparser_ext_id():
    c = ColorParser()
    c.scan('foo')
    e = c.ext_id()
    assert e['element'] == ColorParser.Elements.ext_id and e['ids']==['foo','foo']
    c.scan('foo=bar')
    e = c.ext_id()
    assert e['element'] == ColorParser.Elements.ext_id and e['ids']==['foo','bar']

def test_colorparser_id_list():
    c = ColorParser()
    c.scan('foo,foo=bar,baz,bar=baz')
    e = c.id_list()
    assert e['element'] == ColorParser.Elements.id_list
    assert e['idlist'][0] == ['foo','foo']
    assert e['idlist'][1] == ['foo','bar']
    assert e['idlist'][2] == ['baz','baz']
    assert e['idlist'][3] == ['bar','baz']

def test_colorparser_name():
    c = ColorParser()
    c.scan('.')
    e = c.name()
    assert e['element'] == ColorParser.Elements.id and e['id']=='.'
    c.scan('foo')
    e = c.name()
    assert e['element'] == ColorParser.Elements.id and e['id']=='foo'

def test_colorparser_core_model():
    c = ColorParser()
    c.scan('rgb')
    e = c.core_model()
    assert e['element'] == ColorParser.Elements.model and e['model']==ColorModel.rgb
    c.scan('RGB')
    e = c.core_model()
    assert e is None
    c.scan('named')
    e = c.core_model()
    assert e is None

def test_colorparser_num_model():
    c = ColorParser()
    c.scan('rgb')
    e = c.num_model()
    assert e['element'] == ColorParser.Elements.model and e['model']==ColorModel.rgb
    c.scan('RGB')
    e = c.num_model()
    assert e['element'] == ColorParser.Elements.model and e['model']==ColorModel.RGB
    c.scan('named')
    e = c.num_model()
    assert e is None

def test_colorparser_model():
    c = ColorParser()
    c.scan('rgb')
    e = c.model()
    assert e['element'] == ColorParser.Elements.model and e['model']==ColorModel.rgb
    c.scan('RGB')
    e = c.model()
    assert e['element'] == ColorParser.Elements.model and e['model']==ColorModel.RGB
    c.scan('named')
    e = c.model()
    assert e['element'] == ColorParser.Elements.named

def test_colorparser_model_list_basic():
    c = ColorParser()
    c.scan('rgb/RGB/named')
    e = c.model_list_basic()
    assert e['element'] == ColorParser.Elements.model_list
    assert e['models'][0]==ColorModel.rgb
    assert e['models'][1]==ColorModel.RGB
    assert e['models'][2]==ColorModel.natural

def test_colorparser_model_list():
    c = ColorParser()
    c.scan('rgb/RGB/named')
    e = c.model_list()
    assert e['element'] == ColorParser.Elements.model_list
    assert e['models'][0]==ColorModel.rgb
    assert e['models'][1]==ColorModel.RGB
    assert e['models'][2]==ColorModel.natural
    c.scan('hsb:rgb/RGB/named')
    e = c.model_list()
    assert e['element'] == ColorParser.Elements.model_list
    assert e['models'][0]==ColorModel.rgb
    assert e['models'][1]==ColorModel.RGB
    assert e['models'][2]==ColorModel.natural
    assert e['model'] == ColorModel.hsb

def test_colorparser_spec():
    c = ColorParser()
    c.scan('0.25,0.75,0.1')
    e = c.spec()
    assert e['element'] == ColorParser.Elements.spec and e['values']==[0.25,0.75,0.1]
    c.scan('20 40 60')
    e = c.spec()
    assert e['element'] == ColorParser.Elements.spec and e['values']==[20,40,60]
    c.scan('123ABC')
    e = c.spec()
    assert e['element'] == ColorParser.Elements.spec and e['values']==[1194684]

def test_colorparser_spec_list():
    c = ColorParser()
    c.scan('0.25,0.75,0.1/20 40 60/foo')
    e = c.spec_list()
    assert e['element'] == ColorParser.Elements.spec_list
    assert e['specs'][0]['values'] == [0.25,0.75,0.1]
    assert e['specs'][1]['values'] == [20,40,60]
    assert e['specs'][2]['id'] == 'foo'

def test_colorparser_prefix():
    c = ColorParser()
    c.scan('---')
    e = c.prefix()
    assert e['element']==ColorParser.Elements.minus and e['value']==3

def test_colorparser_postfix():
    c = ColorParser()
    c.scan('!!++')
    e = c.postfix()
    assert e['element']==ColorParser.Elements.series_step and e['value']==2
    c.scan('!![6]')
    e = c.postfix()
    assert e['element']==ColorParser.Elements.series_access and e['value']==6

def test_colorparser_mix():
    c = ColorParser()
    c.scan('!25!foo')
    e = c.mix()
    assert e['element']==ColorParser.Elements.mix and e['pct']==25 and e['id']=='foo'
    c.scan('!50')
    e = c.mix()
    assert e['element']==ColorParser.Elements.mix and e['pct']==50 and e['id']=='white'

def test_colorparser_mix_current_color():
    c = ColorParser()
    c.scan('!25!.')
    e = c.mix()
    assert e['element'] == ColorParser.Elements.mix
    assert e['pct'] == 25 and e['id']=='.'

def test_colorparser_mix_expr():
    c = ColorParser()
    c.scan('!25!foo!50!bar!75')
    e = c.mix_expr()
    assert e['element']==ColorParser.Elements.mix_expr
    assert e['mixes'][0]['element'] == ColorParser.Elements.mix
    assert e['mixes'][0]['pct'] == 25 and e['mixes'][0]['id']=='foo'
    assert e['mixes'][1]['element'] == ColorParser.Elements.mix
    assert e['mixes'][1]['pct'] == 50 and e['mixes'][1]['id']=='bar'
    assert e['mixes'][2]['element'] == ColorParser.Elements.mix
    assert e['mixes'][2]['pct'] == 75 and e['mixes'][2]['id']=='white'

def test_colorparser_expr():
    c = ColorParser()
    c.colors = basenames(ColorModel.natural)
    c.colors['foo'] = c.parseColorSeries('rgb', 'last', None, 'red', None, 'blue')
    c.colors['foo'].reset(16)
    c.scan('-foo!25!green!50!blue!![5]')
    e = c.expr()
    assert e['element']==ColorParser.Elements.expr

def test_colorparser_ext_expr():
    c = ColorParser()
    c.colors = basenames(ColorModel.natural)
    c.scan('rgb:red,4;green!25!blue,2;yellow,1')
    e = c.ext_expr()
    assert e['element']==ColorParser.Elements.expr

def test_colorparser_color():
    c = ColorParser()
    c.colors = basenames(ColorModel.natural)
    c.scan('rgb:red,4;green!25!blue,2;yellow,1>wheel,1,12')
    e = c.ext_expr()
    assert e['element']==ColorParser.Elements.expr

def test_colorparser_scanner():
    c = ColorParser().scan(', RGB wave named -0.5 .25 +4.1 33 -77 --- ++ identifier !! : !')
    assert c[0]['element']==ColorParser.Elements.comma
    assert c[1]['element']==ColorParser.Elements.model and c[1]['model']==ColorModel.RGB
    assert c[2]['element']==ColorParser.Elements.model and c[2]['model']==ColorModel.wave
    assert c[3]['element']==ColorParser.Elements.named
    assert c[4]['element']==ColorParser.Elements.dec and c[4]['value']==-0.5
    assert c[5]['element']==ColorParser.Elements.dec and c[5]['value']==0.25
    assert c[6]['element']==ColorParser.Elements.dec and c[6]['value']==4.1
    assert c[7]['element']==ColorParser.Elements.int and c[7]['value']==33
    assert c[8]['element']==ColorParser.Elements.int and c[8]['value']==-77
    assert c[9]['element']==ColorParser.Elements.minus and c[9]['value']==3
    assert c[10]['element']==ColorParser.Elements.plus and c[10]['value']==2
    assert c[11]['element']==ColorParser.Elements.id and c[11]['id']=='identifier'
    assert c[12]['element']==ColorParser.Elements.symbol and c[12]['id']=='!!'
    assert c[13]['element']==ColorParser.Elements.symbol and c[13]['id']==':'
    assert c[14]['element']==ColorParser.Elements.symbol and c[14]['id']=='!'

def test_colorparser_basic_rgb_parsing():
    c = ColorParser().parseColor('.1,.2,.3', 'rgb')
    assert c.r == 0.1
    assert c.g == 0.2
    assert c.b == 0.3

def test_colorparser_basic_cmy_parsing():
    c = ColorParser().parseColor('.1,.2,.3', 'cmy')
    assert c.c == 0.1
    assert c.m == 0.2
    assert c.y == 0.3

def test_colorparser_basic_cmyk_parsing():
    c = ColorParser().parseColor('.1,.2,.3,.4', 'cmyk')
    assert c.c == 0.1
    assert c.m == 0.2
    assert c.y == 0.3
    assert c.k == 0.4

def test_colorparser_basic_hsb_parsing():
    c = ColorParser().parseColor('.1,.2,.3', 'hsb')
    assert c.h == 0.1
    assert c.s == 0.2
    assert c.b == 0.3

def test_colorparser_basic_gray_parsing():
    c = ColorParser().parseColor('.1', 'gray')
    assert c.gray == 0.1

def test_colorparser_basic_wave_parsing():
    c = ColorParser().parseColor('500', 'wave')
    assert c.freq == 500

def test_colorparser_basic_RGB_parsing():
    c = ColorParser().parseColor('255,127.5,63.75', 'RGB')
    assert c.r == 1.0
    assert c.g == 0.5
    assert c.b == 0.25

def test_colorparser_basic_HSB_parsing():
    c = ColorParser().parseColor('120,60,30', 'HSB')
    assert c.h == 0.5
    assert c.s == 0.25
    assert c.b == 0.125

def test_colorparser_basic_Hsb_parsing():
    c = ColorParser().parseColor('180,0.5,0.25', 'Hsb')
    assert c.h == 0.5
    assert c.s == 0.5
    assert c.b == 0.25

def test_colorparser_basic_HTML_parsing():
    c = ColorParser().parseColor('FF3300', 'HTML')
    assert c.r == 1
    assert c.g == 0.2
    assert c.b == 0

def test_colorparser_basic_Gray_parsing():
    c = ColorParser().parseColor('3', 'Gray')
    assert c.gray == 0.2

def test_colorparser_color_expr_parsing():
    p = ColorParser()
    p.colors = basenames(ColorModel.natural)
    p.colors['foo'] = p.parseColorSeries('rgb', 'last', None, 'red', None, 'blue')
    p.colors['foo'].reset(16)
    c = p.parseColor('-foo!25!green!50!blue!!+>wheel,1,12').as_hsb
    assert round(c.h,4) == 0.1389 and round(c.s,4) == 0.4286 and round(c.b,4) == 0.875
    c = p.parseColor('-foo!25!green!50!blue!!+>wheel,1,12').as_hsb
    assert round(c.h,4) == 0.14 and round(c.s,4) == 0.4425 and round(c.b,4) == 0.8828

def test_colorparser_ext_color_expr_parsing():
    p = ColorParser()
    p.colors = basenames(ColorModel.natural)
    c = p.parseColor('rgb:red,4;green!25!blue,2;yellow,1')
    assert round(c.r,3)==0.714 and round(c.g,3)==0.214 and round(c.b,3)==0.214

def test_colorparser_colorseries_step():
    p = ColorParser()
    p.colors = basenames(ColorModel.natural)
    p.colors['foo'] = p.parseColorSeries('rgb', 'step', 'rgb', '0.4,0.6,0.8', 'rgb', '0.2,0.2,0.2' )
    p.colors['foo'].reset(16)
    c = p.parseColor('foo!![1]')
    assert round(c.r,3)==0.6 and round(c.g,3)==0.8 and round(c.b)==1
    c = p.parseColor('foo!![2]')
    assert round(c.r,3)==0.8 and round(c.g,3)==1.0 and round(c.b,3)==0.2

def test_colornames():
    colors = basenames()
    colors.update(x11names())
    colors.update(svgnames())
    colors.update(dvipsnames())
    assert colors['white'].gray == 1.0
    assert colors['Tan'].c == 0.14 and colors['Tan'].m == 0.42 and colors['Tan'].y == 0.56 and colors['Tan'].k == 0
    assert colors['FireBrick'].r == 0.698 and colors['FireBrick'].g == 0.132 and colors['FireBrick'].b == 0.132
    assert colors['Maroon4'].r == 0.545 and colors['Maroon4'].g == 0.11 and colors['Maroon4'].b == 0.385

def test_color_addition():
    c1 = ColorParser().parseColor('0.1,0.2,0.5', 'rgb')
    c2 = ColorParser().parseColor('0.4,0.5,1.0', 'rgb')
    c = (c1+c2).wrapped
    assert c.r == 0.5
    assert c.g == 0.7
    assert c.b == 0.5

def test_color_subtraction():
    c1 = ColorParser().parseColor('0.4,0.2,1.0', 'rgb')
    c2 = ColorParser().parseColor('0.2,0.5,0.5', 'rgb')
    c = (c1-c2).wrapped
    assert c.r == 0.2
    assert c.g == 0.7
    assert c.b == 0.5

def test_color_mul():
    c1 = ColorParser().parseColor('0.4,0.2,0.5', 'rgb')
    c = (2*c1).wrapped
    assert c.r == 0.8
    assert c.g == 0.4
    assert c.b == 1.0

def test_color_as_model():
    c = ColorParser().parseColor('0.4,0.6,0.8', 'rgb')
    rgb = c.as_model(ColorModel.rgb)
    cmyk = c.as_model(ColorModel.cmyk)
    cmy = c.as_model(ColorModel.cmy)
    gray = c.as_model(ColorModel.gray)
    hsb = c.as_model(ColorModel.hsb)
    assert round(rgb.r,3) == 0.4 and round(rgb.g,3) == 0.6 and round(rgb.b,3) == 0.8
    assert round(cmyk.c,3) == 0.4 and round(cmyk.m,3) == 0.2 and round(cmyk.y,3) == 0.0 and round(cmyk.k,3) == 0.2
    assert round(cmy.c,3) == 0.6 and round(cmy.m,3) == 0.4 and round(cmy.y,3) == 0.2
    assert round(gray.gray,3) == 0.562
    assert round(hsb.h,3) == 0.583 and round(hsb.s,3) == 0.5 and round(hsb.b,3) == 0.8

    c2 = ColorParser().parseColor('400', 'wave')
    rgb2 = c2.as_model(ColorModel.rgb)
    hsb2 = c2.as_model(ColorModel.hsb)
    assert round(rgb2.r,3) == 0.433 and round(rgb2.g,3) == 0.0 and round(rgb2.b,3) == 0.650
    assert round(hsb2.h,3) == 0.778 and round(hsb2.s,3) == 1.0 and round(hsb2.b,3) == 0.650

def test_color_as_list():
    c = ColorParser().parseColor('0.4,0.6,0.8', 'rgb')
    assert c.as_list == [0.4,0.6,0.8]

def test_color_complement():
    c = ColorParser().parseColor('1.0,0.5,0.0', 'rgb')
    assert c.complement.r == 0.0
    assert c.complement.g == 0.5
    assert c.complement.b == 1.0

def test_color_command(tmpdir, renderXHTML, make_document):
    text = '''\\pagecolor{red}\\nopagecolor{\\color{red}Testing}'''
    doc = make_document(packages='xcolor', content=text)
    out = doc.getElementsByTagName('color')[0]
    output = renderXHTML(tmpdir, doc)
    assert output.findAll('span')[-1]['style'] == 'color:#FF0000'

def test_extended_color_command(tmpdir, renderXHTML, make_document):
    text = '''\\definecolorseries{foo}{rgb}{last}{red}{blue}\\resetcolorseries[20]{foo}
        {\\color{rgb:red,1;yellow,2;-foo!25!blue!50!white!!++,3>wheel,2,12}Testing}'''
    doc = make_document(packages='xcolor', content=text)
    out = doc.getElementsByTagName('color')[0]
    output = renderXHTML(tmpdir, doc)
    assert output.findAll('span')[-1]['style'] == 'color:#2AAF0F'

def test_mixing_current_color(tmpdir, renderXHTML, make_document):
    text = '''{\\color{red}Test\\color{.!50!white}{ing}}'''
    doc = make_document(packages='xcolor', content=text)
    out = doc.getElementsByTagName('color')[0]
    output = renderXHTML(tmpdir, doc)
    assert output.findAll('span')[-1]['style'] == 'color:#FF7F7F'

def test_textcolor_command(tmpdir, renderXHTML, make_document):
    text = '''\\textcolor{blue}{Testing}'''
    doc = make_document(packages='xcolor', content=text)
    out = doc.getElementsByTagName('textcolor')[0]
    output = renderXHTML(tmpdir, doc)
    assert output.findAll('span')[-1]['style'] == 'color:#0000FF'

def test_colorbox_command(tmpdir, renderXHTML, make_document):
    text = '''\\colorbox{blue}{Testing}'''
    doc = make_document(packages='xcolor', content=text)
    out = doc.getElementsByTagName('colorbox')[0]
    output = renderXHTML(tmpdir, doc)
    assert output.findAll('span')[-1]['style'] == 'background-color:#0000FF'

def test_fcolorbox_command(tmpdir, renderXHTML, make_document):
    text = '''\\fcolorbox{blue}{green}{Testing}'''
    doc = make_document(packages='xcolor', content=text)
    out = doc.getElementsByTagName('fcolorbox')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'background-color:#00FF00' in output.findAll('span')[-1]['style']
    assert 'border:1px solid #0000FF' in output.findAll('span')[-1]['style']

def test_DefineNamedColor_command(tmpdir, renderXHTML, make_document):
    text = '''\\DefineNamedColor{named}{foo}{rgb}{0.3,0.2,0.1}'''
    doc = make_document(packages='xcolor', content=text)
    colors = doc.userdata.getPath('packages/xcolor/colors')
    assert colors['foo'].r == 0.3 and colors['foo'].g == 0.2 and colors['foo'].b == 0.1
    out = doc.getElementsByTagName('DefineNamedColor')[0]
    assert out.source == ''

def test_definecolor_command(tmpdir, renderXHTML, make_document):
    text = '''\\definecolor{foo}{rgb}{0.3,0.2,0.1}'''
    doc = make_document(packages='xcolor', content=text)
    colors = doc.userdata.getPath('packages/xcolor/colors')
    assert colors['foo'].r == 0.3 and colors['foo'].g == 0.2 and colors['foo'].b == 0.1

def test_providecolor_command(tmpdir, renderXHTML, make_document):
    text = '''\\providecolor{white}{rgb}{0.3,0.2,0.1}'''
    doc = make_document(packages='xcolor', content=text)
    colors = doc.userdata.getPath('packages/xcolor/colors')
    assert colors['white'].gray == 1.0

def test_colorlet_command(tmpdir, renderXHTML, make_document):
    text = '''\\colorlet{foo}{white}'''
    doc = make_document(packages='xcolor', content=text)
    colors = doc.userdata.getPath('packages/xcolor/colors')
    assert colors['foo'].gray == 1.0

def test_definecolorset_command(tmpdir, renderXHTML, make_document):
    text = '''\\definecolorset{gray}{x}{10}{foo,0;bar,0.5;baz,0.75}'''
    doc = make_document(packages='xcolor', content=text)
    colors = doc.userdata.getPath('packages/xcolor/colors')
    assert colors['xfoo10'].gray == 0.0
    assert colors['xbar10'].gray == 0.5
    assert colors['xbaz10'].gray == 0.75

def test_providecolorset_command(tmpdir, renderXHTML, make_document):
    text = '''\\colorlet{xfoo10}{white}\\providecolorset{gray}{x}{10}{foo,0;bar,0.5;baz,0.75}'''
    doc = make_document(packages='xcolor', content=text)
    colors = doc.userdata.getPath('packages/xcolor/colors')
    assert colors['xfoo10'].gray == 1.0
    assert colors['xbar10'].gray == 0.5
    assert colors['xbaz10'].gray == 0.75

def test_preparecolorset_command(tmpdir, renderXHTML, make_document):
    text = '''\\preparecolorset{gray}{x}{10}{foo,0;bar,0.5;baz,0.75}'''
    doc = make_document(packages='xcolor', content=text)
    colors = doc.userdata.getPath('packages/xcolor/colors')
    assert colors['xfoo10'].gray == 0.0
    assert colors['xbar10'].gray == 0.5
    assert colors['xbaz10'].gray == 0.75

def test_definecolors_command(tmpdir, renderXHTML, make_document):
    text = '''\\definecolors{foo=white,bar=black}'''
    doc = make_document(packages='xcolor', content=text)
    colors = doc.userdata.getPath('packages/xcolor/colors')
    assert colors['foo'].gray == 1.0
    assert colors['bar'].gray == 0.0

def test_providecolors_command(tmpdir, renderXHTML, make_document):
    text = '''\\providecolors{foo=white,red=black}'''
    doc = make_document(packages='xcolor', content=text)
    colors = doc.userdata.getPath('packages/xcolor/colors')
    assert colors['foo'].gray == 1.0
    assert colors['red'].r == 1.0

def test_colorseries_commands(tmpdir, renderXHTML, make_document):
    text = '''\\definecolorseries{foo}{rgb}{last}{red}{blue}\\resetcolorseries[20]{foo}
        \\colorlet{bar}{foo!!+}\\colorlet{baz}{foo!!+}'''
    doc = make_document(packages='xcolor', content=text)
    colors = doc.userdata.getPath('packages/xcolor/colors')
    assert colors['bar'].r == 1.0 and colors['bar'].g == 0.0 and colors['bar'].b == 0.0
    assert colors['baz'].r == 0.95 and colors['baz'].g == 0.0 and colors['baz'].b == 0.05
