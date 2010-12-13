#!/usr/bin/env python
### Copyright (C) 2010 Scott W. Dunlop <swdunlop at gmail.com>
### 
### This program is free software; you can redistribute it and/or
### modify it under the terms of the GNU General Public License
### as published by the Free Software Foundation, version 2
### of the License.
### 
### This program is distributed in the hope that it will be useful,
### but WITHOUT ANY WARRANTY; without even the implied warranty of
### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
### GNU General Public License for more details.
### 
### You should have received a copy of the GNU General Public License
### along with this program; if not, write to the Free Software
### Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
### USA.

'''
nolex is an allergic reaction to pygments and other syntax highlighters that
get entirely too deep in the syntax of the file to be reliable and
understandable.  nolex serves the needs of weevil to hunt down non-keyword
symbols for the purposes of correlation, then gets out of the way.
'''

### TODO: make parsers composable, such as css or js within html.
### TODO: separate parser from formatter, so token seqs can be indexed.

import sys, re, cgi, os.path, codecs
from StringIO import StringIO

### These two globals are used for handling embedded strings.
rx_string = re.compile( '(["\'])(\\\\\\1|\\\\\\\\|.)*?\\1' )
def fmt_string( m ):
    c = m.group(1)
    d = m.group(0)[1:-1]
    return '%s<span class="str">%s</span>%s' % ( c, cgi.escape( d ), c )

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
def tag( lang, str ):
    return lang.tag( str )

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
                tok = m.group( 0 ) #cgi.escape( m.group( 0 ) ) 
                # NOTE: This should be done before parsing.
                tok = tok.replace( '\t', '        ' )
                tok.replace( ' ', '&nbsp;' )
                out.write( unicode( f( self, tok ) ) )
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
        str = cgi.escape( str )
        return '<span class="cmt">%s</span>' % ( str, )
    
    def keyword( self, str ):
        str = cgi.escape( str )
        return '<span class="kw">%s</span>' % ( str, )

    def symbol( self, str ):
        str = cgi.escape( str, True ) #Yes, we need to escape quotes.
        if str in self.keywords:
            return self.keyword( str )
        else:
            return '<a class="sym x-%s">%s</a>' % ( str, str ) 

    def eol( self, str ):
        return '\n' 

    def preproc( self, str ):
        str = cgi.escape( str )
        return str

    def string( self, str ):
        c = str[0]
        str = cgi.escape( str[1:-1] )
        #TODO: Looks a little ugly in Python with triple-quotes.
        return '%s<span class="str">%s</span>%s' % ( c, str, c )

    def tag( self, str ):
        if str[1] == '/':
            return '&lt;/<span class="kw">%s</span>&gt;' % (
                cgi.escape( str[2:-1] ),
            )

        str = str[1:-1]
        pts = str.split( None, 1 )
        
        if len( pts ) == 1:
            return '&lt;<span class="kw">%s</span>&gt;' % (
                cgi.escape( str ),
            )
        else:
            return '&lt;<span class="kw">%s</span> %s&gt;' % (
                cgi.escape( pts[0] ), rx_string.sub( fmt_string, pts[1] )
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
        ( symbol,  '[a-zA-Z_][a-zA-Z0-9_]*' ),
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

class xml_lang( lang ):
    RULES = (
        ( comment, '<!-- -->' ),
        ( comment, '<!.+?>' ),
        ( string,  '<[CDATA[.*?]]>' ),
        ( tag,     ( 
            '<('
            '([^>]+?)|'
            '("[^"]+?")|'
            "('[^']+?')"
            ')*?>'
        ) )
    )
    KEYWORDS = []
    
class cxx_lang( c_lang ):
    KEYWORDS = (
        # ANSI C++
        "asm", "delete", "goto", "return", "typedef",
        "auto", "do", "if", "short", "typeid",
        "bad_cast", "double", "inline", "signed", "typename",
        "bad_typeid", "dynamic_cast", "int", "sizeof", "union",
        "bool", "else", "long", "static", "unsigned",
        "break", "enum", "mutable", "static_cast", "using",
        "case", "except", "namespace", "struct", "virtual",
        "catch", "explicit", "new", "switch", "void",
        "char", "extern", "operator", "template", "volatile",
        "class", "false", "private", "this", "while",
        "const", "finally", "protected", "throw", 
        "const_cast", "float", "public", "true", 
        "continue", "for", "register", "try"
        "default", "friend", "reinterpret_cast", "type_info",
    )

class java_lang( c_lang ):
    RULES = (
        ( comment, '//[^\r\n]*' ),
        ( comment, '/\\*.*?\\*/' ),
        ( string,  '"(\\\\\\\\|\\\\"|.)*?"' ),
        ( string,  "'(\\\\\\\\|\\\\'|.)*?'" ),
        ( symbol,  '[a-zA-Z_][a-zA-Z0-9_]*' ),
        ( eol,     '\r?\n' ),
    )
    
    # As per Wikipedia, 2010/12/11
    KEYWORDS = (
       "abstract", "assert", "boolean", "break", "byte", "case", "catch",
       "char", "class", "const", "continue", "default", "do", "double",
       "else", "enum", "extends", "final", "finally", "float", "for", "if",
       "goto", "implements", "import", "instanceof", "int", "interface",
       "long", "native", "new", "package", "private", "protected", "public",
       "return", "short", "static", "strictfp", "super", "switch",
       "synchronized", "this", "throw", "throws", "transient", "try", "void",
       "volatile", "while",
    )

class cs_lang( c_lang ):
    RULES = (
        ( comment, '//[^\r\n]*' ),
        ( comment, '/\\*.*?\\*/' ),
        ( string,  '"(\\\\\\\\|\\\\"|.)*?"' ),
        ( string,  "'(\\\\\\\\|\\\\'|.)*?'" ),
        ( symbol,  '[a-zA-Z_][a-zA-Z0-9_]*' ),
        ( eol,     '\r?\n' ),
    )
    
    # As per Wikipedia, 2010/12/11
    KEYWORDS = (
        "abstract", "event", "new", "struct", "assert", "explicit", "null",
        "switch", "base", "extern", "object", "this", "boolean", "false",
        "operator", "throw", "break", "finally", "out", "true", "byte",
        "fixed", "override", "try", "case", "float", "params", "typeof",
        "catch", "for", "private", "uint", "char", "foreach", "protected",
        "ulong", "checked", "goto", "public", "unchecked", "class", "if",
        "readonly", "unsafe", "const", "implicit", "ref", "ushort", "continue",
        "in", "return", "using", "decimal", "int", "sbyte", "virtual",
        "default", "interface", "sealed", "volatile", "delegate", "internal",
        "short", "void", "double", "issizeof", "while", "double", "issizeof",
        "while", "lock", "stackalloc ", "else", "long", "static ", "enum",
        "name", "space", "string",
    )

class ecma_lang( java_lang ):
    # Don't call it JavaScript..
    #TODO: Support regex literals.
    
    # As per Wikipedia, 2010/12/11
    KEYWORDS = (
        "break", "else", "new", "var", "case", "finally", "return", 
        "void", "catch", "for", "switch", "while", "continue", "function", 
        "this", "with", "default", "if", "throw", "delete", "in", "try", 
        "do", "instanceof", "typeof"
    )

class py_lang( lang ):
    RULES = (
        ( comment, '#[^\r\n]+?\r?\n' ),
        ( string,  "'''(\\\\\\\\|\\\\'|.)*?'''" ),
        ( string,  '"""(\\\\\\\\|\\\\"|.)*?"""' ),
        ( string,  '"(\\\\\\\\|\\\\"|.)*?"' ),
        ( string,  "'(\\\\\\\\|\\\\'|.)*?'" ),
        ( symbol,  '[$a-zA-Z_][$a-zA-Z0-9_]*' ),
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
    if not ext.startswith( '.' ): ext = '.' + ext
    return BY_EXT.get( ext.lower( ), default )( )

def by_mime( mime, default = text ):
    return BY_MIME.get( mime.lower( ), default )( )

register_ext( c_lang, 'c', 'h' )
register_ext( cxx_lang, 'cc', 'cpp', 'hpp', 'cxx' )
register_ext( cs_lang, 'cs' )
register_ext( py_lang, 'py' )
register_ext( java_lang, 'java' )
register_ext( ecma_lang, 'js' )
register_ext( xml_lang, 'xml', 'html', 'xhtml', 'aspx', 'htm' )

def open_file( path ):
    return codecs.open( 
        path, 'r', encoding='utf-8', errors='ignore' 
    )

def parse_file( path ):
    return by_ext( os.path.splitext( path )[-1] ).parse( open( path ).read( ) )

if __name__ == '__main__':
    print parse_file( sys.argv[1] )

