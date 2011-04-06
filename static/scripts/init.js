window.google && google.load('jquery'); // TODO: Figure out why Google API Loader doesn't work...

(function($){ // closure
    $(function(){
        twttr.anywhere(function(T){
            // T('#auth').connectButton(); // Skpped for now...
            T('.screen_name').hovercards();
        }); // END twttr.anywhere

        //$('ul.panels').panels(); // Not used for now... Need better animation.

        /**
         * This adds some magic to any <input> element that has a "title" attribute
         * and no current value. The "title" text will act as the "value" until
         * the user clicks or tabs to it, but that value won't get submitted.
         */
        $('input[value=][title]').each(function(){
            var $input = $(this);

            var title = $input.attr('title');

            $input.focus(function(){
                if ( $input.val() == title ) $input.val('');
            }).blur(function(){
                if ( !$input.val() ) $input.val(title);
            }).blur(); // Initial trigger...

            $input.closest('form').submit(function(){
                if ( $input.val() == title ) $input.val('');
            });
        }); // END each empty input with a title

        /**
         * This adds some magic to links that only have a hash (href="#") and
         * a "rel" attribute. When clicked, they'll "trigger()" the event named
         * by their "rel" on the element with id matching their hash.
         */
        $('a[href^=#][rel]').click(function(){
            var $this = $(this);

            $($this.attr('href')).trigger($this.attr('rel'));

            return false;
        }); // END clicky magic

    }); // END document.ready
})(jQuery.noConflict()); // END closure
