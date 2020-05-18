from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter, QTextCursor, QTextBlockFormat

base_font = 12

def format(color, style='', size=base_font):

    _color = QColor(color)
    _format = QTextCharFormat()
    _format.setForeground(_color)

    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)
    
    _format.setFontPointSize(size)
    return _format


STYLES = {
    'heading1': format('#E06C75', 'bold', base_font * 2),
    'heading2': format('#E06C75', 'bold', base_font * 1.5),
    'heading3': format('#E06C75', 'bold', base_font * 1.17),
    'heading4': format('#E06C75', 'bold', base_font),
    'heading5': format('#E06C75', 'bold', base_font * .83),
    'heading6': format('#E06C75', 'bold', base_font * .67),

    'emphasis': format('#BC78DD', 'italic'),
    'strong': format('#D19A66', 'bold'),
    'link': format('#61AFE9'),
    'image': format('#2B65D1'),

    'code': format('grey'),

}


class MardownHighlighter (QSyntaxHighlighter):


    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        self.tri_single = (QRegExp("```"), 1, STYLES['code'])


        rules = [
            (r'\[(.+)\]\(([^ ]+)( "(.+)")?\)', 0, STYLES['link']),
            (r'\!\[(.+)\]\(([^ ]+)( "(.+)")?\)', 0, STYLES['image']),

            (r'^#[^\n]*', 0, STYLES['heading1']),
            (r'^##[^\n]*', 0, STYLES['heading2']),
            (r'^###[^\n]*', 0, STYLES['heading3']),
            (r'^####[^\n]*', 0, STYLES['heading4']),
            (r'^#####[^\n]*', 0, STYLES['heading5']),
            (r'^######[^\n]*', 0, STYLES['heading6']),

            (r'(\*)([^\*]+)\1', 0, STYLES['emphasis']),
            (r'(\*{2})([^\*\*]+)\1', 0, STYLES['strong']),


            (r'`[^`]*`', 0, STYLES['code']),
            (r'^((?:(?:[ ]{4}|\t).*(\R|$))+)', 0, STYLES['code']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
            for (pat, index, fmt) in rules]


    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text."""
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        self.match_multiline(text, *self.tri_single)


    def match_multiline(self, text, delimiter, in_state, style):
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        if self.currentBlockState() == in_state:
            return True
        else:
            return False