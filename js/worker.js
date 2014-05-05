var PIXEL_WIDTH = 7;
var PIXEL_HEIGHT = 7;
var DRAW = 0;
var ERASE = 1;

var mode = DRAW;

var canvas = $('#canvas');
var selMode = false;
var sel = [];
var prevSel = [];
var nodes = [];
var id;

$.get('http://crowdimage.herokuapp.com/api/getblock/', function(data) {
  id = data.id;
  $('#blockid').html(data.id);

  canvas.css({
    width: PIXEL_WIDTH * data.width,
    height: PIXEL_HEIGHT * data.height
  });

  for (var x=0; x<data.height; x++) {
    nodes[x] = [];
    for (var y=0; y<data.width; y++) {
      var pixel = $('<div>');
      pixel.addClass('pixel');
      pixel.css({
        top: y*PIXEL_HEIGHT + 'px',
        left: x*PIXEL_WIDTH + 'px',
        width: PIXEL_WIDTH + 'px',
        height: PIXEL_HEIGHT + 'px',
        backgroundColor: '#' + data.pixels[y][x][0]
      });
      if (data.pixels[y][x][1]) {
        pixel.addClass('selected');
        pixel.data('selected', true);
        sel.push([x,y]);
      } else {
        pixel.data('selected', false);
      }
      pixel.data('x', x);
      pixel.data('y', y);
      canvas.append(pixel);
      nodes[x].push(pixel);
    }
  }
});

canvas.on('mousedown', '.pixel', function() {
  selMode = true;
  var x = $(this).data('x');
  var y = $(this).data('y');
  select(x,y);
});

$('html').on('mouseup', function() {
  selMode = false;
  prevSel = [];
});

canvas.on('mousemove', '.pixel', function(e) {
  e.preventDefault();

  var x = $(this).data('x');
  var y = $(this).data('y');

  if(!selMode) return;

  // make it selected

  var line;
  if (prevSel.length > 0) {
    line = interpolate([x,y], prevSel);
  } else {
    line = [[x,y]];
  }

  for (var i=1; i<line.length; i++) {
    select(line[i][0], line[i][1]);
  }

  prevSel = [x,y];
});

function select(x,y) {
  var node = nodes[x][y];

  if (mode == ERASE) {
    node.data('selected', false);
    node.removeClass('selected');
    sel.splice(sel.indexOf([x,y]), 1);
  } else if (mode == DRAW) {
    node.data('selected', true);
    node.addClass('selected');
    sel.push([x,y]);
  }
}

function interpolate(a,b) {
  var x0 = a[0];
  var y0 = a[1];
  var x1 = b[0];
  var y1 = b[1];
  var dx = Math.abs(x1-x0);
  var dy = Math.abs(y1-y0);
  var sx = (x0 < x1) ? 1 : -1;
  var sy = (y0 < y1) ? 1 : -1;
  var err = dx-dy;
  var result = [];

  while(true){
    result.push([x0,y0]);

    if ((x0==x1) && (y0==y1)) break;
    var e2 = 2*err;
    if (e2 >-dy){ err -= dy; x0  += sx; }
    if (e2 < dx){ err += dx; y0  += sy; }
  }

  return result;
}

function switchMode(mode) {
  window.mode = mode;
  if (mode == DRAW) {
    $('#canvas').css('cursor', 'url(../img/cursor-pencil.png), auto');
  } else if (mode == ERASE) {
    $('#canvas').css('cursor', 'url(../img/cursor-eraser.png), auto');
  }
}

function getMatrix() {
  var array = [];
  for (var i=0; i<100; i++) {
    var row = [];
    for (var j=0; j<100; j++) {
      row.push(nodes[j][i].data('selected') ? 1 : 0);
    }
    array.push(row);
  }
  return array;
}

function submit() {
  var payload = {
    id: id,
    pixels: JSON.stringify(getMatrix())
  };
  $.ajax({
    url: 'http://jackmontgomery.io/crowdimage/api/returnblock',
    data: payload,
    type: 'POST',
    success: function(data) {
      window.location('index.html#worked');
    }
  });
}

app = new CIWorker({
  canvas: $('#canvas')
});