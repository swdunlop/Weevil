function get_selection( ){
    if( window.getSelection ) return ''+window.getSelection();
    if( document.getSelection ) return ''+document.getSelection();
    if( document.selection ) return ''+document.selection.createRange().text;
};

function set_location( url ){
    document.location.href = url;
}

function ascend_location( ){
    var href = document.location.href;
    href = href.replace( /[/][^/]*[/]?$/, "" );
    if( href.split( "/" ).length > 3 ){
        document.location.href = href;
    }
}

function submit_search( data ){
    var href = document.location.href;
    href = href.replace( /[?].*$/, "" );

    if( document.view_type == 'dir' ){
        set_location( href + "?q=" + encodeURI( data ) );
    }else{
        set_location( "/c?q=" + encodeURI( data ) );
    }
}

function popup_search( ){
    search_dialog.dialog( 'open' )
    $( '#term' ).focus()
}

shortcuts = {
    47 : function( ){ // "/"
        var sel = get_selection( )
        if( sel ) return submit_search( sel )
        return popup_search( )
    }, 
    63 : function( ){ // "/"
        var sel = get_selection( )
        if( sel ) return submit_search( sel )
        return popup_search( )
    }, 
    46 : function( ){ // "."
        ascend_location( )
    }
}

$(function(){
    search_dialog = $('<div title="Search Files.."></div>').html(
        '<input id="term" class="dialog-input"></input>'
    ).dialog({ 'autoOpen' : false, 'buttons' : {
        'Search' : function( ){ submit_search( $('#term').val() ) }
    } })

    $(document).keypress( function( e ){ 
        var t = $(e.target)
        if( $(e.target).is( 'input' ) ) return true
        var c = e.keyCode || e.charCode
        fn = shortcuts[c]
        if( fn ){ fn(); return false }
        return true
    } )

    $( '#term' ).keypress( function( e ){
        if( e.keyCode != 13 ) return true;
        submit_search( $('#term').val() );
        return false;
    } );
})

