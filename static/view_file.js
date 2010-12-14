$( function( ) {
    document.view_type = 'file' // Consumed by core.
   /* 
    if( location.href.search( '#' ) != -1 ){
        $( ".linenodiv > pre" ).html(
            $( ".linenodiv > pre" ).html( ).split( "\n" ).map( function( no ){
                return "<a name='" + no.trim( ) + "'>" + no + "</a>"
            } ).join( "\n" )
        )
        
        // Side effects of assignment, anyone?
        location.href = location.href
    }
   */ 
    function mouseover_sym( evt ){
        var sym = $( evt.target ).attr( 'class' ).split( ' ' )[1]
        $( "." + sym ).addClass( "mark" )
    };

    function mouseleave_sym( evt ){
        var sym = $( evt.target ).attr( 'class' ).split( ' ' )[1]
        $( "." + sym ).removeClass( "mark" )
    };

    $( ".sym" ).mouseover( mouseover_sym ).mouseleave( mouseleave_sym )
} )

