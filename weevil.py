#!/usr/bin/env python
### Copyright (C) 2010 IOActive, Inc.
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


#TODO: Soft-wrap plugin.
#TODO: On keypress "'" in a file, open nearest file with that name.
#TODO: Highlighting a token causes shadows on identical tokens throughout.
#TODO: Nearest is defined as "ascend, then recursively ascend."
#TODO: "?" tab leads to shortcut bar.

import os, os.path, cgi, re, codecs
import bottle, nolex

#################################################################### Shared Data
_setup_complete = False

if not _setup_complete:
    _setup_complete = True
    
    WEEVIL_ROOT = os.path.abspath( os.path.dirname( __file__ ) )
    STATIC_ROOT = os.path.join( WEEVIL_ROOT, 'static' )
    bottle.TEMPLATE_PATH.append( os.path.join( WEEVIL_ROOT, 'views' ) )
    
    try:
        import magic
    except:
        magic = None

### Nomenclature:
### - a Req is the portion of the url after /s/ up to the query or fragment.
### - Req's are separated by forward slashes.
### - a Path is the path to a file referenced by application.
### - Path's are split by /'s

########################################################## Underlying Functions
def req_to_path( req ):
    root = os.getcwd( ) 
    path = os.path.abspath( '.' + os.sep + req.replace( '/', os.sep ) )
    if path == root: 
        return path
    elif not path.startswith( root + os.sep ):
        bottle.abort( 403, 'You younguns stay off my lawn.' )
    elif not os.path.exists( path ):
        bottle.abort( 404, 'Looks like someone stole your file.' )
    return path

def path_to_req( path ):
    return os.path.relpath( path ).replace( os.sep, '/' )

def gen_breadcrumbs( req ):
    ref = '/c'
    yield ('.', '/c')
    for part in req.split( '/' ):
        if part:
            ref += '/' + part
            yield (part, ref)

def gen_title( req ):
    links = ( gen_link( p, l ) for l, p in gen_breadcrumbs( req ) )
    return '<h2>%s</h2>' % '/'.join( links )

def gen_link( req , label ):
    return '<a href="%s">%s</a>' % (
        cgi.escape( req, True ), cgi.escape( label, True )
    )        

def gen_req_link( req, frag = None ):
    if req[0] != '/': req = '/' + req

    item = req.rsplit( '/', 1 )[1]
    path = req_to_path( req )

    if os.path.isdir( path ):
        label = item + '/'
    else:
        label = item
    
    if frag is not None:
        req = req + '#' + frag
        
    return gen_link( '/c' + req, label )

def gen_match_row( path, lineno, line, start, end ):
    #TODO: highlight the start and end.
    #TODO: syntax highlight the line?
    req = path_to_req( path )
    return '<tr><td>%s:%s</td><td>%s</td><tr>' % (
        gen_req_link( req, str( lineno ) ), lineno, cgi.escape( line.strip() )
    )

def iter_src_files( path, excl=None ):
    if excl is None: excl = set()

    if path in excl: return
    excl.add( path )
    try:
        items = os.listdir( path )
        items.sort( )
    except:
        return

    for item in items:
        item_path = os.path.join( path, item )
        if item.startswith( '.' ):
            pass
        elif os.path.isdir( item_path ):
            for subitem in iter_src_files( item_path, excl ):
                yield subitem
        elif not os.path.isfile( item_path ):
            pass
        else:
            #TODO: Exclude binary files.
            yield item_path

def is_text( path ):
    # Hoo boy, here we go..

    # We lack magic, good luck, user!
    if magic is None: return True
    
    if path.endswith( ".wod" ):
        return True

    type = magic.from_file( path, mime=True )
    return type.lower().startswith( "text/" )

def open_file( path ):
    return codecs.open( 
        path, 'r', encoding='utf-8', errors='ignore' 
    )

def iter_file_matches( rx, path ):
    if not is_text( path ): return

    try:
        data = open_file( path )
    except:
        return
    
    lineno = 0
    for line in data.readlines():
        lineno += 1
        m = rx.search( line )
        if m:
            yield path, lineno, line, m.start(), m.end()

def iter_tree_matches( rx, path ):
    for path in iter_src_files( path ):
        for match in iter_file_matches( rx, path ):
            yield match

################################################################## HTTP Services
@bottle.route( '/' )
@bottle.route( '/c' )
def redirect_root( ):
    return view_source( '' )

@bottle.route( '/favicon.ico' )
def fucking_favicons( ):
    bottle.abort( 404, 'Stop discriminating against hackers without artistry.' )

@bottle.route( '/c/:req#.*#' )
def view_source( req ):
    path = req_to_path( req )
    expr = bottle.request.GET.get('q')
    if expr: return search_tree( req, path, expr )

    if os.path.isdir( path ): return view_dir( req, path )
    if os.path.isfile( path ): return view_file( req, path )

def view_dir( req, path ):
    items = list(x for x in os.listdir( path ) if not x.startswith( '.' ))
    items.sort( )

    if not req.endswith( '/' ): req += '/'
    path += os.sep
    
    #TODO: This is somewhat inefficient; we should collapse this to a single
    #      iteration and list.

    file_items = list( x for x in items if os.path.isfile( path + x ) )
    dir_items = list( x for x in items if os.path.isdir( path + x ) )
    
    #TODO: Prioritize directories
    dir_entries = list(gen_req_link( req + x ) for x in dir_items)
    file_entries = list(gen_req_link( req + x ) for x in file_items)
    entries = dir_entries + file_entries
    if not req.startswith( '/' ): req = '/' + req
    crumbs = gen_title( req )
    return bottle.template( 'view_dir', crumbs=crumbs, path=req, entries=entries )

from cStringIO import StringIO

def gen_linenos( data ):
    ct = data.count( '\n' )
    out = StringIO( )
    for i in range( 1, ct+1 ):
        out.write( '<a name="%s">%5s</a>\n' % ( i, i ) )
    return out.getvalue( )

def view_file( req, path ):
    ext = os.path.splitext( path )[-1]

    try:
        data = codecs.open( 
            path, 'r', encoding='utf-8', errors='ignore' 
        ).read( )
    except:
        bottle.abort( 
            403, 'Inscrutable file must contain secret herbs and spices.' 
        )
    
    result = nolex.by_ext( ext ).parse( data )

    crumbs = gen_title( req )
    return bottle.template( 
        'view_file', crumbs=crumbs, path=req, nos=gen_linenos( result ),       
        data=result 
    )

def search_tree( req, path, expr ):
    if not expr:
        bottle.abort( 403, 'Less monkeys, more typewriters?' )
    #TODO: Give a better error response for bogus regex.
    rx = re.compile( expr, re.IGNORECASE )
    rows = ( gen_match_row( *x ) for x in iter_tree_matches( rx, path ) )
    title = "Search for " + expr #Titles quote in the view.
    return bottle.template( 'search_tree', rows=rows, title=title )

@bottle.route( '/s/:req#.*#' )
def fetch_static( req ):
    return bottle.send_file( req, STATIC_ROOT )

##################################################################### Boot Logic

if __name__ == '__main__':
    import sys
    if sys.argv[1:]:
        print 'USAGE: weevil'
        print 
        print 'Provides a source code navigation view of the current directory.'
    else: 
        print 'Starting server.'
        bottle.debug( True )
        bottle.run( reloader = True, port=1982, host = '127.0.0.1' )

