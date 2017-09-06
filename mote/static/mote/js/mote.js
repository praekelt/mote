'use_strict()';

// States for the iframe resize handle.
var drag_active = false;
var drag_element = '';

var progress_a = 0;
var progress_b = 0;
var progress_c = 0;
var progress_d = 0;

$(document).ready(function() {

    /* ---- Initialisers ---- */

    // Get a list of breakpoints from the DOM
    var breakpoints = [];
    $("#pick-breakpoint option").each(function(){
        breakpoints.push(parseInt($(this).val()));
    });
    breakpoints.sort(function(a, b){return a-b});

    var highest = breakpoints[breakpoints.length-1];
    var lowest = breakpoints[0];

    // Set initial width based on window size
    var width = Math.round($(".iframe").width());
    update_global_status(width);
    $(".iframe").each(function(){
      update_iframe_status($(this), width);
    });

    /* --- END Initialisers --- */


    /* ---- Event bindings ---- */

    // Toggle iFrame media query
    $(".iframe-opt").on("click", function(){
        var menu = $(this).parent().find(".iframe-opt-menu");
        var iframe = $(this).parent().find(".iframe");

        menu.toggleClass("active");

        $(this).toggleClass("active");
        menu.find("li").on("click", function(){
            var size = $(this).data("size");
            iframe.stop().animate({width:size}, 300);
            $(this).parent().children().removeClass("active");
            $(this).addClass("active");
            update_iframe_status(iframe, size);
        });
    });

    // Refresh iFrame
    $(".iframe-refresh").on("click", function(){
        var iframe = $(this).parent().find("iframe");
        iframe.attr("src", iframe.attr("src"));
    });

    // Toogle iframe versions
    $("#pick-version").on("change", function(){
      var version = $(this).val();
      $("iframe").each(function(){
        var src = this.src.slice(0, this.src.indexOf("?"));
        this.src = src + "?version=" + version;

        $(this).closest('.sg-wrapper')
            .find('.link-out')
            .attr('href', src + "?version=" + version);
      });
    });

    // Toggle global iframe width
    $("#global-px").on("keyup", function(){
      var pixels = $(this).val();
      $(".iframe").width(pixels);
      $(".iframe").each(function(){
        update_iframe_status($(this), pixels);
      });
      update_global_status(pixels);
    });

    // Toggle global breakpoints
    $("#pick-breakpoint").on("change", function(){
      var pixels = $(this).val();
      console.log(pixels);
      $(".iframe").stop().animate({width:pixels}, 300);
      $(".iframe").each(function(){
        update_iframe_status($(this), pixels);
      });
      update_global_status(pixels);
    });

    $("#global-em").on("keyup", function(){
      var pixels = em_to_px($(this).val());
      $(".iframe").width(pixels);
      $(".iframe").each(function(){
        update_iframe_status($(this), pixels);
      });
      update_global_status(pixels);
    });

    // Reset button
    $("#breakpoint-reset").on("click", function(evt){
      evt.preventDefault();
      $(".iframe").css("width", "100%");
      var width = Math.round($(".iframe").width());
      update_global_status(width);
      $(".iframe").each(function(){
        update_iframe_status($(this), width);
      });
    });

    // Random button
    $("#breakpoint-random").on("click", function(evt){
      evt.preventDefault();
      var rand = Math.round(Math.random()*(highest-lowest)+lowest);
      $(".iframe").animate({"width": rand}, 300);
      var width = Math.round($(".iframe").width());
      update_global_status(width);
      $(".iframe").each(function(){
        update_iframe_status($(this), width);
      });
    });

    // Resizeable iframe
    $(".handle").on("mousedown", function(evt){
        drag_element = $(this).parent();
        drag_active = true;
        $(this).addClass("active");
        // Disable pointer events in iframes while user resizes
        drag_element.find("iframe").css("pointer-events", "none");
    });

    $(document).on("mouseup", function(evt){
        drag_active = false;
        $("iframe").css("pointer-events", "auto");
        $(".handle").removeClass("active");
    });

    $(document).on("mousemove", function(evt){
        if (drag_active){
            var offset = element_position(drag_element.get(0));
            var mouseX = evt.pageX - offset.x - 5 ;
            drag_element.width(mouseX);
            update_iframe_status(drag_element, mouseX);
        }
    });

    // On Preview click. Use JS API to re-render the iframe.
    $("form.Preview button").on("click", function(evt){
        evt.preventDefault();
        // todo: fetch api url from DOM in case of versioning
        var mote_api = new MoteAPI('/mote/api/');
        var button = $(evt.target);
        try {
            var data = JSON.parse(button.prev().val());
        }
        catch(err) {
            alert('We are unable to parse the value you have entered.');
        }
        mote_api.push(
            button.data('dotted-name'),
            data,
            null,
            function(result) {
                var pattern = button.closest('.Pattern');
                var iframe = $('iframe', pattern);
                iframe.contents().find('body').html(result.rendered);
            }
        );
        mote_api.run();
    });

    /* --- END Event Bindings --- */


    /* ---- DOM manipulation ---- */

    // Sticky Elements
    // var toolbarHeight = Math.ceil($('.toolbar').outerHeight());

    $('.toolbar').stick_in_parent();

    //$('[role="sidebar"]').stick_in_parent({
    //    offset_top: toolbarHeight + Math.ceil((($('main').outerHeight() - $('main').height()) / 2))
    //});

    // Toggle Hidden Areas

    $('.sg-hidden-area').each(function() {
        $(this).hide();
    });

    $(document).on('click', '.sg-hidden-area-toggler', function(e) {

        e.preventDefault();

        var target = $(this).attr('href');

        console.log(target);

        if ( $(this).hasClass('off') ) {
            $(this).addClass('on')
                .removeClass('off');

            $(target).slideToggle('open');
        } else if ( $(this).hasClass('on') ) {
            $(this).addClass('off')
                .removeClass('on');

            $(target).slideToggle('close');
        }
    });

    // Live Search
    $('.sidebar-search [type="search"]').hideseek({
        list: '.search-list',
        hidden_mode: true,
        navigation: true
    });

    // Sortable Menu System
    // var top_list = $('#sidebar-nav')[0];
    // var sortable = Sortable.create(top_list, {
    //     onUpdate: function (/**Event*/evt) {
    //         reSort();
    //     },
    // });

    // var child_list = $('#sidebar-nav a.active').next()[0];
    // var sortable = Sortable.create(child_list, {
    //     onUpdate: function (/**Event*/evt) {
    //         reSort();
    //     }
    // });

    function reSort(){

        var library = $('body').data('library');

        var list = {};

        $('#sidebar-nav>li>a').each(function(){
            var category = $(this).html();
            list[category] = [];
            $(this).next().find('li a').each(function(){
                list[category].push($(this).html());
            });
        });

        list = JSON.stringify(list);

        console.log(list);

        $.ajax({
            type: "POST",
            url: "/sort_menu/",
            data: { "pattern_list": list, "library": library}
        })
        .done(function(msg) {
            console.log(msg);
        });
    }

    /* --- END DOM manipulation --- */

    // apply progress graph stats

    var total_progress = progress_a + progress_b + progress_c + progress_d;
    progress_a = Math.round((progress_a / total_progress) * 100);
    progress_b = Math.round((progress_b / total_progress) * 100);
    progress_c = Math.round((progress_c / total_progress) * 100);
    progress_d = Math.round((progress_d / total_progress) * 100);

    while ((progress_a + progress_b + progress_c + progress_d) < 100){
      if (progress_a !== 0){ progress_a += 1;}
      else if (progress_b !== 0){ progress_b += 1;}
      else if (progress_c !== 0){ progress_c += 1;}
      else { progress_d += 1;}
    }

    while ((progress_a + progress_b + progress_c + progress_d) > 100){
      if (progress_a !== 0){ progress_a -= 1;}
      else if (progress_b !== 0){ progress_b -= 1;}
      else if (progress_c !== 0){ progress_c -= 1;}
      else { progress_d -= 1;}

    }

    $('.bar.ready').css('width', (progress_a * 5) + 5);
    $('.bar.refactor').css('width', (progress_b * 5) + 5);
    $('.bar.wip').css('width', (progress_c * 5) + 5);
    $('.bar.deprecated').css('width', (progress_d * 5) + 5);

    // Iframe Variation Toggle
    $('.iframe-variation-toggler').on('change', function() {
        var targetIframe = $(this).data('target');
        var value = $(this).val();

        $(targetIframe).attr('src', $(this).val());
        $('[data-linksto="' + targetIframe + '"]').attr('href', $(this).val());
    });

}); // $(document).ready();

