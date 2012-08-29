<?xml version="1.0" encoding="UTF-8"?>

<!--
/* ***** BEGIN LICENSE BLOCK *****
 * Licensed under Version: MPL 1.1/GPL 2.0/LGPL 2.1
 * Full Terms at http://mozile.mozdev.org/0.8/LICENSE
 *
 * Software distributed under the License is distributed on an "AS IS" basis,
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
 * for the specific language governing rights and limitations under the
 * License.
 *
 * The Original Code is James A. Overton's code (james@overton.ca).
 *
 * The Initial Developer of the Original Code is James A. Overton.
 * Portions created by the Initial Developer are Copyright (C) 2005-2006
 * the Initial Developer. All Rights Reserved.
 *
 * Contributor(s):
 *	James A. Overton <xsl:james@overton.ca>
 *
 * ***** END LICENSE BLOCK ***** */

/** 
 * @fileoverview Converts HTML into MediaWiki's wikitext format.
 * <xsl:p>Project Homepage: http://mozile.mozdev.org
 * @author James A. Overton <xsl:james@overton.ca>
 * @version 0.8
 * $Id: html2wiki.xsl,v 1.3 2006/09/02 21:20:13 jameso Exp $
 */

/**** SUPPORT ****/
In general, white space will not always match the original wikitext.

Complete Support:
- Paragraphs
- Bold and Italics
- Inline HTML: tt, code, strike, u, span, sup, sub
- Other HTML: br, hr
- Lists: ul, ol, dl
- Tables
- Math
- Headings - Should always use h* elements.
- No Wiki - The element <p class="nowiki"> becomes <nowiki>
- Templates - The combination
	<span class="template">
		<span class="template-name">Template name</span>
		...
	</span>
	becomes {{Template name}}
- Reference - The combination
	<sup class="reference">
		<span class="reference-content">Reference content.</span>
		...
	</sup>
	becomes <ref>Reference content.</ref>
- References - The element <ol class="references">...</ol> becomes <references/>
- Categories - The element
	<span class="category-link">Category name</span> 
	becomes [[Category:Category name]]
- Images - Container divs for "frame" images should be marked with class="frame" instead of class="thumb", and scaled images should be marked with class="scaled" in addition to their other classes.

Partial Support:
- Links - Some cases not yet handled.
- Comments - Problems maintaining HTML entities.
- Block HTML: center, blockquote, pre - Minor problems with white space.
- Generated Content - Not all automatically generated content is stripped.

Unsupported:
- Signatures - Nothing extra needed?
- Date translations - Nothing extra needed?
- Redirects - No change required?

In order to fully support HTML 2 wikitext translation the MediaWiki wikitext parser will have to provide more information in the HTML output than it currently does (as of version 1.7.1). 
Proposed changes:
- Headings should use classes.
- The <nowiki> tag should translate to <p class="nowiki">
- Templates, references, category links, and magic words will have to be marked as such by the parser. This stylesheet assumes that:
	1) they will be marked by <span> tags (which should not change the page layout) or other container element.
	2) there will be nested <span> tags (hidden with CSS "display:none") with the wikitext content to be used.
	Nested templates do not need to be marked.
- Images need to be marked with more information about framing and scaling. THis can be done with added classes.

-->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<xsl:output method="text" encoding="UTF-8" media-type="text/plain"/>
	<xsl:strip-space elements="*"/>
	
	<xsl:template match="/">
		<xsl:text xml:space="preserve">html2wiki.xsl Wikitext Output

