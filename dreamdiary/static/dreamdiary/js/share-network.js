$(function () {

/*=========================================================
  Store active items in activeItems variable
=========================================================*/

var activeItems = [];
$('#selected-items .item').each(function (i) {
  activeItems.push($(this).attr('data-id'));
});

/*=========================================================
  Highlight selected groups
=========================================================*/

highlightActiveItems();
function highlightActiveItems() {

  // Add active classes to active items in #all-items list
  $('#all-items .item').each(function (i) {
    if($.inArray($(this).attr('data-id'), activeItems) != -1) {
      $(this).addClass('active');
     } else {
      $(this).removeClass('active');
    }
  });

}

/*=========================================================
  Update active item data
=========================================================*/

function updateActiveItems() {
  
  // Update the activeItems array
  activeItems = [];
  $('#selected-items .item').each(function (i) {
    activeItems.push($(this).attr('data-id'));
  });

  // Update #selected-counter count
  $('#selected-counter').html(activeItems.length);

  // Add flag to body if there are no active shares
  if (activeItems.length > 0) {
    $('body').removeClass('not-shared');
  } else {
    $('body').addClass('not-shared');
  }

}

/*=========================================================
  Switch views
=========================================================*/

// Switch views between #all-items list & #selected-items list
$(document).on('click', '#select-view .action', function () {
  if ($(this).hasClass('selected-items')) {
    $('body').removeClass('show-all-items').addClass('show-selected-items');
  } else {
    $('body').removeClass('show-selected-items').addClass('show-all-items');
  }
});

/*=========================================================
  Select/unselect #active-items list items
=========================================================*/

$(document).on('click', '#all-items .item', function () {

  // Select item
  if (!$(this).hasClass('active')) {

    // Append a clone of the item to selected list
    $('#selected-items .item-list').append($(this).clone());

    // Add active class
    $(this).addClass('active');

    updateActiveItems();

  // Unselect item
  } else {
    
    // Remove the item from #selected-items list
    $('#selected-items .item').filter('[data-id="' + $(this).attr('data-id') + '"]').remove();

    // Remove active class
    $(this).removeClass('active');

    updateActiveItems();

  }

});

/*=========================================================
  Remove item from #selected-items list
=========================================================*/

$(document).on('click', '#selected-items .item .action', function () {

    // Remove active class from the matching item in #all-items list
    $('#all-items .item').filter('[data-id="' + $(this).closest('.item').attr('data-id') + '"]').removeClass('active');

    // Remove the item from #selected-items list
    $(this).closest('.item').remove();

    updateActiveItems();

});

/*=========================================================
  Item list - pagination & filtering
=========================================================*/

filtering();
function filtering() {

  //
  // Globals
  //

  var searchTimeout = false;
  var ajaxRequest = false;

  //
  // Listeners
  //

  // Next/previous page action
  $(document).on('click', '.pagination .next, .pagination .previous', function (e) {
    e.preventDefault();
    changePage($(this).attr('href'));
  });

  // Go to page action
  $(document).on('submit', '.pagination form', function (e) {
    e.preventDefault();
    var pageNumber = $(this).find('input').val();
    if (!isNaN(pageNumber)) {
      changePage(pageNumber);
    }
    return false;
  });

  // Searching
  $(document)
  .on('submit', '.filtering .search form', function (e) {

    e.preventDefault();
    return false;

  })
  .on('keydown', '.filtering .search input', function (e) {

    var $search = $(this).closest('.search');

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
    if ($search.hasClass('searching')) {
      $search.removeClass('searching');
    }

  })
  .on('keyup', '.filtering .search input', function (e) {

    // Start filtering after a comfortable timeout
    e.preventDefault();
    var $search = $(this).closest('.search');
    searchTimeout = setTimeout(function () {
      $search.addClass('searching');
      changePage(1);
    }, 200);

  });

  //
  // Functions
  //

  function changePage(pageNumber) {

    // Get some data (notice the ternary operators)
    var $pagination = $('.pagination'),
        $list = $('#all-items ul.item-list'),
        $search = $('.filtering .search'),
        urlBase = $pagination.attr('data-pagination-url'),
        page = '&p=' + pageNumber,
        searchQuery = ($search.find('input').val() !== '') ? '&q=' + encodeURIComponent($search.find('input').val()) : '&q=',
        url = urlBase + page + searchQuery;

    ajaxRequest = $.get(url)
    .success(function (data) {

      // Replace the old page with the new page
      $pagination.replaceWith($(data).filter('.pagination'));
      $list.replaceWith($(data).filter('ul'));

    })
    .complete(function () {

      // Remove searching class
      if ($search.hasClass('searching')) {
        $search.removeClass('searching');
      }

      // Set ajaxRequest to false
      ajaxRequest = false;

    });

  }

}

/*=========================================================
  Save groups
=========================================================*/

$(document).on('click', '#share-to-groups', function () {

  // Append a hidden input for each selected group
  var $this = $(this);
  if ($('#selected-items .item').length){
    $('#selected-items .item').each(function () {
      $this.after('<input type="hidden" name="l[]" value="' + $(this).attr('data-id') + '" />');
    });
  }
  else{
    $this.after('<input type="hidden" name="l[]" value="" />');
  }

});


//
// END SCRIPT
//
});
