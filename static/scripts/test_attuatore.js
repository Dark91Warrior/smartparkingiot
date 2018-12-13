$(document).ready(function () {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('result-yes-controllore').style.display = 'none';
    document.getElementById('result-no-controllore').style.display = 'none';
    document.getElementById('result-yes-sensori').style.display = 'none';
    document.getElementById('result-no-sensori').style.display = 'none';
    document.getElementById('buttonTest').style.display = 'none';
});

function test(parking) {
    document.getElementById('content').style.display = 'none';
    document.getElementById('content2').style.display = 'none';
    document.getElementById('fuori_servizio').style.display = 'none';
    document.getElementById('loading').style.display = 'block';

    var URL = "/arduino/attesa";

    $.ajax({
        type: 'post',
        url: URL,
        data: JSON.stringify({parking: parking}),
        contentType: "application/json",
        dataType: "json",
        success: function (resp) {
            var obj = resp;

            document.getElementById('loading').style.display = 'none';
            document.getElementById('buttonGestisci').style.display = 'none';
            document.getElementById('buttonTest').style.display = 'block';


            if (obj.controllore === 'YES' && obj.sensori === 'YES') {
                document.getElementById('result-yes-controllore').style.display = 'block';
                document.getElementById('result-no-controllore').style.display = 'none';
                document.getElementById('result-yes-sensori').style.display = 'block';
                document.getElementById('result-no-sensori').style.display = 'none';
            }
            else if (obj.controllore === 'NO' && obj.sensori === 'NO') {
                document.getElementById('result-yes-controllore').style.display = 'none';
                document.getElementById('result-no-controllore').style.display = 'block';
                document.getElementById('result-yes-sensori').style.display = 'none';
                document.getElementById('result-no-sensori').style.display = 'block';
            }
            else if (obj.controllore === 'YES' && obj.sensori === 'NO') {
                document.getElementById('result-yes-controllore').style.display = 'block';
                document.getElementById('result-no-controllore').style.display = 'none';
                document.getElementById('result-yes-sensori').style.display = 'none';
                document.getElementById('result-no-sensori').style.display = 'block';
            }
            else if (obj.controllore === 'NO' && obj.sensori === 'YES') {
                document.getElementById('result-yes-controllore').style.display = 'none';
                document.getElementById('result-no-controllore').style.display = 'block';
                document.getElementById('result-yes-sensori').style.display = 'block';
                document.getElementById('result-no-sensori').style.display = 'none';
            }
        },
        error: function (e) {
            alert('Error: ' + e);
        }
    });
}