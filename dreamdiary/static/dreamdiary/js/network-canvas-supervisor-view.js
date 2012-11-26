// Initialize learning network plugin
$(function() { $.fn.networkCanvas(); });

(function($) {

    $.fn.networkCanvas = function(options) {
    
        var opts = $.extend({}, $.fn.networkCanvas.defaults, options);

        // Define canvas selectors
        var sel_canvas = opts.canvas[0] + opts.canvas[1],
            sel_canvasContainer = opts.canvasContainer[0] + opts.canvasContainer[1],
            sel_canvasHandle = opts.canvasHandle[0] + opts.canvasHandle[1],
            sel_itemContainer = opts.itemContainer[0] + opts.itemContainer[1],
            sel_item = opts.item[0] + opts.item[1],
            sel_connector = opts.itemConnector[0] + opts.itemConnector[1];

    // INIT

        if (options === 'center') {
            centerScreen();
        } else {
            alignItems();
            centerScreen();
            mouseEvents();
            canvasDraggable();
        }

    // MAIN FUNCTIONS (PRIVATE)

        function alignItems() {

            // Check if there are any items on canvas
            if ($(sel_itemContainer).length) {

                // Position all the existing active items and connectors correctly
                $(sel_itemContainer + ',' + sel_connector).each(function (i) {

                    var itemWidth = $(sel_canvas).width(),
                        itemHeight = $(sel_canvas).height(),
                        canvasItemDistH = Math.round(opts.itemDistance + $(sel_canvas).outerWidth()),
                        canvasItemDistV = Math.round(opts.itemDistance + $(sel_canvas).outerHeight()),
                        connectorLengthH = Math.round(canvasItemDistH - $(sel_canvas).outerWidth() - (opts.connectorMargin * 2)),
                        connectorLengthV = Math.round(canvasItemDistV - $(sel_canvas).outerHeight() - (opts.connectorMargin * 2)),
                        leftVal, topVal;

                    // If data-coord attribute exists and the coordinates are numbers            
                    if ($(this).attr('data-coord') && !isNaN($(this).attr('data-coord').split('_')[0]) && !isNaN($(this).attr('data-coord').split('_')[1])) {

                        // Get x and y coordinates from the data-coord attribute
                        var posX = parseInt($(this).attr('data-coord').split('_')[0]),
                            posY = parseInt($(this).attr('data-coord').split('_')[1]);

                        // Calculate the left and top values from the coordinates
                        if ($(this).hasClass(opts.itemConnector[1]) && $(this).hasClass('vertical')) {

                            // Set height and width
                            $(this).css({'height':connectorLengthV, 'width':opts.connectorWidth});

                            // Calculate correct left and top values
                            leftVal = (posX * (opts.itemDistance + itemWidth)) + ((itemWidth - $(this).outerWidth(true)) / 2);
                            if (posY < 0) {
                                topVal = (posY * (opts.itemDistance + itemHeight)) + itemHeight + opts.connectorMargin;
                            } else {
                                topVal = (posY * (opts.itemDistance + itemHeight)) - opts.connectorMargin - $(this).outerHeight(true);
                            }

                        } else if ($(this).hasClass(opts.itemConnector[1]) && $(this).hasClass('horizontal')) {

                            // Set height and width
                            $(this).css({'height':opts.connectorWidth,'width':connectorLengthH});

                            // Calculate correct left and top values
                            if (posX < 0) {
                                leftVal = (posX * (opts.itemDistance + itemWidth)) + itemWidth + opts.connectorMargin;
                            } else {
                                leftVal = (posX * (opts.itemDistance + itemWidth)) - opts.connectorMargin - $(this).outerWidth(true);
                            }
                            topVal = (posY * (opts.itemDistance + itemHeight)) + ((itemHeight - $(this).outerHeight(true)) / 2);

                        } else {

                            leftVal = posX * (opts.itemDistance + itemWidth);
                            topVal = posY * (opts.itemDistance + itemHeight);

                        }

                        // Add correct coordinate data
                        $(this).attr('data-coord', leftVal + '_' + topVal);

                        // Add correct left and top values
                        $(this).css({'position':'absolute', 'left':leftVal, 'top':topVal});

                    // If data-coord does not exist
                    } else {

                        // Create dummy left value
                        leftVal = (i + 1) * (opts.itemDistance + itemWidth);

                        // Add dummy coordinate data
                        $(this).attr('data-coord', leftVal + '_0');

                        // Add left and top values
                        $(this).css({'position':'absolute', 'left':leftVal, 'top': 0});

                    }

                });

            }

        }

        function centerScreen() {

            // Check if there are any items on canvas
            if ($(sel_itemContainer).length) {

                // Center relative to first item
                var $target = $(sel_itemContainer).first();

                // Init (Make sure the container has the correct start values)
                var initLeft = $(sel_canvas).offset().left - $(sel_canvasContainer).offset().left,
                    initTop = $(sel_canvas).offset().top - $(sel_canvasContainer).offset().top;
                $(sel_canvas).css({'left': initLeft,'top': initTop, 'margin-left': 0, 'margin-top': 0});

                // Calculate left value
                var parentLeft = $(sel_canvas).offset().left - $(sel_canvasContainer).offset().left,
                    targetLeft = $target.offset().left - $(sel_canvasContainer).offset().left,
                    targetLeftCenter = ($(sel_canvasContainer).width() / 2) - ($target.outerWidth(true) / 2),
                    leftDiff = targetLeft - targetLeftCenter,
                    left = Math.round(parentLeft - leftDiff);

                // Calculate top value
                var parentTop = $(sel_canvas).offset().top - $(sel_canvasContainer).offset().top,
                    targetTop = $target.offset().top - $(sel_canvasContainer).offset().top,
                    targetTopCenter = ($(sel_canvasContainer).height() / 2) - ($target.outerHeight() / 2),
                    topDiff = targetTop - targetTopCenter,
                    top = Math.round(parentTop - topDiff);

                // Move canvas to new position
                $(sel_canvas).css({'left': left, 'top': top});

            }

        }

        function mouseEvents() {

            // Toggle item details
            $(sel_canvas).on('click.networkToggleTip', sel_item + ' > .title, ' + sel_item + ' > .color', function (event) {
                event.preventDefault();
                var $infoBox = $(this).closest(sel_item).find('.info');
                // If the clicked item's info box is open
                if ($infoBox.is(':visible')) {
                    // Close the item's infobox
                    $infoBox.fadeOut(200);
                // If the clicked item's info box is closed
                } else {
                    // Close all open infoboxes
                    $(this).closest(sel_canvas).find('.info').hide();
                    // Show the item's infobox
                    $infoBox.fadeIn(200);
                }
            });

            // Extend toggle to answer indicator element
            $(sel_canvas).on('click.networkExtendToggleTip', sel_item + ' .answer-indicator', function () {
                $(this).siblings('.color').trigger('click');
            });

            // Close item details
            $(sel_canvas).on('click.networkCloseTip', sel_item + ' .info .close', function () {
                $(this).closest('.info').fadeOut(200);
            });

            // Switch views between task & work
            $(sel_canvas).on('click', sel_item + ' .view-switch .tab', function () {
                if (!$(this).hasClass('active')) {

                    // Toggle active class
                    $(this).addClass('active').siblings().removeClass('active');

                    // Toggle view
                    $(this).parent().siblings('.views').find('.tab-content').removeClass('active').end().find('.' + $(this).attr('data-tab-target')).addClass('active');

                }
            });

        }

        function canvasDraggable() {

            $(sel_canvasHandle).draggable({
                cursor: 'move',
                cancel: sel_itemContainer + ', .nodrag',
                stop: function(event, ui) {

                    var canvasLeft = Math.round( $(sel_canvas).position().left ),
                        canvasTop = Math.round( $(sel_canvas).position().top ),
                        handleLeft = Math.round( $(sel_canvasHandle).position().left ),
                        handleTop = Math.round( $(sel_canvasHandle).position().top ),
                        left = canvasLeft + handleLeft,
                        top = canvasTop + handleTop;

                    // Center canvas handle inside canvas container, but keep the canvas at its drop place
                    $(sel_canvas).css({'left': left, 'top': top});
                    $(sel_canvasHandle).css({'left': 0, 'top': 0});
                    
                }
            });

        }

    };
    
    $.fn.networkCanvas.defaults = {
        item: ['.', 'task'],
        itemContainer: ['.', 'network-canvas-item-container'],
        canvas: ['#', 'network-canvas'],
        canvasHandle: ['#', 'network-canvas-handle'],
        canvasContainer: ['#', 'network-canvas-container'],
        itemConnector: ['.', 'network-canvas-item-connector'],
        itemDistance: 120,
        connectorMargin: 40,
        connectorWidth: 10,
        itemFade: true,
        itemFadeInSpeed: 400,
        itemFadeOutSpeed: 400,
        centeringSpeed: 600
    };

})(jQuery);
