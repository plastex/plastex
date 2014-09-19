<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:d="http://docbook.org/ns/docbook"
  version="1.0" exclude-result-prefixes="d"
  >
<!--
    <script src="https://google-code-prettify.googlecode.com/svn/loader/run_prettify.js?skin=doxy"></script>
-->
  <xsl:import href="/AppDocs/xml/docbook/xsl-1.78.1/html/onechunk.xsl" />

  <xsl:param name="xref.with.number.and.title" select="0" />
  <xsl:param name="table.borders.with.css" select="1" />
  <xsl:param name="table.cell.border.thickness">1pt</xsl:param>
  <xsl:param name="chunker.output.encoding">UTF-8</xsl:param>
  <xsl:param name="chunker.output.indent">yes</xsl:param>
  <xsl:param name="generate.id.attributes" select="1" />

  <xsl:param name="toc.list.type">ul</xsl:param>
  <xsl:param name="generate.toc">
    book toc,title
    article toc,title
    part toc
    preface toc
    chapter toc
    appendix toc
    section toc
  </xsl:param>
  <xsl:param name="toc.section.depth">2</xsl:param>
  <xsl:param name="generate.section.toc.level">1</xsl:param>
  <xsl:param name="toc.max.depth">1</xsl:param>
  <xsl:param name="autotoc.label.in.hyperlink">1</xsl:param>
  <xsl:param name="autotoc.label.separator"><xsl:text>  </xsl:text></xsl:param>

  <xsl:param name="html.stylesheet">css/foundation.css</xsl:param>
  <xsl:param name="html.stylesheet.type">text/css</xsl:param>

  <xsl:template match="d:programlisting" mode="class.value"><xsl:value-of select="'prettyprint'" /></xsl:template>
  <xsl:template match="d:citation">
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template name="user.head.content">
    <script src="js/vendor/modernizr.js"></script>
    <link href='http://fonts.googleapis.com/css?family=Open+Sans:400italic,400,600' rel='stylesheet' type='text/css'/>
    <link href='http://fonts.googleapis.com/css?family=Inconsolata:400,700' rel='stylesheet' type='text/css'/>
  </xsl:template>

  <!-- inline equations -->
  <xsl:template match="d:inlinemediaobject[@remap='math']/d:imageobject/d:imagedata">
    <xsl:element name="img">
      <xsl:attribute name="class">math</xsl:attribute>
      <xsl:attribute name="alt">
        <xsl:choose>
          <xsl:when test="../../d:textobject[@role='tex']/d:phrase">
            <xsl:value-of select="../../d:textobject[@role='tex']/d:phrase" />
          </xsl:when>
          <xsl:when test="../../d:alt">
            <xsl:value-of select="../../d:alt" />
          </xsl:when>
          <xsl:otherwise>
            <xsl:text>External File:</xsl:text>
            <xsl:value-of select="@fileref"></xsl:value-of>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
      <xsl:attribute name="src">
        <xsl:value-of select="@fileref" />
      </xsl:attribute>
    </xsl:element>
    <xsl:apply-templates />
  </xsl:template>

  <!--  block equations -->
  <xsl:template match="d:mediaobject[@remap='math']/d:imageobject/d:imagedata">
    <xsl:element name="img">
      <xsl:attribute name="class">math</xsl:attribute>
      <xsl:attribute name="alt">
        <xsl:choose>
          <xsl:when test="../../d:textobject[@role='tex']/d:phrase">
            <xsl:value-of select="../../d:textobject[@role='tex']/d:phrase" />
          </xsl:when>
          <xsl:when test="../../d:alt">
            <xsl:value-of select="../../d:alt" />
          </xsl:when>
          <xsl:otherwise>
            <xsl:text>External File:</xsl:text>
            <xsl:value-of select="@fileref"></xsl:value-of>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
      <xsl:attribute name="src">
        <xsl:value-of select="@fileref" />
      </xsl:attribute>

    </xsl:element>
    <xsl:apply-templates />
  </xsl:template>

</xsl:stylesheet>