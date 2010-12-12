#!/usr/bin/env python

import sys, re, cgi, os.path
from cStringIO import StringIO

def comment( lang, str ): 
    return lang.comment( str )
def symbol( lang, str ): 
    return lang.symbol( str )
def eol( lang, str ): 
    return lang.eol( str )
def preproc( lang, str ): 
    return lang.preproc( str )
def string( lang, str ): 
    return lang.string( str )
def space( lang, str ):
    return lang.space( str )

class lang:
    RULES = []
    KEYWORDS = [] 
    FLAGS = re.S | re.M 

    def __init__( self ):
        self.rules = map( self.compile_rule, self.RULES )
        self.keywords = set( map( cgi.escape, self.KEYWORDS ) )

    def parse( self, src ):
        out = StringIO( )

        ofs = 0; end = len( src )
        rules = self.rules
        while ofs < end:
            skip = True

            for f, p in rules:
                m = p.match( src, ofs )
                if not m: continue
                tok = cgi.escape( m.group( 0 ) ) 
                # NOTE: This should be done before parsing.
                tok = tok.replace( '\t', '        ' )
                tok.replace( ' ', '&nbsp;' )
                out.write( f( self, tok ) )
                ofs = m.end( )
                skip = False
                break
            
            if skip:
                out.write( cgi.escape( src[ofs] ) )
                ofs += 1
        
        return out.getvalue( )

    def compile_rule( self, rule ):
        return rule[0], re.compile( rule[ 1 ], self.FLAGS )
    
    def comment( self, str ):
        return '<span class="cmt">%s</span>' % ( str, )
    
    def keyword( self, str ):
        return '<span class="kw">%s</span>' % ( str, )

    def symbol( self, str ):
        if str in self.keywords:
            return self.keyword( str )
        else:
            return '<a class="sym x-%s">%s</a>' % ( str, str ) 

    def eol( self, str ):
        return '\n' 

    def preproc( self, str ):
        return str

    def string( self, str ):
        return '%s<span class="str">%s</span>%s' % (
            str[0], str[1:-1], str[-1]
        )

class text( lang ):
    RULES = (
        ( preproc, '^[^\r\n]+' ),
        ( eol,     '\r?\n' ),
    )

class c_lang( lang ):
    RULES = (
        ( comment, '//[^\r\n]*' ),
        ( comment, '/\\*.*?\\*/' ),
        ( string,  '"(\\\\\\\\|\\\\"|.)*?"' ),
        ( string,  "'(\\\\\\\\|\\\\'|.)*?'" ),
        ( symbol,  '[a-zA-Z_][a-zA-Z0-9_]+' ),
        ( eol,     '\r?\n' ),
        ( preproc, '^#[^\r\n]*' ),
    )

    KEYWORDS = (
        # C89 / C90
        "auto", "break", "case", "char", "const", "continue", "default", "do",
        "double", "else", "enum", "extern", "float", "for", "goto", "if", 
        "int", "long", "register", "return", "short", "signed", "sizeof", 
        "static", "struct", "switch", "typedef", "union", "unsigned", "void",
        "volatile", "while",

        # C99 
        "_Bool", "_Complex", "_Imaginary", "inline", "restrict",
        
        # Common Compiler-Specific Keywords (Mostly calling convention)
        "asm", "cdecl", "far", "fortran", "huge", "interrupt", "near", 
        "pascal", "typeof"
    )

class py_lang( lang ):
    RULES = (
        ( comment, '#[^\r\n]+?\r?\n' ),
        ( string,  "'''(\\\\\\\\|\\\\'|.)*?'''" ),
        ( string,  '"""(\\\\\\\\|\\\\"|.)*?"""' ),
        ( string,  '"(\\\\\\\\|\\\\"|.)*?"' ),
        ( string,  "'(\\\\\\\\|\\\\'|.)*?'" ),
        ( symbol,  '[a-zA-Z_][a-zA-Z0-9_]+' ),
        ( eol,     '\r?\n' ),
    )

    KEYWORDS = (
        # As of Python 2.7
        'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
        'elif', 'else', 'except', 'exec', 'finally', 'for', 'from', 'global',
        'if', 'import', 'in', 'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'with', 'yield'
    )
    
BY_EXT = {}
BY_MIME = {}

def register_ext( lang, *exts ):
    for ext in exts:
        if not ext.startswith( '.' ): ext = '.' + ext
        ext = ext.lower( )
        BY_EXT[ ext ] = lang

def register_mime( lang, *mimes ):
    for mime in mimes:
        BY_MIME[mime.lower( )] = lang

def by_ext( ext, default = text ):
    return BY_EXT.get( ext.lower( ), default )( )

def by_mime( mime, default = text ):
    return BY_MIME.get( mime.lower( ), default )( )

register_ext( c_lang, 'c', 'h', 'cc', 'cpp', 'hpp', 'cxx' )
register_ext( py_lang, 'py' )

def parse_file( path ):
    return by_ext( os.path.splitext( path )[-1] ).parse( open( path ).read( ) )

js = ''' <script src='https://ajax.googleapis.com/ajax/libs/jquery/1.4.4/jquery.min.js'></script><script>$( function( ){

    function mouseover_sym( evt ){
        var sym = $( evt.target ).text( )
        console.log( "Mouse Enter: " + sym )
        console.log( $( ".x-" + sym ).addClass( "mark" ) )
    };

    function mouseleave_sym( evt ){
        var sym = $( evt.target ).text( )
        console.log( "Mouse Leave: " + sym )
        console.log( $( ".x-" + sym ).removeClass( "mark" ) )
    };

    $( ".sym" ).mouseover( mouseover_sym ).mouseleave( mouseleave_sym )
    
} )
</script>'''

css = '''<style>
body {
    color: #000;
    background: #FFF;
}
pre {
    font-family: "droid sans mono", "andale mono", "bitstream vera sans mono", "lucida console", "courier new" !important;
}
.sym {
}
.mark {
    text-decoration: underline;
    background-color: #DDD;
}
.kw {
    font-weight: bold;
}
.cmt {
    font-style: italic;
}
.str {
    color: #484800;
}
</style>'''

if __name__ == '__main__':
    data = parse_file( sys.argv[1] )
    out = open( sys.argv[1] + '.html', 'w' )
    out.write( '<html><head>' + js + css + '</head><pre>' )
    out.write( data )
    out.write( '</pre></html>' )