// Updates the px/em tag on iframes
function update_iframe_status(elem, width){
    $(elem).find("#pixels").html(width);
    $(elem).find("#rems").html(px_to_em(width));
}

// Updates the px/em fields on the toolbar
function update_global_status(width) {
  $("#global-px").val(width);
  $("#global-em").val(px_to_em(width));
}

// Converts pixels to ems
function px_to_em(input) {
    //var emSize = parseFloat($("body").width());
    //return Math.round((input / emSize) * 100) / 10;
    return Math.round((input/16) * 10)/10;
}

// Converts ems to px
function em_to_px(input) {
    return Math.round((input*16) * 10)/10;
}

// Calculates an elements offset for relative mouse positioning
function element_position(e) {
  var x = 0, y = 0;
  var inner = true ;
  do {
      x += e.offsetLeft;
      y += e.offsetTop;
      var style = getComputedStyle(e,null) ;
      var borderTop = getNumericStyleProperty(style,"border-top-width") ;
      var borderLeft = getNumericStyleProperty(style,"border-left-width") ;
      y += borderTop ;
      x += borderLeft ;
      if (inner){
        var paddingTop = getNumericStyleProperty(style,"padding-top") ;
        var paddingLeft = getNumericStyleProperty(style,"padding-left") ;
        y += paddingTop ;
        x += paddingLeft ;
      }
      inner = false ;
  } while (e = e.offsetParent);

  return { x: x, y: y };
}

