function LaunchContainerEditBlock(runtime, element) {

    console.log($('.xblock-save-button', element));

    function notify(response) {
        var $notificationEl = $('#notification-message'); 

        if (response.result === 'success') {
          $notificationEl.addClass('success');
          $notificationEl.html('It worked!');
        }
        else {
          $notificationEl.addClass('error');
          $notificationEl.html("It didn't work! "+response.result); 
        }
    }

    $('.save-button', element).bind('click', function() {
        var handlerUrl = runtime.handlerUrl(element, 'studio_submit');
        var data = {
            'project': $('input[name=project]').val(),
            'project_friendly': $('input[name=project_friendly]').val(),
            'project_token': $('input[name=project_token]').val(),
        };

        $.post(
            handlerUrl, 
            JSON.stringify(data))
          .done(function(response) { 
              notify(response);
        });
    });

    $('.cancel-button', element).bind('click', function() {
//        runtime.notify('cancel', {});
    });
}

