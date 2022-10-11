
var endpoint = 'http://localhost:5000/'



async function initDash() {
    await sleep(1000); // annoying but necessary maybe add a loading wheel??
    simpleRequest('getComponents');
    simpleRequest('updateComponents');
}


function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}


function eventCheckBox(e) {
    if ($('#all').is(':checked')) {
        console.log('change');
        $('.rows').find('input[type="checkbox"]').prop('checked', true);
    } else {
        $('.rows').find('input[type="checkbox"]').prop('checked', false);
    }
}



function simpleRequest(url_) {
    $.ajax({
        method: 'GET',
        url: endpoint + url_,
        processData: false,  // tell jQuery not to process the data
        contentType: false,   // tell jQuery not to set contentType
        success:function(response)
        {
            console.log(response)
        }
        });
}

function simpleForm(url_, id_) {
    var form = $(id_)[0];
    var fd = new FormData(form)
    $.ajax({
        method: 'POST',
        url: url_,
        data: fd,
        processData: false,  // tell jQuery not to process the data
        contentType: false,   // tell jQuery not to set contentType
        success:function(response)
        {
            console.log(response)
        }
        });
}





