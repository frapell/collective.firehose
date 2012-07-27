
$(document).ready(function() {
    var url = window.location.href + '/@@store_hit';
    $.ajax({ 
            async: true,
            type: "POST", 
            url: url,  
            success: function(msg){ 
                    //None 
                } 
            }); 

});