(function($){ // closure
    $.fn.panels = function ( options )
    {
        return this.each(function(){
            $this = $(this);

            $this.is('.panels') || $this.addClass('.panels');

            $panels = $(this).children('.panel');

            $panels.filter(':not(:first)').hide();

            // TODO: Refactor to use parent as event delegate for Ajax'ed panels.
            $panels.bind('show.panels', function( event, callback ){
                var $panel = $(this);

                if ( !$panel.is(':visible') )
                {
                    $panel.siblings('.panel').trigger(
                        'hide.panels', [ function(){ 
                            // TODO: Different animation... Configurable?
                            $panel.fadeIn(callback);
                        } ]
                    );
                }
            }); // END bind show.panels

            // TODO: Refactor to use parent as event delegate for Ajax'ed panels.
            $panels.bind('hide.panels', function( event, callback ){
                var $panel = $(this);

                if ( $panel.is(':visible') )
                {
                    // TODO: Different animation... Configurable?
                    $panel.fadeOut(callback);
                }
            }); // END bind hide.panels
        }); // END each
    } // END panels plugin
})(jQuery); // END closure
