from plasTeX.TeX import TeX

def test_accent():
    input_data = r'\"o'
    tex = TeX()
    tex.input(input_data)
    node = tex.parse()[0]
    assert node.source == input_data