</xsl:text>
		<xsl:apply-templates/>
	</xsl:template>
	
	
	
	<!-- Preformatted Text -->
	<xsl:template match="text()[ancestor::pre]">
		<xsl:value-of select="."/>
	</xsl:template>
	
	<!-- Text: Remove newlines. -->
	<xsl:template match="text()">
		<xsl:value-of select="translate(., '&#xA;', ' ')"/>
	</xsl:template>

	
	<!-- Attributes: Create a space separated list. -->
	<xsl:template name="attributes">
		<xsl:if test="attribute::*">
			<xsl:text xml:space="preserve"> </xsl:text>
		</xsl:if>
		<xsl:for-each select="attribute::*">
			<!-- make name lowercase -->
			<xsl:value-of select="translate(name(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"/>
			<xsl:text xml:space="preserve">="</xsl:text>
			<xsl:value-of select="."/>
			<xsl:text xml:space="preserve">"</xsl:text>
			<xsl:if test="position() != last()">
				<xsl:text xml:space="preserve"> </xsl:text>
			</xsl:if>
		</xsl:for-each>
	</xsl:template>


	
	<!-- No Wiki: Insert a nowiki tag. -->
	<xsl:template match="p[@class='nowiki']">
		<xsl:text xml:space="preserve">
&lt;nowiki&gt;</xsl:text>
		<xsl:apply-templates/>
		<xsl:text xml:space="preserve">&lt;/nowiki&gt;
</xsl:text>
	</xsl:template>

	<!-- Template -->
	<xsl:template match="span[@class='template']">
		<xsl:text xml:space="preserve">{{</xsl:text>
		<xsl:value-of select="span[@class='template-name']"/>
		<xsl:text xml:space="preserve">}}
</xsl:text>
	</xsl:template>

	<!-- Reference -->
	<xsl:template match="sup[@class='reference']">
		<xsl:text xml:space="preserve">&lt;ref&gt;</xsl:text>
		<xsl:apply-templates select="span[@class='reference-content']"/>
		<xsl:text xml:space="preserve">&lt;/ref&gt;
</xsl:text>
	</xsl:template>
	
	<!-- References: Insert a closed references tag. -->
	<xsl:template match="ol[@class='references']">
		<xsl:text xml:space="preserve">&lt;references/&gt;
</xsl:text>
	</xsl:template>

	<!-- Category: Insert a category link. -->
	<xsl:template match="span[@class='category-link']">
		<xsl:text xml:space="preserve">[[</xsl:text>
		<xsl:value-of select="."/>
		<xsl:text xml:space="preserve">]]
</xsl:text>
	</xsl:template>

	<!-- Magic Words -->
	<xsl:template match="span[@class='magic-word']">
		<xsl:value-of select="span[@class='magic-word-name']"/>
		<xsl:text xml:space="preserve">
</xsl:text>
	</xsl:template>

	<!-- Table of Contents -->
	<xsl:template match="table[@id='toc']">
		<!-- Remove -->
	</xsl:template>

	<!-- Footer -->
	<xsl:template match="div[@class='printfooter']">
		<!-- Remove -->
	</xsl:template>

	<!-- Category Links -->
	<xsl:template match="div[@id='catlinks']">
		<!-- Remove -->
	</xsl:template>



	<!-- Paragraph -->
	<xsl:template match="p">
		<xsl:text xml:space="preserve">
</xsl:text>
		<xsl:apply-templates/>
		<xsl:text xml:space="preserve">
</xsl:text>
	</xsl:template>
	
	<!-- Italics -->
	<xsl:template match="i|em">
		<xsl:text xml:space="preserve">''</xsl:text>
		<xsl:apply-templates/>
		<xsl:text xml:space="preserve">''</xsl:text>
	</xsl:template>
	
	<!-- Bold -->
	<xsl:template match="b|strong">
		<xsl:text xml:space="preserve">'''</xsl:text>
		<xsl:apply-templates/>
		<xsl:text xml:space="preserve">'''</xsl:text>
	</xsl:template>
	
	<!-- Underline -->
	<xsl:template match="u|span[@style='text-decoration: underline;']">
		<xsl:text xml:space="preserve">&lt;u&gt;</xsl:text>
		<xsl:apply-templates/>
		<xsl:text xml:space="preserve">&lt;/u&gt;</xsl:text>
	</xsl:template>
	
	<!-- Strike -->
	<xsl:template match="s|strike|span[@style='text-decoration: line-through;']">
		<xsl:text xml:space="preserve">&lt;strike&gt;</xsl:text>
		<xsl:apply-templates/>
		<xsl:text xml:space="preserve">&lt;/strike&gt;</xsl:text>
	</xsl:template>
	
	<!-- Line Break -->
	<xsl:template match="br">
		<xsl:text xml:space="preserve">&lt;br&gt;</xsl:text>
	</xsl:template>
	
	<!-- Horizontal Rule -->
	<xsl:template match="hr">
		<xsl:text xml:space="preserve">----
