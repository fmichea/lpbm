$(document).ready(function () {
    $('.article-contents > .panel-body > p').each(function () {
        // Images not wrapped in a link are wrapped into a link to themselves.
        $('> img', this).wrap(function () {
            return '<a href="' + $(this).attr('src') + '"></a>';
        });

        imgs = $('> a > img', this);

        // No image? ... done for this paragraph.
        if (imgs.length == 0)
            return;

        // Now all images in a link are wrapped in a thumbnail, and given a
        // tooltip.
        imgs.each(function () {
            link = $(this).parent();
            addTooltip = function (text) {
                link.attr('title', text);
                link.tooltip({'delay': {'show': 500, 'hide': 100},
                              'placement': 'top'});
            };

            src = $(this).attr('src');
            href = link.attr('href');

            if (href == src) {
                addTooltip("click to see in full size");
            } else if (href.slice(-4) == '.gif' &&
                       src.slice(0, href.length - 4) == href.slice(0, -4)) {
                addTooltip("click to see annimated");
            }
        });

        sizes = [0, 6, 5, 4];
        offsets = [0, 3, 1, 0];

        sizeSelector = imgs.length;
        if (3 < sizeSelector)
            sizeSelector = 2;

        imgs.each(function () {
            img = $(this);
            $(this).parent().wrap(function () {
                return '<div class="col-md-' + sizes[sizeSelector] + '">'
                  + '<div class="thumbnail"></div></div>';
            });
            $(this).parent().parent().append(function () {
                return '<div class="caption text-center"><h4>'
                  + img.attr('alt') + '</h4></div>';
            });
        });

        offsetClass = 'col-md-offset-' + offsets[sizeSelector];
        if (imgs.length <= 3) {
            $(this)[0].classList.add('row');
            if (offsets[imgs.length]) {
                $('> div:first', this)[0].classList.add(offsetClass);
            }
        } else {
            $('> div:even', this).each(function () {
                console.log($(this)[0]);
                $(this)[0].classList.add(offsetClass);
                friend = $(this)[0].nextSibling;
                console.log(friend);
                $(this).wrap('<div class="row"></div>');
                if (friend != null)
                    $(friend.nextElementSibling).appendTo($(this).parent());
            });
        }
        imgs.each(function () {
            width = $(this).parent().parent().width();
            $(this).css('max-height', width - 150);
        });
    });

    $('.codehilitetable').wrap(''
        + '<div class="row"><div class="col-md-10 col-md-offset-1">'
        + '</div></div>');
    $('.codehilitetable .linenos').css('width', function () {
        return $(this).width() + 2;
    });
    $('.codehilitetable').css('width', '100%');

    $('#backToTopButton').click(function () {
        $(window).scrollTop(0);
    });

    $('.lpbm-collapser-button').click(function () {
      $('> .lpbm-collapser-button-elapse', this).toggle();
      $('> .lpbm-collapser-button-collapse', this).toggle();
      $('> .lpbm-collapser-body', $(this).parent().parent()).toggle();
    });
});
