var app = new CISubmit({
  canvas: $('#sub-img'),
  fileinput: $('#img-input')
});

$('#screen1-upload').show();

$('#img-input').on('dragover', function(e) {
  $('#img-input-overlay').addClass('over');
  $('#img-input-overlay p').html('release!');
});

$('#img-input').on('dragleave', function(e) {
  $('#img-input-overlay').removeClass('over');
  $('#img-input-overlay p').html('drag and drop a photo here');
});

$("#img-input").change(function() {
  $('.screen').css('-webkit-transition', '-webkit-transform 0.4s, opacity 0.4s');
  $('#screen1-upload').addClass('away');
  $('#screen2-draw').removeClass('initial');
});

function step3() {
  // make sure polygon is good
  var poly = [];
  poly = poly.concat.apply(poly, app.getPixels());

  if (poly.length < 6 || !PolyK.IsSimple(poly)) {
    $('#badModal').modal();
    return;
  }

  $('#screen2-draw').addClass('away');
  $('#screen3-info').removeClass('initial');
}

$('#submit-form').submit(function(e) {
  e.preventDefault();
  formData = new FormData(this);
  formData.append('selectedPixels',JSON.stringify(app.getPixels()));
  $.ajax( {
    url: 'http://jackmontgomery.io/crowdimage/api/submitpic',
    type: 'POST',
    data: formData,
    processData: false,
    contentType: false,
    success: function(data) {
      window.location = 'index.html#submitted';
    }
  });
});