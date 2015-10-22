
mimetype = 'application/epub+zip'

container = '''<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
         <rootfile full-path="OEBPS/content.opf"
          media-type="application/oebps-package+xml" />
    </rootfiles>
</container>
'''

titlepage = '''<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
  <title tal:content="data/title"></title>
  <style type="text/css">
      .booktitle {
        letter-spacing: 0.20em;
        font-family: Times, serif;
        font-weight: bold;
        font-size: x-large;
        margin: 5em;
      }
  </style>
</head>
<body>
<div class="booktitle">
  <span tal:content="data/title"></span>
</div>
<ul class="toc">
    <span tal:condition="data/subs" tal:repeat="section data/subs" tal:omit-tag="">
      <li><a tal:attributes="href section/url" tal:content="section/entry"></a></li>
      <span tal:condition="section/subs">
        <ul>
          <span tal:repeat="subsection section/subs" tal:omit-tag="">
            <li><a tal:attributes="href subsection/url" tal:content="subsection/entry"></a></li>
            <span tal:condition="subsection/subs">
              <ul>
                <span tal:repeat="subsubsection subsection/subs" tal:omit-tag="">
                  <li><a tal:attributes="href subsubsection/url" tal:content="subsubsection/entry"></a></li>
                </span>
              </ul>
            </span>      
          </span>
        </ul>    
      </span>
    </span>
  </ul>
</body>
</html>'''

opf = '''<package xmlns="http://www.idpf.org/2007/opf"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    unique-identifier="bookid" version="2.0">
  <metadata>
    <dc:title tal:content="data/title"></dc:title>
    <dc:creator>My Company Inc.</dc:creator>
    <dc:identifier id="bookid" tal:content="data/isbn"></dc:identifier>
    <dc:language>en</dc:language>
    <dc:date tal:content="date"></dc:date>
    <dc:publisher>My Publisher, Inc.</dc:publisher>
    <meta name="cover" content="cover-image" />
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="text/xml"/>
    <span tal:omit-tag="" tal:repeat="filename data/cssnames">
      <item id="style"   tal:attributes="href filename/fullname" media-type="text/css"/>
    </span>
    <item id="titlepage" href="titlepage.html" media-type="application/xhtml+xml"/>    
    <span tal:omit-tag="" tal:repeat="filename data/htmlnames">
      <item tal:attributes="id filename/stem;href filename/fullname" media-type="application/xhtml+xml"/>
    </span>
    <span tal:omit-tag="" tal:repeat="filename data/imagenames">
      <item tal:attributes="id filename/stem;href filename/fullname" media-type="image/png"/>
    </span>
  </manifest>
  <spine toc="ncx">
    <itemref idref="titlepage" linear="no"/>
    <span tal:omit-tag="" tal:repeat="filename data/htmlnames">
      <itemref tal:attributes="idref filename/stem"/>
    </span>
  </spine>
  <guide>
    <reference href="titlepage.html" type="cover" title="Cover"/>
  </guide>
</package>'''

ncx = '''<span tal:define="global mycounter python:1" tal:omit-tag="" >
  <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" tal:attributes="content data/isbn"/>
    <meta name="dtb:depth" content="3"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle>
    <text tal:content="data/title"></text>
  </docTitle>
  <navMap>
    <navPoint tal:attributes="id string:navpoint-${mycounter};playOrder string:${mycounter}">
      <navLabel>
        <text>Book Cover</text>
      </navLabel>
      <content src="titlepage.html" />
    </navPoint>
    <span tal:repeat="section data/subs" tal:omit-tag="" >
      <navPoint tal:define="global mycounter python:mycounter+1"
                tal:attributes="id string:navpoint-${mycounter}; playOrder string:${mycounter}">
        <navLabel>
          <text tal:content="section/entry"></text>
        </navLabel>
        <content tal:attributes="src section/url" />
        <span tal:repeat="subsection section/subs" tal:omit-tag="" >
          <navPoint tal:define="global mycounter python:mycounter+1"
                    tal:attributes="id string:navpoint-${mycounter}; playOrder string:${mycounter}">
            <navLabel>
              <text tal:content="subsection/entry"></text>
            </navLabel>
            <content tal:attributes="src subsection/url" />
            <span tal:repeat="subsubsection subsection/subs" tal:omit-tag="" >
              <navPoint tal:define="global mycounter python:mycounter+1"
                        tal:attributes="id string:navpoint-${mycounter}; playOrder string:${mycounter}">
                <navLabel>
                  <text tal:content="subsubsection/entry"></text>
                </navLabel>
                <content tal:attributes="src subsubsection/url" />
              </navPoint>
            </span>
          </navPoint>
        </span>
      </navPoint>  
    </span>  
  </navMap>
  </ncx>
</span>
'''


