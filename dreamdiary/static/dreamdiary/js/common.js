$(function () {

/*=========================================================
  Sortable lists
=========================================================*/

// Extened initSortables to events outside the scope of the parent function
$(document).on('click', '.tab-content-work > .actions > .remove', function () {
  initSortables();
});

initSortables();
function initSortables() {

  // Remove temporary sort cancel classes
  $('.sortable-cancel-temp').removeClass('sortable-cancel sortable-cancel-temp');

  $('.sortable').each(function (i) {

    var $this = $(this),
        connections = '',
        data_connectID = 'data-sortable-connect-id',
        data_connectTo = 'data-sortable-connect-to',
        class_itemClone = 'sortable-item-clone',
        class_phClone = 'ui-sortable-placeholder-clone',
        class_sortSuccess = 'sort-successful',
        animationDuration = 300;

    // If this is connected to other sortables
    if ($this.attr('data-sortable-connect-to')) {
      // Connect connected sortables
      function sortableConnections(i) {
        var connectionsArray = [];
        for ( var i = 0; i < $this.attr(data_connectTo).split(',').length; ++i ) {
          if ($('[' + data_connectID + '="' + $this.attr(data_connectTo).split(',')[i] + '"]').length) {
            connectionsArray.push('[' + data_connectID + '="' + $this.attr(data_connectTo).split(',')[i] + '"]');
          }
        }
        return connectionsArray.toString();
      }
      connections = sortableConnections();
    }

    // Init jQuery UI sortable
    $this.sortable({
      items: '.sortable-item',
      handle: '.sortable-handle',
      cancel: '.sortable-cancel',
      helper: 'clone',
      placeholder: 'ui-sortable-placeholder',
      tolerance: 'pointer',
      connectWith: connections,
      start: function(event, ui) {

        // Prevent all sorting until the sortable's are reloaded
        // - fixes a bug, where items disappear on too fast sorting
        $('.sortable-handle').addClass('sortable-cancel sortable-cancel-temp');
        // Identify the original sortable list
        $originalList = ui.item.closest('.sortable');
        // Set placeholder height according to helper
        ui.placeholder.css({'height': ui.helper.outerHeight()});
        // If sortable has connections 
        if (connections !== '') {
          // Clone the item and placeholder
          var itemClone = ui.item.clone().addClass(class_itemClone),
              phClone = ui.placeholder.clone().addClass(class_phClone).hide();
          // Put the item and placeholder to the list
          ui.item.after(itemClone);
          ui.placeholder.after(phClone);
        }

      },
      change: function(event, ui) {

        // If sortable has connections 
        if (connections !== '') {
          // If placeholder is inside sender list
          if (ui.placeholder.siblings('.' + class_itemClone).length) {
            // Update placeholder clone's position
            $('.' + class_phClone).detach().insertAfter(ui.placeholder);
          }
        }

      },
      over: function(event, ui) {

        // Make sure that placeholder is initially visible
        ui.placeholder.show();
        // Make sure that cloned placeholder is initially hidden
        $('.' + class_phClone).hide();
        // Make sure that helper is not blocked
        ui.helper.removeClass('blocked');
        // If placeholder moves to a connected list
        if (ui.placeholder.closest('.sortable').attr(data_connectID) !== ui.sender.attr(data_connectID)) {
          // If duplicate items exist
          if (ui.placeholder.siblings('[data-id="' + ui.item.attr('data-id') + '"]').length) {
            // Hide placeholder
            ui.placeholder.hide();
            // Show cloned placeholder
            $('.' + class_phClone).show();
            // Add block class to helper
            ui.helper.addClass('blocked');
          // If duplicate items do not exist
          } else {
            // Show clone
            ui.item.siblings('.' + class_itemClone).show();
          }
        // If placeholder moves back to the sender list
        } else {
          // Set placeholder height according to helper
          ui.placeholder.css({'height': ui.helper.outerHeight()});
          // Hide clone
          ui.item.siblings('.' + class_itemClone).hide();
        }

        // Remove temporary item container highlight class (canvas related)
        $('.canvas-item-container-highlight').removeClass('canvas-item-container-highlight');

      },
      beforeStop: function(event, ui) {

        // If sortable has connections 
        if (connections !== '') {
          // If helper is blocked
          if (ui.helper.hasClass('blocked')) {
            // Move the item clone to correct position & show it
            $('.' + class_itemClone).detach().insertBefore('.' + class_phClone).show();
            // Remove placeholder clone
            $('.' + class_phClone).remove();
            // Add remove class to the item
            ui.item.addClass('remove');
          // If helper is not blocked
          } else {
            // If the item was not moved to a connected list
            if (ui.item.siblings('.' + class_itemClone).length) {
              // Remove item clone
              ui.item.siblings('.' + class_itemClone).remove();
              // Indicate that the sort was succesful
              ui.item.addClass(class_sortSuccess).animate({opacity: 1}, animationDuration, function () {
                // Remove the item's 'sort succesful' class
                ui.item.removeClass(class_sortSuccess);
              });
            }
            // Remove temporary placeholder
            $('.' + class_phClone).remove();
          }
        // If sortable does not have connections 
        } else {
          // Indicate that the sort was succesful
          ui.item.addClass(class_sortSuccess).animate({opacity: 1}, animationDuration, function () {
            // Remove the item's 'sort succesful' class
            ui.item.removeClass(class_sortSuccess);
          });
        }

      },
      update: function(event, ui) {},
      receive: function(event, ui) {

        // If helper was blocked during drag release
        if (ui.item.hasClass('remove')) {
          // Remove the original item
          ui.item.remove();
          // Indicate that the sort was succesful
          $('.' + class_itemClone).addClass(class_sortSuccess).animate({opacity: 1}, animationDuration, function () {
            // Remove the item clone's clone class and 'sort succesful' class
            $('.' + class_itemClone).removeClass(class_sortSuccess + ' ' + class_itemClone);
          });
        } else {
          // Indicate that the sort was succesful
          ui.item.addClass(class_sortSuccess).animate({opacity: 1}, animationDuration, function () {
            // Remove the item's 'sort succesful' class
            ui.item.removeClass(class_sortSuccess);
          });
          // Remove the item clone's clone class
          $('.' + class_itemClone).removeClass(class_itemClone);
        }

      },
      stop: function(event, ui) {

        // AJAX - post item order
        // If item is moved within original list
        if (ui.item.closest($originalList).length) {
          var itemList = [],
              itemType = ui.item.attr('data-type');
          // Populate item list
          $originalList.find('.sortable-item').each(function () {
            itemList.push($(this).attr('data-id'));
          });
          // Post new item order
          $.post("/ajax/order/", { t: itemType, l: itemList }, function(data) {
          });
        }

        // Wait for the animations to complete
        $('.sortable').animate({opacity: 1}, animationDuration, function () {
          // reload sortables
          reloadSortables();
        });

      }
    });

  });

  // Add touch support to sortables
  // - Attach function only to sortable handles, otherwise things get buggy
  if(Modernizr.touch) {
    $('.sortable-handle').addTouch();
  }
}

function reloadSortables() {

  // Destroy & reload sortables to recognize new items
  $('.sortable').each(function () {
    if ($(this).hasClass('ui-sortable')) {
      $(this).sortable('destroy');
    }
  });
  initSortables();

}


/*=========================================================
  Canvas area resizing / Sticky footer
=========================================================*/

// If canvas exists
adjustLayout();
function adjustLayout() {

  if ($('#network-canvas').length === 1) {
    canvasSize();
    $(window).resize(canvasSize);
  } else {
    stickyFooter();
    $(window).resize(stickyFooter);
  }

  function canvasSize() {

    var $canvas = $('#network-canvas-outer-wrap');
    // Reset canvas inline styles
    if ($canvas.attr('style')) {
      $canvas.removeAttr('style');
    }
    // Define height & min-height
    var height = $(window).height() - $canvas.offset().top - ($canvas.outerHeight(true) - $canvas.height()) - $canvas.siblings('.actions').outerHeight(true),
        minHeight = $canvas.height();
    // Set canvas height
    if (height > minHeight) {
      $canvas.height(height);
    } else {
      $canvas.height(minHeight);
    }
  }

  function stickyFooter() {
    // Remove content min-height
    if ($('#content-container').attr('style')) {
      $('#content-container').removeAttr('style');
    }
    // Set content min-height
    var minHeight = $('#content-container').height() + ($(window).height() - $('body').height());
    if ($('body').height() < $(window).height()) {
      $('#content-container').css('min-height', minHeight);
    }
  }

}


/*=========================================================
  Canvas minimap
=========================================================*/

// Listeners
$(document).on('click', '.scale-minimap', function (e) {
  if ($('#network-canvas').hasClass('minimap-active')) {
    minimap('deactivate');
  } else {
    minimap('activate');
  }
}).on('click', '.canvas-item-clone', function () {
  if ($('#network-canvas').hasClass('minimap-active')) {
    var $targetElement = $('.network-canvas-item-container[data-minimap-id="' + $(this).attr('data-minimap-id') + '"]');
    minimap('deactivate', $targetElement);
  }
});

function minimap(method, zoomElement) {

  // Globals
  var minimap = {};
  minimap.method = {};
  minimap.utility = {};

  // Elements
  var $canvas = $('#network-canvas');
  var $canvasContainer = $('#network-canvas-container');
  var $canvasItems = $('.network-canvas-item-container');
  var $toggleButton = $('.scale-minimap');
  var $zoomContainer = $('#zoomContainer');
  var $zoomViewport = $('#zoomViewport');

  // Check that canvas, container and items exist
  if ($canvas.length === 0 || $canvasContainer.length === 0 || $canvasItems.length === 0 || $canvas.hasClass('animating')) { return; }

  //
  // Methods
  //

  minimap.method.activate = function () {

    var targetScale = minimap.utility.getTargetScale();
    $canvas.addClass('animating');
    $toggleButton.addClass('active');
    $zoomViewport.addClass('nodrag');

    minimap.utility.createClones();

    // If target scale is one, just center canvas
    if (targetScale === 1) {

      var target = minimap.utility.getArea($canvasItems, false),
          targetLeft = target.offsetLeft,
          targetTop = target.offsetTop,
          targetWidth = target.width,
          targetHeight = target.height,
          targetPos = minimap.utility.getCenterPosition(targetLeft, targetTop, targetWidth, targetHeight);

      $canvas.stop(true).animate({ left: targetPos.left, top: targetPos.top }, 400, function () {
        $canvas.attr('data-scale', 1).removeClass('minimap-active animating');
        $toggleButton.removeClass('active');
        $zoomViewport.removeClass('nodrag');
        minimap.utility.destroyClones();
      });

    } else {

      var $fake = $('<div id="fake"></div>');
      var area = minimap.utility.getArea($canvasItems, false);

      $fake.css({
        position: 'absolute',
        left: area.left,
        top: area.top,
        width: area.width,
        height: area.height
      });

      $canvas.append($fake);

      $fake.zoomTo({
        targetsize: 1,
        scalemode: "both",
        duration: 600,
        easing: "ease",
        nativeanimation: true,
        root: $zoomContainer,
        debug: false,
        animationendcallback: function () {
          $fake.remove();
          $canvas.attr('data-scale', targetScale).addClass('minimap-active').removeClass('animating');
        } 
      });

    }

  };

  minimap.method.deactivate = function () {

    var currentScale = $canvas.attr('data-scale') ? parseFloat($canvas.attr('data-scale')) : 1;
    $canvas.addClass('animating');

    if (currentScale !== 1) {

      $zoomContainer.zoomTo({
        targetsize: 1,
        scalemode: "both",
        duration: 600,
        easing: "ease",
        nativeanimation: true,
        root: $zoomContainer,
        debug: false,
        animationendcallback: function () {

          if (zoomElement !== undefined && zoomElement.length === 1) {
            var target = zoomElement,
                targetLeft = target.offset().left,
                targetTop = target.offset().top,
                targetWidth = target.outerWidth(),
                targetHeight = target.outerHeight(),
                targetPos = minimap.utility.getCenterPosition(targetLeft, targetTop, targetWidth, targetHeight);

            $canvas.stop(true).animate({left: targetPos.left, top: targetPos.top, 'margin-left': 0, 'margin-top': 0 }, 600, function () {
              $canvas.attr('data-scale', 1).removeClass('minimap-active animating');
              $toggleButton.removeClass('active');
              $zoomViewport.removeClass('nodrag');
              minimap.utility.destroyClones();
            });

          } else {

            $canvas.attr('data-scale', 1).removeClass('minimap-active animating');
            $toggleButton.removeClass('active');
            $zoomViewport.removeClass('nodrag');
            minimap.utility.destroyClones();
          }

        }
      });

    } else {

      $canvas.attr('data-scale', 1).removeClass('minimap-active').removeClass('animating');
      $toggleButton.removeClass('active');
      $zoomViewport.removeClass('nodrag');
      minimap.utility.destroyClones();

    }

  };

  // Utilities

  minimap.utility.getDifference = function (num1, num2) {
    return (num1 > num2) ? num1-num2 : num2-num1;
  };

  minimap.utility.getArea = function (elements, scaling) {

    var minX, maxX, minY, maxY, width, height, offsetLeft, offsetTop;
    var currentScale = $canvas.attr('data-scale') ? parseFloat($canvas.attr('data-scale')) : 1;

    elements.each(function () {

      var el = $(this);
      var left, top;

      if (scaling === true) {
        left = el.position().left / currentScale;
        top = el.position().top / currentScale;
      } else if (scaling === false) {
        left = el.position().left;
        top = el.position().top;
      } else {
        left = (el.position().left / currentScale) * scaling;
        top = (el.position().top / currentScale) * scaling;
      }

      var right = left + el.outerWidth();
      var bottom = top + el.outerHeight();

      minX = minX === undefined || left < minX ? left : minX;
      maxX = maxX === undefined || right > maxX ? right : maxX;
      minY = minY === undefined || top < minY ? top : minY;
      maxY = maxY === undefined || bottom > maxY ? bottom : maxY;

    });

    width = minimap.utility.getDifference( minX, maxX );
    height = minimap.utility.getDifference( minY, maxY );

    if (scaling === true) {
      offsetLeft = ($canvas.offset().left + minX) / currentScale;
      offsetTop = ($canvas.offset().top + minY) / currentScale;
    } else if (scaling === false) {
      offsetLeft = $canvas.offset().left + minX;
      offsetTop = $canvas.offset().top + minY;
    } else {
      offsetLeft = (($canvas.offset().left + minX) / currentScale) * scaling;
      offsetTop = (($canvas.offset().top + minY) / currentScale) * scaling;
    }

    return { width: width, height: height, left: minX, top: minY, offsetLeft: offsetLeft, offsetTop: offsetTop };

  };

  minimap.utility.getTargetScale = function () {

    var area = minimap.utility.getArea($canvasItems, true);
    var container_width = $canvasContainer.width();
    var container_height = $canvasContainer.height();
    var width_ratio = container_width / area.width;
    var height_ratio = container_height / area.height;
    var target_scale = 1;

    if (width_ratio < 1 && height_ratio < 1) {
      if (width_ratio < height_ratio) {
        target_scale = width_ratio;
      } else {
        target_scale = height_ratio;
      }
    } else if (width_ratio < 1) {
      target_scale = width_ratio;
    } else if (height_ratio < 1) {
      target_scale = height_ratio;
    }

    return target_scale;

  };

  minimap.utility.getCenterPosition = function ( targetLeft, targetTop, targetWidth, targetHeight ) {

    // Save original styles
    var originalStyles = $canvas.attr('style');

    // Get init values
    var initLeft = $canvas.offset().left - $canvasContainer.offset().left,
        initTop = $canvas.offset().top - $canvasContainer.offset().top;

    // Set init values
    $canvas.css({ left: initLeft, top: initTop, 'margin-left': 0, 'margin-top': 0 });

    // Get the goodies
    var canvasLeft = $canvas.offset().left,
        canvasTop = $canvas.offset().top,
        containerLeft = $canvasContainer.offset().left,
        containerTop = $canvasContainer.offset().top,
        containerWidth = $canvasContainer.width(),
        containerHeight = $canvasContainer.height();

    // Calculate left and top
    var left = Math.round((canvasLeft - containerLeft) - ((targetLeft - containerLeft) - ((containerWidth / 2) - (targetWidth / 2))));
    var top = Math.round((canvasTop - containerTop) - ((targetTop - containerTop) - ((containerHeight / 2) - (targetHeight / 2))));

    // Return original styles
    $canvas.attr('style', originalStyles);

    return { left: left, top: top };

  };

  minimap.utility.createClones = function () {

    var clones = [];
    var $cloneContainer = $('<div id="clone-container">');

    $cloneContainer.css({
      position: 'absolute',
      left: -5000,
      top: -5000,
      width: 10000,
      height: 10000,
      zIndex: 9998
    });

    clones.push($cloneContainer);

    $canvasItems.each(function (i) {
      var $ci = $(this);
      var $clone = $('<div class="canvas-item-clone" data-minimap-id="' + i +'"></div>');
      $clone.css({ position: 'absolute', width: $ci.outerWidth(), height: $ci.outerHeight(), left: $ci.position().left, top: $ci.position().top, zIndex: 9999, cursor: 'pointer' });
      clones.push($clone);
      $ci.attr('data-minimap-id', i);
    });

    $canvas.append(clones);

  };

  minimap.utility.destroyClones = function () {
    $('#clone-container').remove();
    $('.canvas-item-clone').remove();
  };

  // Method router
  minimap.method[method]();

}


/*=========================================================
  Pagination & search
=========================================================*/

initFilters();
function initFilters() {

  // Globals

  var searchTimeout = false;
  var ajaxRequest = false;

  // Listeners

  $(document)
  .on('click', '.js-filter-next', function (e) {

    e.preventDefault();
    var filterID = $(this).closest('.js-filter-paginator').attr('data-filter-id');
    filter('next', filterID);

  })
  .on('click', '.js-filter-previous', function (e) {

    e.preventDefault();
    var filterID = $(this).closest('.js-filter-paginator').attr('data-filter-id');
    filter('previous', filterID);

  })
  .on('submit', '.js-filter-paginator form', function (e) {

    e.preventDefault();
    var filterID = $(this).closest('.js-filter-paginator').attr('data-filter-id');
    filter('jump', filterID);
    return false;

  })
  .on('submit', '.js-filter-search form', function (e) {

    e.preventDefault();
    return false;

  })
  .on('keydown', '.js-filter-search input', function (e) {

    var $search = $(this).closest('.js-filter-search');

    // Abort current ajax request
    if (ajaxRequest !== false) {
      ajaxRequest.abort();
      ajaxRequest = false;
    }

    // Clear search timeout
    if (searchTimeout !== false) {
      clearTimeout(searchTimeout);
    }

    // Remove searching class
    if ($search.hasClass('filter-searching')) {
      $search.removeClass('filter-searching');
    }

  })
  .on('keyup', '.js-filter-search input', function (e) {

    // Start filtering after a comfortable timeout
    e.preventDefault();
    var $search = $(this).closest('.js-filter-search');
    var filterID = $search.attr('data-filter-id');
    searchTimeout = setTimeout(function () {
      $search.addClass('filter-searching');
      filter('search', filterID);
    }, 200);

  })
  .on('click', '.open-search', function (e) {

    e.preventDefault();

    var $search = $(this).closest('.header').find('.search');
    var filterID = $search.attr('data-filter-id');

    $search.slideToggle(200, function() {

      // If search field just closed
      if ($search.find('input').is(':hidden')) {

        // Empty search field
        $search.find('input').val('');

        // Trigger filtering
        $search.find('input').trigger('keydown').trigger('keyup');

      // If search field just opened
      } else {

        // Focus on search field
        $search.find('input').focus();

      }

    });

  });

  // The function

  function filter(action, filterID) {

    // Define allowed actions
    if (action !== 'next' && action !== 'previous' && action !== 'jump' && action !== 'search') { return; }

    // Get main elements
    var $content = $('.js-filter-content').filter('[data-filter-id="' + filterID + '"]');
    var $paginator = $('.js-filter-paginator').filter('[data-filter-id="' + filterID + '"]');
    var $search = $('.js-filter-search').filter('[data-filter-id="' + filterID + '"]');
    var $nextPage = $paginator.find('.js-filter-next');
    var $prevPage = $paginator.find('.js-filter-previous');
    var $currentPage = $paginator.find('.js-filter-current');

    // Let's get the data
    var urlBase = $paginator.attr('data-pagination-url');
    var searchVal = $search.find('input').val();
    var query = searchVal === '' ? '&q=' : '&q=' + encodeURIComponent(searchVal);
    var pageNumber;

    // Define page number based on the action
    if (action === 'next' && $nextPage.length > 0 && $nextPage.attr('href') !== '') {
      pageNumber = $nextPage.attr('href');
    } else if (action === 'previous' && $prevPage.length > 0 && $prevPage.attr('href') !== '') {
      pageNumber = $prevPage.attr('href');
    } else if (action === 'jump' && !isNaN($currentPage.val())) {
      pageNumber = $currentPage.val();
    } else if (action === 'search') {
      pageNumber = 1;
    } else {
      return;
    }

    // Create the complete URL
    var page = '&p=' + pageNumber;
    var url = urlBase + page + query;

    // Let's set search active if needed
    if (searchVal === '') {
      $search.removeClass('search-active');
    } else {
      $search.addClass('search-active');
    }

    ajaxRequest = $.get(url)
    .success(function (data) {

      // Replace paginator
      $paginator.replaceWith($(data).filter('.js-filter-paginator'));

      // If filtering is active
      if ($search.hasClass('search-active')) {

        // Replace content and always disable sortables
        $content.replaceWith($(data).filter('.js-filter-content').removeClass('sortable'));

      // If filtering is not active
      } else {

        // Replace content
        $content.replaceWith($(data).filter('.js-filter-content'));

        // Reload sortables if needed
        if ($(data).filter('.js-filter-content').hasClass('sortable')) {
          reloadSortables();
        }

      }

      // Adjust layout
      adjustLayout();

    })
    .complete(function () {

      // Remove searching class
      if ($search.hasClass('filter-searching')) {
        $search.removeClass('filter-searching');
      }

      // Set ajaxRequest to false
      ajaxRequest = false;

    });

  }

}

/*=========================================================
  Add/Remove attachments
=========================================================*/

addremAttachments();
function addremAttachments() {
  
  var attList = '#attachment-list',
      attField = '#add-attachment',
      addButton = '#add-attachment-button',
      removeButton = attList + ' .remove';

  // Add attachment functionality
  $('body').on('click', addButton, function (e) {
      e.preventDefault();
      // Define the attachment name & appendable attachment item
      var attName = $.trim($(attField).val()),
          $attItem = $('<li><span class="title"><a href="' + attName + '">' + attName + '</a></span><span class="remove"></span><input type="hidden" name="attachment[]" value="' + attName + '" /></li>');
      $attItem.find('a').attr('target', '_blank');
      // If attachment field is not empty
      if (attName != '') {
        // Append attachment item to attachment list
        $(attList).find('ul').append($attItem);
        $attItem.hide().fadeIn(200);
        // Reset input field value
        $(attField).val('');
      }
  });

  // Extend adding funtionality to enter keypress
  $('body').on('keydown', attField, function (e) {
    if (e.keyCode == 13) {
      e.preventDefault();
      $(addButton).trigger('click');
      return false;
    }
  });

  // Removing attachments
  $('body').on('click', removeButton, function (e) {
      e.preventDefault();
      $(this).closest('li').fadeOut(200, function () {
        $(this).closest('li').remove();
      });
  });
  
}

/*=========================================================
  Colorpicker
=========================================================*/

colorselector();
function colorselector() {

  // Set classes and ids used in color selector
  var color = '.color',
      cs = '.color-selector',
      csTitle = cs + ' .title'
      csItemWrap = cs + ' .color-item-wrap',
      csItem = cs + ' .color-item',
      csColorTitleBox = cs + ' .active-color',
      csActiveColor = cs + ' .active-color .color-indicator',
      csTitleInput = cs + ' .active-color input'
      csActions = cs + ' .actions',
      csSave = cs + ' .actions .save',
      csCancel = cs + ' .actions .cancel',
      csClose = cs + ' .close',
      networkCanvas = '#network-canvas';

  // Inner function for transforming RGB values to HEX values
  function rgb2hex(rgb) {
    if (rgb === undefined) { return; }
    rgb = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
    function hex(x) { return ('0' + parseInt(x).toString(16)).slice(-2); }
    return '#' + hex(rgb[1]) + hex(rgb[2]) + hex(rgb[3]);
  }

  //
  // Toggle selector
  //

  $('body').on('click', color, function () {

    $target = $(this);

    //if colorpicker is disabled with explit flag or itme is in network canvas
    //don't open colorpicker
    if (($target.hasClass('disable-color')) || ($target.closest(networkCanvas).length)){
        return;
    }

    if ($target.hasClass('active')) {

    $target.removeClass('active');
    $(cs).hide();

    } else {

    $(color).filter('.active').removeClass('active');
    $target.addClass('active');

    // Make sure the element's height and width can be calculated
    $(cs).css({'display': 'block', 'visibility': 'hidden', 'position': 'absolute'});

    // Get the needed values for positioning
    var targetHeight = $target.outerHeight(true),
        targetWidth = $target.outerWidth(true),
        targetLeft =  $target.offset().left,
        targetTop =  $target.offset().top,
        csTitleHeight = $(csTitle).outerHeight(true),
        left = targetLeft + targetWidth + 15,
        top = targetTop;
    
    // If target element's height is smaller than colorpickers title block
    if (targetHeight < csTitleHeight) {
        top = targetTop - ((csTitleHeight - targetHeight) / 2);
    }

    // Show and position the colorpicker
    $(cs).css({'visibility': 'visible', 'left': left, 'top': top });

    // Get target's color HEX and title
    var targetColorHEX = rgb2hex($target.children().css('background-color')),
        targetColorTitle = $target.attr('title') ? $.trim($target.attr('title')) : '';

    // Set colorpicker values according to the clicked element
    $(csTitleInput).val(targetColorTitle);
    $(csActiveColor).css('background-color', targetColorHEX);

    // Remove active class from active item
    $(csItemWrap).filter('.active').removeClass('active');

    // Set active class to correct item
    $(csItemWrap).each(function () {
        var csColorHEX = rgb2hex($(this).children().css('background-color'));
        if (csColorHEX === targetColorHEX) {
        $(this).addClass('active');
        }
    });

    // If the target's color exists inside color swatch
    if ($(csItemWrap).filter('.active').length) {

        // Add class to show actions and color title
        $(cs).addClass('activeColor');

    // If the target's color does not exist inside color swatch
    } else {

        // Remove class to show actions and color title
        $(cs).removeClass('activeColor');
    }
    
    }


  });

  //
  // Extend toggle to close and cancel buttons
  //

  $('body').on('click', csClose + ',' + csCancel, function () {
    $(color).filter('.active').trigger('click');
  });

  //
  // Pick a color
  //

  $('body').on('click', csItemWrap, function () {
    if (!$(this).hasClass('active')) {

      // Add class to show actions and color title
      $(cs).addClass('activeColor');

      // Make the chosen element active
      $(csItemWrap).filter('.active').removeClass('active');
      $(this).addClass('active');

      // Get color HEX and title
      var colorHEX = rgb2hex($(this).children().css('background-color')),
          colorTitle = $(this).attr('title') ? $.trim($(this).attr('title')) : '';

      // Set the title & color
      $(csTitleInput).val(colorTitle);
      $(csActiveColor).css('background-color', colorHEX);

    }
  });

  //
  // Save color
  //

  $('body').on('click', csSave, function () {

    // Get color data & sanitize it
    var colorHEX = rgb2hex($(csActiveColor).css('background-color')),
        colorTitle = $(csTitleInput).val()
        itemID = $('.color').filter('.active').attr('data-color-item-id'),
        itemType = $('.color').filter('.active').attr('data-color-item-type');

    // Save color data
    $.post('/ajax/color/', {'i':itemID, 't':itemType, 'title':colorTitle, 'rgb':colorHEX})
      .success(function (data) {

        // Update the target element's color
        $(color).filter('.active').children().css('background-color', colorHEX);

        // Update color title to color selector's active item
        $(csItemWrap).filter('.active').attr('title', colorTitle);

        // Update color title to all matching color items
        $(color).each(function () {
          var targetColorHEX = rgb2hex($(this).children().css('background-color'));
          if (targetColorHEX === colorHEX) {
            $(this).attr('title', colorTitle);
          }
        });

      });

  });

}


/*=========================================================
  Modal windows init
=========================================================*/

$(document).on('click', '.modalWindow', function (event) {
  event.preventDefault();

  if (!$(this).hasClass('modalWindowActive')) { 

    // Set flag for determining already bound modal window instances
    $(this).addClass('modalWindowActive');

    // Bind modal window function
    $(this).colorbox({
      transition: 'elastic',
      iframe: true,
      fastIframe: false,
      scrolling: false,
      innerWidth: '500px',
      innerHeight: '550px',
      initialWidth: '100px',
      initialHeight: '100px',
      opacity: 0.5,
      onLoad: function() {
        $('#cboxClose').hide();
      },
      onComplete: function() {
        $('#cboxClose').fadeIn(400);
      }
    });

    // Trigger click
    $(this).trigger('click');

  }

});

/*=========================================================
  Tab functionality
=========================================================*/

$(document).on('click', '.tab', function() {
  var $tab = $(this);
  var $tabContent = $('.tab-content[data-tab-id="' + $tab.attr('data-tab-id') + '"]');
  if ($tab.hasClass('active')) { return; }
  $('.tab.active, .tab-content.active').removeClass('active');
  $tab.addClass('active');
  $tabContent.addClass('active');
  adjustLayout();
});

// Add url parameter "&t=x" on submitting action form 
$(document).on('submit', '.archive-actions-form', function () {
  var $activeTab = $('.tab.active');
  var $form = $(this);
  if ($activeTab.length === 1) {
    var tabID = $activeTab.attr('data-tab-id');
    $form.attr('action', $form.attr('action') + '&t=' + tabID);
  }
});

// Check if page has url parameter "t" and change the tab accordingly
tabURL();
function tabURL() {
  var tabID = getURLParameter('t');
  if (tabID !== null) {
    var $tab = $('.tab[data-tab-id="' + tabID + '"]');
    if ($tab.length === 1) {
      $tab.trigger('click');
    }
  }
  function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null;
  }
}

/*=========================================================
  Save learning network data
=========================================================*/

$('body').on('click', '#save-network', function (e) {

  // Save learning network item data to #network-canvas element
  $.fn.networkCanvas('saveData');

  // Add the data to #network-data input field
  $('#network-data').val($('#network-canvas').data('itemData'));

});


//
// END SCRIPT
//
});
