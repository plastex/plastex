from plasTeX.Packages.color import latex2htmlcolor

def test_color():
    colors = [("1", "#FFFFFF"),
              ("0", "#000000"),
              ("0.4", "#666666"),
              ("1,0,1", "#FF00FF"),
              ("0.2,0,0.8", "#3300CC")]

    for (i, o) in colors:
        assert latex2htmlcolor(i) == o
