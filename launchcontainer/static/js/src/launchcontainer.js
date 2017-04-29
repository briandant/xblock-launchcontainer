function getURLOrigin(path) {
    var link = document.createElement('a');
    link.setAttribute('href', path);

    port = (link.port) ? ':'+link.port : '';
    return link.protocol + '//' + link.hostname + port;
}

function LaunchContainerXBlock(runtime, element) {

    $(document).ready(
      function () {
        var $launcher = $('#launcher1'); 
        var $launch_button = $launcher.find('#launcher_submit');
        var $owner_email = "{{ user_email }}"; 
        if ($owner_email == "None") { 
          $launcher.find('#launcher_email').removeClass('hide');
        };

        $launch_button.click(function() {
            console.log('Clicked launch button');
            console.log($owner_email);
            $launch_button.attr('disabled', 'disabled').val('Launching...');
            if ($owner_email == undefined) { 
              console.log("yep it failed");
              var $owner_email = $launcher.find('#launcher_email').val();
            };
            $launcher.find('iframe')[0].contentWindow.postMessage({
                owner_email: $owner_email,
                project: "{{ project }}"
            }, "{{ API_url }}");
            return false;
        });
        window.addEventListener("message", function (event) {
            if (event.origin !== getURLOrigin('{{ API_url }}')) return;
            if(event.data.status === 'siteDeployed') {
                $launcher.html(event.data.html_content);
            } else if(event.data.status === 'deploymentError') {
                $launcher.text(event.data.error_message);
            }
        }, false);
    });

}
