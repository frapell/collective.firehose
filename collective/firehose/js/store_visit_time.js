
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
        var params = {'visited_time':active_time};
        
        // Chrome needs this to be asynchronous to work 
        $.ajax({ 
                async: false,
                type: "POST", 
                url: url, 
                data: params, 
                timeout: 500,
                success: function(msg){ 
                        //None 
                    } 
                }); 
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