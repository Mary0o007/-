<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:output method="html" encoding="UTF-8" />

    <xsl:template match="/">
        <html>
            <head>
                <link rel="stylesheet" type="text/css" href="lab_1.css" />
                <title>Библиотека</title>
            </head>
            <body>
                <h2>Библиотека</h2>
                <table>
                    <tr>
                        <th>Книга/Журнал</th>
                        <th>Название</th>
                        <th>Автор</th>
                        <th>Год</th>
                        <th>Издательство</th>
                    </tr>
                    
                    <!-- Книги -->
                    <xsl:for-each select="library/book">
                        <tr>
                            <td>Книга</td>
                            <td><xsl:value-of select="title" /></td>
                            <td><xsl:value-of select="author" /></td>
                            <td><xsl:value-of select="year" /></td>
                            <td><xsl:value-of select="publisher" /></td>
                        </tr>
                    </xsl:for-each>

                    <!-- Журналы -->
                    <xsl:for-each select="library/magazine">
                        <tr>
                            <td>Журнал</td>
                            <td><xsl:value-of select="title" /></td>
                            <td>
                                <xsl:choose>
                                    <xsl:when test="author"><xsl:value-of select="author" /></xsl:when>
                                    <xsl:otherwise>Не указан</xsl:otherwise>
                                </xsl:choose>
                            </td>
                            <td><xsl:value-of select="year" /></td>
                            <td><xsl:value-of select="publisher" /></td>
                        </tr>
                    </xsl:for-each>
                </table>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