// Returns a numeric style property for use in offset calculations
function getNumericStyleProperty(style, prop){
  return parseInt(style.getPropertyValue(prop),10);
}

// Toggles state tags for patterns
function getState(pattern){

    // var div = $('#'+pattern);
    // comment1 = div.contents().filter(function() {
    //     return this.nodeType === 8;
    // }).get(0);
    // comment2 = div.contents().filter(function() {
    //     return this.nodeType === 8;
    // }).get(1);
    //
    // var state = comment1.nodeValue;
    // var reason = comment2.nodeValue;
    // state = state.replace(' @State: ', '');
    // reason = reason.replace(' @Reason: ', '');
    // var tag = '';
    //
    // var menuitem = $('a[href*='+div.attr('id')+']').parent();
    //
    // switch(state){
    //     case "Needs Refactoring ":
    //       tag = div.find('.tag-warning');
    //       tag.css('display', 'inline-block');
    //       tag.find('.tooltip').html(reason);
    //       menuitem.addClass("orange");
    //       progress_a += 1;
    //       break;
    //     case "Production Ready ":
    //       tag = div.find('.tag-success');
    //       tag.css('display', 'inline-block');
    //       tag.find('.tooltip').html(reason);
    //       menuitem.addClass("green");
    //       progress_b += 1;
    //       break;
    //     case "Deprecated ":
    //       tag = div.find('.tag-danger');
    //       tag.css('display', 'inline-block');
    //       tag.find('.tooltip').html(reason);
    //       menuitem.addClass("red");
    //       progress_c += 1;
    //       break;
    //     case "Work in Progress ":
    //       tag = div.find('.tag-info');
    //       tag.css('display', 'inline-block');
    //       tag.find('.tooltip').html(reason);
    //       menuitem.addClass("blue");
    //       progress_d += 1;
    //       break;
    // }
}

// Ajax CSRF prep

function getCookie(name) {
var cookieValue = null;
if (document.cookie && document.cookie != '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) == (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
        }
    }
}
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

//Ajax call
function csrfSafeMethod(method) {
// these HTTP methods do not require CSRF protection
return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
