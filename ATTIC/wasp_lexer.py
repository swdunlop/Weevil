import pygments.lexers.functional

__all__ = ['SchemeLexer']

class WaspLexer( pygments.lexers.functional.SchemeLexer ): 
    name = 'Wasp Lisp'
    aliases = ['waspvm', 'wasp']
    filenames = ['*.ms']
    mimetypes = ['text/x-wasp']
    keywords = [] #TODO: Buh?
    builtins = [
        'let', 'set!', 'deflet', 'define', '?', 'function', 'lambda',
        'define-record-type', 'export', 'guard', 'case', 'cond',
        'begin', 'else', 'when', 'unless', 'while', 'until', 'forever',
        'or', 'and', 'if', 'return', 'quote', 'quasiquote', 'apply',
        'import', 'module', 's:', 'r:', 't:'
    ]