</xsl:text>
	</xsl:template>
	
	<!-- General HTML Tags: Insert a tag with the same name and attributes. -->
	<xsl:template name="html">
		<!-- make name lowercase -->
		<xsl:param name="name" select="translate(name(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"/>
		<xsl:text xml:space="preserve">&lt;</xsl:text>
		<xsl:value-of select="$name"/>
		<xsl:call-template name="attributes"/>
		<xsl:text xml:space="preserve">&gt;</xsl:text>
		<xsl:apply-templates/>
		<xsl:text xml:space="preserve">&lt;/</xsl:text>
		<xsl:value-of select="$name"/>
		<xsl:text xml:space="preserve">&gt;</xsl:text>
	</xsl:template>
	
	<!-- http://meta.wikimedia.org/wiki/Help:HTML_in_wikitext -->
	
	<!-- Inline HTML Tags -->
	<xsl:template match="big|cite|code|em|font|rb|rp|rt|ruby|small|sub|sup|tt|var">
		<xsl:call-template name="html"/>
	</xsl:template>
	
	<!-- Block HTML Tags -->
	<xsl:template match="center|blockquote|h1|h2|h3|h4|h5|h6|pre">
		<xsl:text xml:space="preserve">
</xsl:text>
		<xsl:call-template name="html"/>
		<xsl:text xml:space="preserve">
</xsl:text>
	</xsl:template>
	
	<!-- Ignored HTML Tags -->
	<xsl:template match="script|div[@class='editsection']"/>
	
	<!-- Comments -->
	<xsl:template match="comment()">
		<xsl:text xml:space="preserve">
&lt;!--</xsl:text>
		<xsl:value-of select="."/>
		<xsl:text xml:space="preserve">--&gt;
</xsl:text>
	</xsl:template>


	
	<!-- Heading 1 -->
	<xsl:template match="h2|div[@class='heading2' or @style='border-bottom: 1px solid rgb(0, 0, 0); font-size: 150%;']">
		<xsl:text xml:space="preserve">
== </xsl:text>
		<xsl:apply-templates/>
		<xsl:text xml:space="preserve"> ==
</xsl:text>
	</xsl:template>
	
	<!-- Heading 2 -->
	<xsl:template match="h3|div[@class='heading3' or @style='font-size: 132%; font-weight: bold;']">
		<xsl:text xml:space="preserve">
=== </xsl:text>
		<xsl:apply-templates/>
		<xsl:text xml:space="preserve"> ===
</xsl:text>
	</xsl:template>
	
	<!-- Heading 3 -->
	<xsl:template match="h4|div[@class='heading4' or @style='font-size: 116%; font-weight: bold;']">
		<xsl:text xml:space="preserve">
==== </xsl:text>
		<xsl:apply-templates/>
		<xsl:text xml:space="preserve"> ====
</xsl:text>
	</xsl:template>


	
	<!-- Lists -->
	<xsl:template match="ul|ol|dl">
		<xsl:apply-templates/>
		<xsl:call-template name="space-list"/>
	</xsl:template>
	
	<!-- Space lists: Insert a newline, but not if this is a sub-list. -->
	<xsl:template name="space-list">
		<xsl:choose>
			<xsl:when test="ancestor::ul|ancestor::ol|ancestor::dl">
				<!-- do nothing -->
			</xsl:when>
			<xsl:otherwise>
				<xsl:text xml:space="preserve">
