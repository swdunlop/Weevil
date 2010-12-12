from pygments.lexer import RegexLexer, include, bygroups, using
from pygments.token import *

__all__ = ['DdxLexer']

class DdxLexer( RegexLexer ):
    """
    For DeDex Disassembly.
    """
    name = 'DDX'
    aliases = ['ddx']
    filenames = ['*.ddx']
    mimetypes = ['text/x-ddx']


            # invoke-virtual
            # invoke-static
            # invoke-direct
            # return-void
            # new-instance
            # move-result-object
            # if-eqz
            # new-instance
            # const-string
    #: optional Comment or Whitespace
    string = r'"[^"]*?"'
    identifier = r'([-a-zA-Z$._/<>][-a-zA-Z$._/0-9<>]*|' + string + ')'
    number = r'(?:0[xX][a-zA-Z0-9]+|\d+)'
    hexn = r'(?:0[xX][0-9a-fA-F]+|$0[0-9a-fA-F]*|[0-9]+[0-9a-fA-F]*h)'
    decn = r'[0-9]+'
    register = (r'(?:v[0-9,v]+)|(?:[{]v[0-9,v]+[}])')

    tokens = {
        'root':[
            include('whitespace'),
            (hexn + ':', Name.Label),
            (r'\..*?$', Comment.Preproc),
            (identifier, Name.Function, 'operands'),
            (r'[\r\n]+', Text)
        ],

        'operands': [
            (string, String),
            (hexn, Number.Hex),
            (decn, Number.Integer),
            (register, Name.Label),
            (identifier, Name.Variable),
            
            include('punctuation'),
            include('whitespace')
        ],

        'whitespace': [
            (r'\n', Text),
            (r'\s+', Text),
            (r';.*?\n', Comment)
        ],

        'punctuation': [
            (r'[,]+', Punctuation)
        ]
    }

    def analyse_text(text):
        return re.match(r'^\.\w+', text, re.M)

