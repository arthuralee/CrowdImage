var CISubmit = function(options) {
  this.fileinput = options.fileinput;
  this.canvas = options.canvas.get(0);

  this.init();
};

CISubmit.prototype.init = function() {
  this.stage = new createjs.Stage(this.canvas);
  this.width = this.canvas.width;
  this.height = this.canvas.height;
  this.points = [];

  // Bind events
  var _this = this;
  $("#img-input").change(function(){
    _this.loadImage(this);
  });
};

CISubmit.prototype.loadImage = function(input) {
  var _this = this;
  if (input.files && input.files[0]) {
    var reader = new FileReader();

    reader.onload = function (e) {
      var image = new Image();
      image.src = e.target.result;
      image.onload = function() {
        _this.displayImage(this);
      }
    }
    reader.readAsDataURL(input.files[0]);
  }
}

CISubmit.prototype.displayImage = function(img) {
  ri = img.width/img.height;
  rf = this.width/this.height;

  var scale = rf > ri ? this.height/img.height : this.width/img.width;

  this.bitmap = new createjs.Bitmap(img);
  this.bitmap.scaleX = scale;
  this.bitmap.scaleY = scale;
  this.bitmap.y = (this.height - img.height*scale)/2;
  this.bitmap.x = (this.width - img.width*scale)/2;
  this.addClickHandler(this.bitmap);
  this.stage.addChild(this.bitmap);
  this.stage.update();
};

CISubmit.prototype.addClickHandler = function(bitmap) {
  var _this = this;
  bitmap.on('click', function(e) {
    var currPoint = {x: e.stageX, y: e.stageY};

    var circle = new createjs.Shape();
    circle.graphics.beginFill('red').drawCircle(0, 0, 4);
    circle.x = currPoint.x;
    circle.y = currPoint.y;
    _this.stage.addChild(circle);

    currPoint.circle = circle;

    _this.points.push(currPoint);
    _this.updateCanvas();
  });
};

CISubmit.prototype.updateCanvas = function() {
  if (this.sel) this.stage.removeChild(this.sel);

  this.sel = new createjs.Shape();
  this.sel.graphics.setStrokeStyle(2);
  this.sel.graphics.beginStroke('black');
  this.sel.graphics.beginFill('rgba(100,100,255,0.5)');

  if (this.points.length > 0) {
    this.sel.graphics.moveTo(this.points[0].x, this.points[0].y);
  }

  for (var i=0; i<this.points.length; i++) {
    var point = this.points[i];

    if (i+1 < this.points.length) {
      var nextPoint = this.points[i+1];
      this.sel.graphics.lineTo(nextPoint.x, nextPoint.y);
    }
  }

  //this.sel.graphics.closePath();
  this.stage.addChild(this.sel);
  this.stage.update();
};

CISubmit.prototype.undo = function() {
  var latestPoint = this.points[this.points.length - 1];
  latestPoint.circle.graphics.clear();
  this.points.pop();
  this.updateCanvas();
};

CISubmit.prototype.getPixels = function() {
  return this.points.map(function(point) {
    return [Math.round((point.x - this.bitmap.x) / this.bitmap.scaleX),
            Math.round((point.y - this.bitmap.y) / this.bitmap.scaleY)];
  }.bind(this));
};