</xsl:text>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	
	<!-- List Item -->
	<xsl:template match="li">
		<xsl:text xml:space="preserve">
</xsl:text>
		<xsl:call-template name="item-prefix"/>
		<xsl:text xml:space="preserve"> </xsl:text>
		<xsl:apply-templates/>
	</xsl:template>
	
	<!-- Definition Term -->
	<xsl:template match="dt">
		<xsl:text xml:space="preserve">
</xsl:text>
		<xsl:call-template name="item-prefix"/>
		<xsl:text xml:space="preserve">; </xsl:text>
		<xsl:apply-templates/>
	</xsl:template>
	
	<!-- Definition Description -->
	<xsl:template match="dd">
		<xsl:text xml:space="preserve">
</xsl:text>
		<xsl:call-template name="item-prefix"/>
		<xsl:text xml:space="preserve">: </xsl:text>
		<xsl:apply-templates/>
	</xsl:template>
	
	<!-- List Item Prefixes: Prefix the line with * # ; characters. -->
	<xsl:template name="item-prefix">
		<xsl:for-each select="ancestor::*">
			<xsl:choose>
				<xsl:when test="name()='ul'">
					<xsl:text xml:space="preserve">*</xsl:text>
				</xsl:when>
				<xsl:when test="name()='ol'">
					<xsl:text xml:space="preserve">#</xsl:text>
				</xsl:when>
				<xsl:when test="name()='dt'">
					<xsl:text xml:space="preserve">;</xsl:text>
				</xsl:when>
				<xsl:when test="name()='dd'">
					<xsl:text xml:space="preserve">:</xsl:text>
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:template>




	<!-- Wiki Image -->
	<xsl:template name="wiki-image">
		<xsl:param name="href" select="substring-after(descendant::img/@longdesc, '/wiki/')"/>
		<xsl:param name="format"/>
		<xsl:param name="position">
			<xsl:choose>
				<xsl:when test="contains(@class, 'none')">
					<xsl:text xml:space="preserve">none</xsl:text>
				</xsl:when>
				<xsl:when test="contains(@class, 'right')">
					<xsl:text xml:space="preserve">right</xsl:text>
				</xsl:when>
				<xsl:when test="contains(@class, 'left')">
					<xsl:text xml:space="preserve">left</xsl:text>
				</xsl:when>
				<xsl:when test="contains(@class, 'center')">
					<xsl:text xml:space="preserve">center</xsl:text>
				</xsl:when>
			</xsl:choose>
		</xsl:param>
		<xsl:param name="width"/>
		<xsl:param name="caption">
			<xsl:choose>
				<xsl:when test="descendant::div[@class='thumbcaption']">
					<xsl:value-of select="normalize-space(descendant::div[@class='thumbcaption'])"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="descendant::img/@alt"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:param>

		<xsl:text xml:space="preserve">[[</xsl:text>
		<xsl:value-of select="$href"/>
		<xsl:if test="$format != ''">
			<xsl:text xml:space="preserve">|</xsl:text>
			<xsl:value-of select="$format"/>
		</xsl:if>
		<xsl:if test="$position != ''">
			<xsl:text xml:space="preserve">|</xsl:text>
			<xsl:value-of select="$position"/>
		</xsl:if>
		<xsl:if test="$width != '' and $width != 'px'">
			<xsl:text xml:space="preserve">|</xsl:text>
			<xsl:value-of select="$width"/>
		</xsl:if>
		<xsl:if test="$caption != ''">
			<xsl:text xml:space="preserve">|</xsl:text>
			<xsl:value-of select="$caption"/>
		</xsl:if>
		<xsl:text xml:space="preserve">]]
