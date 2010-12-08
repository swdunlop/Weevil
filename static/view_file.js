$( function( ) {
    document.view_type = 'file' // Consumed by core.
    if( location.href.search( '#' ) != -1 ){
        $( ".linenodiv > pre" ).html(
            $( ".linenodiv > pre" ).html( ).split( "\n" ).map( function( no ){
                return "<a name='" + no.trim( ) + "'>" + no + "</a>"
            } ).join( "\n" )
        )
        
        // Side effects of assignment, anyone?
        location.href = location.href
    }
} )

