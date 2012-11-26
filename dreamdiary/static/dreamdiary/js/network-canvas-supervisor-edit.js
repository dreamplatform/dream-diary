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

        if (options === 'saveData') {
            saveItemData();
        } else if (options === 'clean' || options === 'center') {
            cleanCanvas();
        } else {
            init();
            mouseEvents();
            canvasDraggable();
            canvasSortable();
        }

    // MAIN FUNCTIONS (PUBLIC)

        function saveItemData() {

            /* NOTE: This function depends on json jquery plugin */

            var array = [];

            $(sel_itemContainer + ',' + sel_connector).filter('.active').each(function () {

                var object = {},
                    posX = parseInt($(this).attr('data-coord').split('_')[0]),
                    posY = parseInt($(this).attr('data-coord').split('_')[1]),
                    itemWidth = $(sel_canvas).width(),
                    itemHeight = $(sel_canvas).height(),
                    canvasItemDistX = Math.round(opts.itemDistance + $(sel_canvas).outerWidth(true)),
                    canvasItemDistY = Math.round(opts.itemDistance + $(sel_canvas).outerHeight(true));


                // If the item is vertical connector
                if ($(this).hasClass('vertical')) {
                    object.type = 'connector-vertical';
                    object.x = (posX - ((itemWidth - $(this).outerWidth(true)) / 2)) / canvasItemDistX;
                    if (posY > 0) {
                        object.y = (posY + $(this).outerHeight(true) + opts.connectorMargin) / canvasItemDistY;
                    } else {
                        object.y = (posY - opts.connectorMargin - itemHeight) / canvasItemDistY;
                    }

                // If the item is horizontal connector
                } else if ($(this).hasClass('horizontal')) {
                    object.type = 'connector-horizontal';
                    if (posX > 0) {
                        object.x = (posX + $(this).outerWidth(true) + opts.connectorMargin) / canvasItemDistX;
                    } else {
                        object.x = (posX - opts.connectorMargin - itemWidth) / canvasItemDistX;
                    }
                    object.y = (posY - ((itemHeight - $(this).outerHeight(true)) / 2)) / canvasItemDistY;

                // If the item is task
                } else {
                    object.type = 'item';
                    object.x = posX / canvasItemDistX;
                    object.y = posY / canvasItemDistY;
                    object.id = $(this).find(sel_item).attr('data-id');
                }

                // Push the objects into the array
                array.push(object);

            });

            // Store JSON data to learning network element
            $(sel_canvas).data('itemData', $.toJSON(array));

        }

        function cleanCanvas() {

        // LOGIC

            if (options === 'center') {
                centerScreen();
            } else {
                addItems();
                centerScreen();
                showItems();
                reloadSortable();
                // Clean up temporary classnames
                $(sel_itemContainer).removeClass('married divorced divorced-neighbour');
            }

        // FUNCTIONS

            function addItems() {

                $(sel_itemContainer + '.divorced, ' + sel_itemContainer + '.married').each(function () {

                    var $target = $(this),
                        left = Math.round($target.position().left),
                        top = Math.round($target.position().top),
                        canvasItemDistH = Math.round(opts.itemDistance + $(sel_canvas).outerWidth()),
                        canvasItemDistV = Math.round(opts.itemDistance + $(sel_canvas).outerHeight()),
                        connectorLengthH = Math.round(canvasItemDistH - $(sel_canvas).outerWidth() - (opts.connectorMargin * 2)),
                        connectorLengthV = Math.round(canvasItemDistV - $(sel_canvas).outerHeight() - (opts.connectorMargin * 2)),
                        targetCoord = left + '_' + top;

                    // Item coordinates & identifiers

                    var itemNLeft = Math.round(left),
                        itemNTop = Math.round(top - canvasItemDistV),
                        itemNCoord = itemNLeft + '_' + itemNTop,
                        $itemN = $(sel_itemContainer + '[data-coord="' + itemNCoord + '"]');

                    var itemELeft = Math.round(left + canvasItemDistH),
                        itemETop = Math.round(top),
                        itemECoord = itemELeft + '_' + itemETop,
                        $itemE = $(sel_itemContainer + '[data-coord="' + itemECoord + '"]');

                    var itemSLeft = Math.round( left ),
                        itemSTop = Math.round(top + canvasItemDistV),
                        itemSCoord = itemSLeft + '_' + itemSTop,
                        $itemS = $(sel_itemContainer + '[data-coord="' + itemSCoord + '"]');

                    var itemWLeft = Math.round(left - canvasItemDistH),
                        itemWTop = Math.round(top),
                        itemWCoord = itemWLeft + '_' + itemWTop,
                        $itemW = $(sel_itemContainer + '[data-coord="' + itemWCoord + '"]');

                    // Connector positions and identifiers

                    var conNLeft = Math.round(left + ($target.outerWidth(true) / 2) - (opts.connectorWidth / 2)),
                        conNTop = Math.round(top - opts.connectorMargin - connectorLengthV),
                        conNCoord = conNLeft + '_' + conNTop,
                        $conN = $(sel_connector + '[data-coord="' + conNCoord + '"]');

                    var conELeft = Math.round(left + ($target.outerWidth(true) + opts.connectorMargin)),
                        conETop = Math.round(top + ($target.outerHeight(true) / 2) - (opts.connectorWidth / 2)),
                        conECoord = conELeft + '_' + conETop,
                        $conE = $(sel_connector + '[data-coord="' + conECoord + '"]');

                    var conSLeft = Math.round(left + ($target.outerWidth(true) / 2) - (opts.connectorWidth / 2)),
                        conSTop = Math.round(top + opts.connectorMargin + $target.outerHeight(true)),
                        conSCoord = conSLeft + '_' + conSTop,
                        $conS = $(sel_connector + '[data-coord="' + conSCoord + '"]');

                    var conWLeft = Math.round(left - opts.connectorMargin - connectorLengthH),
                        conWTop = Math.round(top + ($target.outerHeight(true) / 2) - (opts.connectorWidth / 2)),
                        conWCoord = conWLeft + '_' + conWTop,
                        $conW = $(sel_connector + '[data-coord="' + conWCoord + '"]');


                    // If element is only divorced
                    if ($target.hasClass('divorced') && !$target.hasClass('married')) {

                        // If there canvas does not have active items
                        if (!$(sel_itemContainer).filter('.active').length) {

                            // Remove all item containers (except the first) 
                            $(sel_itemContainer).not(':first').addClass('kill');

                            // Remove all connectors
                            $(sel_connector).addClass('kill');

                        }

                        // If canvas has active items
                        else {

                            // Identify & temporarily tag all non-active neighbour items
                            if ($itemN.length && !$itemN.hasClass('active')) {
                                $itemN.addClass('divorced-neighbour');
                            }
                            if ($itemE.length && !$itemE.hasClass('active')) {
                                $itemE.addClass('divorced-neighbour');
                            }
                            if ($itemS.length && !$itemS.hasClass('active')) {
                                $itemS.addClass('divorced-neighbour');
                            }
                            if ($itemW.length && !$itemW.hasClass('active')) {
                                $itemW.addClass('divorced-neighbour');
                            }

                            // Mark target's neighbour connectors to be removed later on
                            if ($conN.length) {
                                $conN.removeClass('active').addClass('kill');
                            }
                            if ($conE.length) {
                                $conE.removeClass('active').addClass('kill');
                            }
                            if ($conS.length) {
                                $conS.removeClass('active').addClass('kill');
                            }
                            if ($conW.length) {
                                $conW.removeClass('active').addClass('kill');
                            }

                            // Get divorced and it's non-active neighbours
                            $(sel_itemContainer + '.divorced,' + sel_itemContainer + '.divorced-neighbour').each(function () {

                                $target = $(this);
                                left = Math.round($target.position().left);
                                top = Math.round($target.position().top);
                                canvasItemDistH = Math.round(opts.itemDistance + $(sel_canvas).outerWidth());
                                canvasItemDistV = Math.round(opts.itemDistance + $(sel_canvas).outerHeight());
                                connectorLengthH = Math.round(canvasItemDistH - $(sel_canvas).outerWidth() - (opts.connectorMargin * 2));
                                connectorLengthV = Math.round(canvasItemDistV - $(sel_canvas).outerHeight() - (opts.connectorMargin * 2));

                                // Item coordinates & identifiers

                                itemNLeft = Math.round(left);
                                itemNTop = Math.round(top - canvasItemDistV);
                                itemNCoord = itemNLeft + '_' + itemNTop;
                                $itemN = $(sel_itemContainer+'[data-coord="' + itemNCoord + '"]');

                                itemELeft = Math.round(left + canvasItemDistH);
                                itemETop = Math.round(top);
                                itemECoord = itemELeft + '_' + itemETop;
                                $itemE = $(sel_itemContainer + '[data-coord="' + itemECoord + '"]');

                                itemSLeft = Math.round(left);
                                itemSTop = Math.round(top + canvasItemDistV);
                                itemSCoord = itemSLeft + '_' + itemSTop;
                                $itemS = $(sel_itemContainer + '[data-coord="' + itemSCoord + '"]');

                                itemWLeft = Math.round(left - canvasItemDistH);
                                itemWTop = Math.round(top);
                                itemWCoord = itemWLeft + '_' + itemWTop;
                                $itemW = $(sel_itemContainer + '[data-coord="' + itemWCoord + '"]');

                                // If element has no active neighbours tag the element to be removed
                                if (!($itemN.length && $itemN.hasClass('active')) && !($itemE.length && $itemE.hasClass('active')) && !($itemS.length && $itemS.hasClass('active')) && !($itemW.length && $itemW.hasClass('active'))) {
                                   $target.addClass('kill'); 
                                }

                            });
                        }

                    // If element is only married
                    } else if ($target.hasClass('married') && !$target.hasClass('divorced')) {

                        // Add coordinate data to target
                        $target.attr('data-coord', targetCoord);

                        // Append needed items
                        if (!$itemN.length && !$itemN.hasClass('active')) {
                            $(sel_canvas).append('<ul data-sortable-connect-id="canvas-inactive" data-coord="' + itemNCoord + '" class="' + opts.itemContainer[1] + ' inactive new" style="left:' + itemNLeft + 'px;top:' + itemNTop + 'px;"></ul>');
                        }
                        if (!$itemE.length && !$itemE.hasClass('active')) {
                            $(sel_canvas).append('<ul data-sortable-connect-id="canvas-inactive" data-coord="' + itemECoord + '" class="' + opts.itemContainer[1] + ' inactive new" style="left:' + itemELeft + 'px;top:' + itemETop + 'px;"></ul>');
                        }
                        if (!$itemS.length && !$itemS.hasClass('active')) {
                            $(sel_canvas).append('<ul data-sortable-connect-id="canvas-inactive" data-coord="' + itemSCoord + '" class="' + opts.itemContainer[1] + ' inactive new" style="left:' + itemSLeft + 'px;top:' + itemSTop + 'px;"></ul>');
                        }
                        if (!$itemW.length && !$itemW.hasClass('active')) {
                            $(sel_canvas).append('<ul data-sortable-connect-id="canvas-inactive" data-coord="' + itemWCoord + '" class="' + opts.itemContainer[1] + ' inactive new" style="left:' + itemWLeft + 'px;top:' + itemWTop + 'px;"></ul>');
                        }

                        // Append needed connectors
                        if ($itemN.length && $itemN.hasClass('active') && !$conN.length) {
                            $(sel_canvas).append('<div data-coord="' + conNCoord + '" class="' + opts.itemConnector[1] + ' vertical new" style="position:absolute;left:' + conNLeft + 'px;top:' + conNTop + 'px;height:' + connectorLengthV + 'px;width:' + opts.connectorWidth + 'px;"></div>');
                        }
                        if ($itemE.length && $itemE.hasClass('active') && !$conE.length) {
                            $(sel_canvas).append('<div data-coord="' + conECoord + '" class="' + opts.itemConnector[1] + ' horizontal new" style="position:absolute;left:' + conELeft + 'px;top:' + conETop + 'px;height:' + opts.connectorWidth + 'px;width:' + connectorLengthH + 'px;"></div>');
                        }
                        if ($itemS.length && $itemS.hasClass('active') && !$conS.length) {
                            $(sel_canvas).append('<div data-coord="' + conSCoord + '" class="' + opts.itemConnector[1] + ' vertical new" style="position:absolute;left:' + conSLeft + 'px;top:' + conSTop + 'px;height:' + connectorLengthV + 'px;width:' + opts.connectorWidth + 'px;"></div>');
                        }
                        if ($itemW.length && $itemW.hasClass('active') && !$conW.length) {
                            $(sel_canvas).append('<div data-coord="' + conWCoord + '" class="' + opts.itemConnector[1] + ' horizontal new" style="position:absolute;left:' + conWLeft + 'px;top:' + conWTop + 'px;height:' + opts.connectorWidth + 'px;width:' + connectorLengthH + 'px;"></div>');
                        }

                    }

                });

            }

            function centerScreen() {

                if ($(sel_itemContainer).filter('.married').length) {
                    // Center relative to center target
                    var $target = $(sel_itemContainer).filter('.married');
                } else {
                    if ($(sel_itemContainer).filter('.active').length) {
                        // Center relative to first active item
                        var $target = $(sel_itemContainer).filter('.active').first();
                    } else {
                        // Center relative to first safe item
                        var $target = $(sel_itemContainer).not('.kill').first();
                    }
                }

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
                    top =  Math.round(parentTop - topDiff);

                // Move canvas to new position
                if (options === 'center') {
                    $(sel_canvas).stop(true).css({'left': left, 'top': top});
                } else {
                    if (opts.centeringSpeed > 0 ) {
                        $(sel_canvas).stop(true).animate({left: left, top: top}, opts.centeringSpeed);
                    } else {
                        $(sel_canvas).css({'left': left, 'top': top});
                    }
                }

            }

            function showItems() {

                if (opts.itemFade === true) {

                    $(sel_itemContainer + ',' + sel_connector).filter('.new').each(function () {
                        $(this).removeClass('new').css('display','none').fadeIn(opts.itemFadeInSpeed);
                    });

                    $(sel_itemContainer + ',' + sel_connector).filter('.kill').each(function () {
                        $(this).removeClass('kill').fadeOut(opts.itemFadeOutSpeed, function () {
                            $(this).remove();
                        });
                    });

                } else {

                    $(sel_itemContainer + ',' + sel_connector).filter('.kill').each(function () {
                        $(this).removeClass('kill').remove();
                    });
                    
                }

            }

            function reloadSortable() {
                // Destroy & Reload sortable function in order to recognize new items
                $(sel_itemContainer).each(function () {
                  if ($(this).hasClass('ui-sortable')) {
                    $(this).sortable('destroy');
                  }
                });
                canvasSortable();
            }
        }

    // MAIN FUNCTIONS (PRIVATE)

        function init() {

            // Check if there are any active items on canvas
            if ($(sel_itemContainer + '.active').length) {

                // Position all the existing active items and connectors correctly
                $(sel_itemContainer + '.active,' + sel_connector + '.active').each(function (i) {

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

                // Append the needed inactive items and connectors according to the existing items
                $(sel_itemContainer + '.active').each(function () {

                    var $target = $(this),
                        left = Math.round($target.position().left),
                        top = Math.round($target.position().top),
                        canvasItemDistH = Math.round(opts.itemDistance + $(sel_canvas).outerWidth()),
                        canvasItemDistV = Math.round(opts.itemDistance + $(sel_canvas).outerHeight()),
                        connectorLengthH = Math.round(canvasItemDistH - $(sel_canvas).outerWidth() - (opts.connectorMargin * 2)),
                        connectorLengthV = Math.round(canvasItemDistV - $(sel_canvas).outerHeight() - (opts.connectorMargin * 2));

                    // Define item coordinates & identifiers

                    var itemNLeft = Math.round(left),
                        itemNTop = Math.round(top - canvasItemDistV),
                        itemNCoord = itemNLeft + '_' + itemNTop,
                        $itemN = $(sel_itemContainer + '[data-coord="' + itemNCoord + '"]');

                    var itemELeft = Math.round(left + canvasItemDistH),
                        itemETop = Math.round(top),
                        itemECoord = itemELeft + '_' + itemETop,
                        $itemE = $(sel_itemContainer + '[data-coord="' + itemECoord + '"]');

                    var itemSLeft = Math.round(left),
                        itemSTop = Math.round(top + canvasItemDistV),
                        itemSCoord = itemSLeft + '_' + itemSTop,
                        $itemS = $(sel_itemContainer + '[data-coord="' + itemSCoord + '"]');

                    var itemWLeft = Math.round(left - canvasItemDistH),
                        itemWTop = Math.round(top),
                        itemWCoord = itemWLeft + '_' + itemWTop,
                        $itemW = $(sel_itemContainer + '[data-coord="' + itemWCoord + '"]');

                    // Define connector positions and identifiers

                    var conNLeft = Math.round(left + ($target.outerWidth(true) / 2) - (opts.connectorWidth / 2)),
                        conNTop = Math.round(top - opts.connectorMargin - connectorLengthV),
                        conNCoord = conNLeft + '_' + conNTop,
                        $conN = $(sel_connector + '[data-coord="' + conNCoord + '"]');

                    var conELeft = Math.round(left + ($target.outerWidth(true) + opts.connectorMargin)),
                        conETop = Math.round(top + ($target.outerHeight(true) / 2) - (opts.connectorWidth / 2)),
                        conECoord = conELeft + '_' + conETop,
                        $conE = $(sel_connector + '[data-coord="' + conECoord + '"]');

                    var conSLeft = Math.round(left + ($target.outerWidth(true) / 2) - (opts.connectorWidth / 2)),
                        conSTop = Math.round(top + opts.connectorMargin + $target.outerHeight(true)),
                        conSCoord = conSLeft + '_' + conSTop,
                        $conS = $(sel_connector + '[data-coord="' + conSCoord + '"]');

                    var conWLeft = Math.round(left - opts.connectorMargin - connectorLengthH),
                        conWTop = Math.round(top + ($target.outerHeight(true) / 2) - (opts.connectorWidth / 2)),
                        conWCoord = conWLeft + '_' + conWTop,
                        $conW = $(sel_connector + '[data-coord="' + conWCoord + '"]');


                    // Append needed items

                    if (!$itemN.length && !$itemN.hasClass('active')) {
                        $(sel_canvas).append('<ul data-sortable-connect-id="canvas-inactive" data-coord="' + itemNCoord + '" class="' + opts.itemContainer[1] + ' inactive" style="left:' + itemNLeft + 'px;top:' + itemNTop + 'px;"></ul>');
                    }
                    if (!$itemE.length && !$itemE.hasClass('active')) {
                        $(sel_canvas).append('<ul data-sortable-connect-id="canvas-inactive" data-coord="' + itemECoord + '" class="' + opts.itemContainer[1] + ' inactive" style="left:' + itemELeft + 'px;top:' + itemETop + 'px;"></ul>');
                    }
                    if (!$itemS.length && !$itemS.hasClass('active')) {
                        $(sel_canvas).append('<ul data-sortable-connect-id="canvas-inactive" data-coord="' + itemSCoord + '" class="' + opts.itemContainer[1] + ' inactive" style="left:' + itemSLeft + 'px;top:' + itemSTop + 'px;"></ul>');
                    }
                    if (!$itemW.length && !$itemW.hasClass('active')) {
                        $(sel_canvas).append('<ul data-sortable-connect-id="canvas-inactive" data-coord="' + itemWCoord + '" class="' + opts.itemContainer[1] + ' inactive" style="left:' + itemWLeft + 'px;top:' + itemWTop + 'px;"></ul>');
                    }

                    // Append needed connectors

                    if ($itemN.length && $itemN.hasClass('active') && !$conN.length) {
                        $(sel_canvas).append('<div data-coord="' + conNCoord + '" class="' + opts.itemConnector[1] + ' vertical" style="position:absolute;left:' + conNLeft + 'px;top:' + conNTop + 'px;height:' + connectorLengthV + 'px;width:' + opts.connectorWidth + 'px;"></div>');
                    }
                    if ($itemE.length && $itemE.hasClass('active') && !$conE.length) {
                        $(sel_canvas).append('<div data-coord="' + conECoord + '" class="' + opts.itemConnector[1] + ' horizontal" style="position:absolute;left:' + conELeft + 'px;top:' + conETop + 'px;height:' + opts.connectorWidth + 'px;width:' + connectorLengthH + 'px;"></div>');
                    }
                    if ($itemS.length && $itemS.hasClass('active') && !$conS.length) {
                        $(sel_canvas).append('<div data-coord="' + conSCoord + '" class="' + opts.itemConnector[1] + ' vertical" style="position:absolute;left:' + conSLeft + 'px;top:' + conSTop + 'px;height:' + connectorLengthV + 'px;width:' + opts.connectorWidth + 'px;"></div>');
                    }
                    if ($itemW.length && $itemW.hasClass('active') && !$conW.length) {
                        $(sel_canvas).append('<div data-coord="' + conWCoord + '" class="' + opts.itemConnector[1] + ' horizontal" style="position:absolute;left:' + conWLeft + 'px;top:' + conWTop + 'px;height:' + opts.connectorWidth + 'px;width:' + connectorLengthH + 'px;"></div>');
                    }

                });

                function centerScreen() {

                    // Center relative to first active item
                    var $target = $(sel_itemContainer).filter('.active').first();

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
                centerScreen();

            }

        }

        function mouseEvents() {

            // Add active class to connector
            $(sel_canvas).off('click.networkToggleConnector', sel_connector).on('click.networkToggleConnector', sel_connector, function () {
                $(this).toggleClass('active');
            });

            // Toggle item details
            $(sel_canvas).off('click.networkToggleTip', sel_item + ' > .title a, ' + sel_item + ' > .color').on('click.networkToggleTip', sel_item + ' > .title a, ' + sel_item + ' > .color', function (event) {
                event.preventDefault();
                var $infoBox = $(this).closest(sel_item).find('.info'),
                    itemLink = $(this).closest(sel_item).children('.title').find('a').attr('href'),
                    itemText = $(this).closest(sel_item).children('.title').find('.text').html(),
                    infoBoxTitle = '<div class="arrow"></div><div class="title"><span class="link"><a href="' + itemLink + '">' + itemText + '</a></span><span class="close"></span></div><div class="actions"><span class="remove">Poista tehtävä oppimisverkosta</span></div>';
                // If the clicked item's info box is open
                if ($infoBox.is(':visible')) {
                    // Close the item's infobox
                    $infoBox.fadeOut(200);
                // If the clicked item's info box is closed
                } else {
                    // Close all open infoboxes
                    $(this).closest(sel_canvas).find('.info').hide();
                    // If the item does not have additional title data
                    if (!$infoBox.find('.title').length) {
                        // Append the additional title data
                        $infoBox.prepend(infoBoxTitle);
                    }
                    // Show the item's infobox
                    $infoBox.fadeIn(200);
                }
            });

            // Close item details
            $(sel_canvas).off('click.networkCloseTip', sel_item + ' .info .close').on('click.networkCloseTip', sel_item + ' .info .close', function () {
                $(this).closest('.info').fadeOut(200);
            });

            // Remove item
            $(sel_canvas).off('click.removeItem', sel_item + ' .info .remove').on('click.removeItem', sel_item + ' .info .remove', function () {
                // Remove & add necessary item container classes & attributes
                $(this).closest(sel_itemContainer)
                    .removeClass('active').addClass('inactive divorced')
                    .attr('data-sortable-connect-id', 'canvas-inactive');
                // Remove item
                $(this).closest(sel_item).remove();
                // Reload canvas
                cleanCanvas();
            });

        }

        function canvasDraggable() {

            $(sel_canvasHandle).draggable({
                cursor: 'move',
                cancel: sel_itemContainer + '.active, ' + sel_connector + ', .nodrag',
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

            // Add touch support to sortables
            // - Attach function only to sortable handles, otherwise things get buggy
            // - NOTE: Crashes when applied at the same time to sortable handle, try to find a solution...
            //$(sel_canvasHandle).addTouch();

        }

        function canvasSortable() {

            var connections = '',
                data_connectID = 'data-sortable-connect-id',
                data_connectTo = 'data-sortable-connect-to',
                class_itemClone = 'sortable-item-clone',
                class_phClone = 'ui-sortable-placeholder-clone',
                class_sortSuccess = 'sort-successful',
                animationDuration = 300;

            // Add sortable handle class to color elements
            $(sel_canvas).find('.color').addClass('sortable-handle');

            $(sel_itemContainer).sortable({
                connectWith: sel_itemContainer + '.inactive',
                items: sel_item,
                handle: '.sortable-handle',
                cancel: '.sortable-cancel',
                helper: 'clone',
                placeholder: 'ui-sortable-placeholder',
                tolerance: 'pointer',
                start: function(event, ui) {

                    // If item is dragged within canvas
                    if (ui.placeholder.closest(sel_canvas).length) {
                        ui.item.closest(sel_itemContainer)
                            .removeClass('active').addClass('inactive divorced')
                            .attr('data-sortable-connect-id', 'canvas-inactive');
                    }

                },
                change: function(event, ui) {

                    // Set temporary highlight class to item container
                    $('.canvas-item-container-highlight').removeClass('canvas-item-container-highlight');
                    ui.placeholder.closest(sel_itemContainer).addClass('canvas-item-container-highlight');
    
                },
                over: function(event, ui) {

                    // If item is dragged into the canvas from a connected list
                    if (!ui.sender.hasClass(opts.itemContainer[1])) {
                        // Reset placeholder height
                        ui.placeholder.removeAttr('style');
                        // If canvas has duplicate items
                        if ($(sel_canvas).find('[data-id="' + ui.item.attr('data-id') + '"]').length) {
                            // Hide placeholder
                            ui.placeholder.hide();
                            // Show cloned placeholder
                            $('.' + class_phClone).show();
                            // Add block class to helper
                            ui.helper.addClass('blocked');
                        // If canvas does not have duplicate items
                        } else {
                            // Show clone
                            ui.item.siblings('.' + class_itemClone).show();
                        }
                    }

                },
                beforeStop: function(event, ui) {

                    // Remove temporary item container highlight class
                    $('.canvas-item-container-highlight').removeClass('canvas-item-container-highlight');

                    // If item is dragged within canvas
                    if (ui.placeholder.closest(sel_canvas).length) {
                        ui.placeholder.closest(sel_itemContainer)
                            .removeClass('inactive').addClass('active married')
                            .attr('data-sortable-connect-id', 'canvas-active');
                        cleanCanvas();
                    }

                },
                receive: function(event, ui) {

                    // Remove temporary item container highlight class
                    $('.canvas-item-container-highlight').removeClass('canvas-item-container-highlight');

                    // If item is dragged into the canvas from a connected list
                    if (!ui.sender.hasClass(opts.itemContainer[1])) {
                        // If helper was blocked during drag release
                        if (ui.item.hasClass('remove')) {
                            // Remove the original item
                            ui.item.remove();
                            // Indicate that the sort was succesful
                            $('.' + class_itemClone).addClass(class_sortSuccess).animate({opacity: 1}, animationDuration, function () {
                                // Remove the item clone's clone class and 'sort succesful' class
                                $('.' + class_itemClone).removeClass(class_sortSuccess + ' ' + class_itemClone);
                            });
                        // If helper was not blocked during drag release
                        } else {
                            // Remove & add necessary canvas item classes & update sortable connect id
                            ui.item.closest(sel_itemContainer)
                                .removeClass('inactive').addClass('active married')
                                .attr('data-sortable-connect-id', 'canvas-active');
                            // Remove the item clone's clone class
                            $('.' + class_itemClone).removeClass(class_itemClone);
                            // Reload canvas
                            cleanCanvas();
                        }
                    }

                }
            });

        }
    };
    
    $.fn.networkCanvas.defaults = {
        item: ['.', 'sortable-item'],
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