</xsl:text>
	</xsl:template>
	
	<!-- Framed Image -->
	<xsl:template match="div[contains(@class, 'frame')]">
		<xsl:call-template name="wiki-image">
			<xsl:with-param name="format" select="'frame'"/>
		</xsl:call-template>
	</xsl:template>
	
	<!-- Thumbnail Image -->
	<xsl:template match="div[contains(@class, 'thumb') or contains(@class, 'thumbnail')]">
		<xsl:param name="width">
			<xsl:if test="contains(@class, 'scaled')">
				<xsl:value-of select="concat(descendant::img/@width, 'px')"/>
			</xsl:if>
		</xsl:param>
		<xsl:call-template name="wiki-image">
			<xsl:with-param name="format" select="'thumb'"/>
			<xsl:with-param name="width" select="$width"/>
		</xsl:call-template>
	</xsl:template>
	
	<!-- Floated Image -->
	<xsl:template match="div[contains(@class, 'float') or contains(@class, 'center')]">
		<xsl:param name="width">
			<xsl:if test="contains(@class, 'scaled')">
				<xsl:value-of select="concat(descendant::img/@width, 'px')"/>
			</xsl:if>
		</xsl:param>
		<xsl:call-template name="wiki-image">
			<xsl:with-param name="width" select="$width"/>
		</xsl:call-template>
	</xsl:template>
	
	<!-- Linked Image -->
	<xsl:template match="a[@class='image']">
		<xsl:call-template name="wiki-image"/>
	</xsl:template>



	<!-- Link -->
	<xsl:template match="a">
		<xsl:choose>
			<!-- Ignore named links (anchors) -->
			<xsl:when test="@name">
				<!-- do nothing -->
			</xsl:when>
			<!-- Wiki Link -->
			<xsl:when test="starts-with(@href, '/wiki/')">
				<xsl:call-template name="wiki-link"/>
			</xsl:when>
			<!-- Wikipedia Link -->
			<xsl:when test="starts-with(@title, 'w:')">
				<xsl:call-template name="general-link"/>
			</xsl:when>
			<!-- Wikimedia Link -->
			<xsl:when test="starts-with(@href, 'http://upload.wikimedia.org')">
				<xsl:call-template name="media-link"/>
			</xsl:when>
			<!-- Internal Link -->
			<xsl:when test="starts-with(@href, '#')">
				<xsl:call-template name="internal-link"/>
			</xsl:when>
			<!-- External Link -->
			<xsl:when test="starts-with(@href, 'http:') or starts-with(@href, 'mailto:')">
				<xsl:call-template name="external-link"/>
			</xsl:when>
			<xsl:otherwise>
				<xsl:call-template name="external-link"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	
	<!-- Handle link pipes -->
	<xsl:template name="link-pipe">
		<xsl:param name="href"/>
		<xsl:choose>
			<xsl:when test="$href != . and @title != .">
				<xsl:text xml:space="preserve">|</xsl:text>
				<xsl:value-of select="."/>
			</xsl:when>
			<xsl:when test="@title != '' and $href != @title">
				<xsl:text xml:space="preserve">|</xsl:text>
				<xsl:value-of select="@title"/>
			</xsl:when>
		</xsl:choose>
	</xsl:template>
	
	<!-- General Link -->
	<xsl:template name="general-link">
		<xsl:text xml:space="preserve">[[</xsl:text>
		<xsl:value-of select="@title"/>
		<xsl:text xml:space="preserve">]]</xsl:text>
	</xsl:template>
	
	<!-- Wiki Link -->
	<xsl:template name="wiki-link">
		<xsl:param name="href" select="substring-after(@href, '/wiki/')"/>
		<xsl:text xml:space="preserve">[[</xsl:text>
		<xsl:value-of select="translate($href, '_', ' ')"/>
		<xsl:call-template name="link-pipe">
			<xsl:with-param name="href" select="$href"/>
		</xsl:call-template>
		<xsl:text xml:space="preserve">]]</xsl:text>
	</xsl:template>
	
	<!-- Media Link -->
	<xsl:template name="media-link">
		<xsl:text xml:space="preserve">[[Media:</xsl:text>
		<xsl:value-of select="@title"/>
		<xsl:if test="concat('Media:', @title) != . and concat('media:', @title) != .">
			<xsl:text xml:space="preserve">|</xsl:text>
			<xsl:value-of select="."/>
		</xsl:if>
		<xsl:text xml:space="preserve">]]</xsl:text>
	</xsl:template>
	
	<!-- Internal Link -->
	<xsl:template name="internal-link">
		<xsl:param name="href" select="translate(@href, '_', ' ')"/>
		<xsl:text xml:space="preserve">[[</xsl:text>
		<xsl:value-of select="$href"/>
		<xsl:call-template name="link-pipe">
			<xsl:with-param name="href" select="$href"/>
		</xsl:call-template>
		<xsl:text xml:space="preserve">]]</xsl:text>
	</xsl:template>
	
	<!-- External Link -->
	<xsl:template name="external-link">
		<xsl:choose>
			<!-- Reference style -->
			<xsl:when test="@class='external autonumber'">
				<xsl:text xml:space="preserve">[</xsl:text>
				<xsl:value-of select="@href"/>
				<xsl:text xml:space="preserve">]</xsl:text>
			</xsl:when>
			<!-- Named style -->
			<xsl:when test="@href != .">
				<xsl:text xml:space="preserve">[</xsl:text>
				<xsl:value-of select="@href"/>
				<xsl:text xml:space="preserve"> </xsl:text>
				<xsl:value-of select="."/>
				<xsl:text xml:space="preserve">]</xsl:text>
			</xsl:when>
			<!-- Named style -->
			<xsl:when test="@title != @href">
				<xsl:text xml:space="preserve">[</xsl:text>
				<xsl:value-of select="@href"/>
				<xsl:text xml:space="preserve"> </xsl:text>
				<xsl:value-of select="@title"/>
				<xsl:text xml:space="preserve">]</xsl:text>
			</xsl:when>
			<!-- Inline style -->
			<xsl:otherwise>
				<xsl:value-of select="@href"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	
	<!-- Image -->
	<xsl:template match="img">
		<xsl:choose>
			<!-- Wiki Image -->
			<xsl:when test="starts-with(@href, '/wiki/')">
				<xsl:call-template name="wiki-image"/>
			</xsl:when>
			<!-- Math Image -->
			<xsl:when test="@class='tex'">
				<xsl:call-template name="math-image"/>
			</xsl:when>
			<xsl:otherwise>
				<!-- TODO: Default case -->
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<!-- Math Image -->
	<xsl:template name="math-image">
		<xsl:text xml:space="preserve">&lt;math&gt;</xsl:text>
		<xsl:value-of select="@alt"/>
		<xsl:text xml:space="preserve">&lt;/math&gt;</xsl:text>
	</xsl:template>


	
	<!-- Table -->
	<!-- See: http://meta.wikimedia.org/wiki/Help:Table -->
	<xsl:template match="table">
		<xsl:text xml:space="preserve">
{|</xsl:text>
		<xsl:call-template name="attributes"/>
		<xsl:apply-templates/>
		<xsl:text xml:space="preserve">
|}
</xsl:text>
	</xsl:template>

	<!-- Table Caption -->
	<xsl:template match="caption">
		<xsl:text xml:space="preserve">
|+ </xsl:text>
		<xsl:apply-templates/>
	</xsl:template>

	<!-- Table Row -->
	<xsl:template match="tr">
		<xsl:text xml:space="preserve">
|-</xsl:text>
		<xsl:apply-templates/>
	</xsl:template>

	<!-- Table Cell -->
	<xsl:template match="td">
		<xsl:text xml:space="preserve">
| </xsl:text>
		<xsl:apply-templates/>
	</xsl:template>

	<!-- Table Header -->
	<xsl:template match="th">
		<xsl:text xml:space="preserve">
! </xsl:text>
		<xsl:apply-templates/>
	</xsl:template>

	
</xsl:stylesheet>