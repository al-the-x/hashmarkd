window.google && google.load('jquery'); // TODO: Figure out why Google API Loader doesn't work...

(function($){ // closure
    $(function(){
        twttr.anywhere(function(T){
            T('.screen_name, .tweet').hovercards();
        }); // END twttr.anywhere

        /**
         * Compile the reusable "pattern" first, which matches raw links that haven't
         * been rendered as an anchor tag yet.
         */
        var pattern = /(?!<a href=")http:\S+/g;

        /**
         * Replace instances of textual links within a ".tweet" with _actual_ links
         * that you can click on, ignoring the links that may already be "hovercards()".
         */
        $('.tweet').html(function(index, html){
            return html.replace(pattern, '<a href="$&" rel="external">$&</a>');
        }); // END linkify link-like text in tweets


        /**
         * Links with "rel=external" refer to documents off-site and should open
         * in a new window / tab / whatever by default.
         */
        $('a[href][rel=external]').click(function(){
            window.open(this.href);

            return false;
        }); // END click external links

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
         * This adds some magic to links that only have a hash (href="#something") and
         * a "rel" attribute. When clicked, they'll "trigger()" the event named
         * by their "rel" on the element with id matching the hash.
         */
        $('a[href^=#][rel]').click(function(){
            var $el = $(this);

            $($el.attr('href')).trigger($el.attr('rel'));

            return false;
        }); // END clicky magic

    }); // END document.ready
})(jQuery.noConflict()); // END closure
