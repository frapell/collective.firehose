
$(document).ready(function() {

    var isActive = true;
    var active_time = 0;
    var last_time = new Date().getTime();

    $(window).bind('focus', function(){
        isActive = true;
    })

    $(window).bind('blur', function(){
        isActive = false;
    })

    $(window).bind('unload', function(){
        var url = window.location.href + '/@@store_visit_time';
        $.post(url,
               {'visited_time':active_time},
               function(results){});
    })

    // test
    setInterval(function () { 
        var time_now = new Date().getTime();  
        if (isActive){
            active_time += time_now - last_time;
        } 
        last_time = time_now;     
    }, 1000);

});