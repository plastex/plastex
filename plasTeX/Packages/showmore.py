def ProcessOptions(options, document):
    """This is called when the package is loaded."""

    document.userdata.setdefault('extra-nav', []).extend([
        {'icon': 'eye-minus', 'id': 'showmore-minus', 'class': 'showmore'},
        {'icon': 'eye-plus', 'id': 'showmore-plus', 'class': 'showmore'}])
    document.userdata.setdefault('extra-css', []).append('showmore.css')
    document.userdata.setdefault('extra-js', []).extend(
            ['showmore.js', 'jquery.cookie.js'])

