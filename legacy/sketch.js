// An initial framework for procedurally generated landscapes in p5js
//
// By Jon Froehlich
// http://makeabilitylab.io/
//
// Based on:
//  - https://twitter.com/muted_mountains (follow them!)
//  - https://jonoshields.com/2017/03/29/creating-procedurally-generated-scenes/

let topColor;
let bottomColor;
let sun;
let mountainRanges = [];
let maxMountainRanges = 6;
let mountainClouds = [];

function setup() {
  createCanvas(windowWidth, windowHeight);
  colorMode(HSB, 255);

  topColor = getRandomTopBGColor();
  bottomColor = color(hue(topColor), saturation(topColor) * 0.9, brightness(topColor) * 1.5);
  sun = new Sun(topColor);

  for (let i = 0; i < maxMountainRanges; i++) {
    let mountainRange = new MountainRange(i, maxMountainRanges, topColor);
    mountainRanges.push(mountainRange);
  }
  
  let node = createDiv('<div id="hiddenColorDiv" style="visibility:hidden;position:absolute;z-index:4;"></div>');
  $('#hiddenColorDiv').css("color", bottomColor);

  smooth();
}

function draw() {
  drawBackground(topColor, bottomColor);
  sun.draw();

  // draw in reverse order (based on zindex)

  for (let i = mountainRanges.length - 1; i >= 0; i--) {

    let mountainRange = mountainRanges[i];
    mountainRange.draw();
  }

}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
}

function getRandomTopBGColor() {
  colorMode(HSB, 255);
  let hue = random(0, 255);
  return color(hue, 115, 150);
}

function drawBackground(top, bottom) {
  // p5js has very limited gradient fill support, so we actually
  // don't use p5js here, we use regular Canvas drawing
  // https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/createLinearGradient
  let ctx = drawingContext;
  let grd = ctx.createLinearGradient(0, 0, 0, width);
  grd.addColorStop(0, top);
  grd.addColorStop(0.4, bottom);

  let oldFillStyle = ctx.fillStyle; // save old fillstyle to reset
  ctx.fillStyle = grd;
  ctx.fillRect(0, 0, width, height);
  ctx.fillStyle = oldFillStyle;
}

class Shape {
  constructor(x, y, width, height, strokeColor, fillColor) {
    this.x = x;
    this.y = y;
    this.width = width;
    this.height = height;
    this.strokeColor = strokeColor;
    this.fillColor = fillColor;
    this.strokeWeight = 1;
  }

  getLeft() {
    return this.x;
  }

  getRight() {
    return this.x + this.width;
  }

  getBottom() {
    return this.y;
  }

  getTop() {
    return this.y + this.height;
  }

  contains(x, y) {
    return x >= this.x && // check within left edge
      x <= (this.x + this.width) && // check within right edge
      y >= this.y && // check within top edge
      y <= (this.y + this.height); // check within bottom edge
  }
}

class Sun extends Shape {

  constructor(baseColor) {
    let size = 50 + width * random(0.1, 0.3);
    let xLoc = width/2 + (size/4 + width/2)* random();
    let yLoc = size * random(-0.2, 0.5);
    super(xLoc, yLoc, size, size);

    this.fillColor = color(hue(topColor), saturation(topColor) * 0.9,
      brightness(topColor) * 1.6);
  }

  draw() {
    noStroke();
    fill(this.fillColor);
    ellipse(this.x, this.y, this.width, this.height);
  }
}

class MountainRange extends Shape {
  constructor(zIndex, numMountains, baseColor) {
    let maxMountainHeight = (zIndex + 1) / numMountains * (height - height * 0.4);
    maxMountainHeight += min(pow(zIndex, random(3.3, 4)), 100);

    super(0, height - maxMountainHeight, width, maxMountainHeight);

    let sat = map(zIndex, 0, numMountains, 0, saturation(topColor));
    let bright = map(zIndex, 0, numMountains, 0, saturation(topColor));
    this.fillColor = color(hue(topColor), sat, bright);

    // 5 is smooth, 10 is kinda rugged, 30 is jagged
    this.jaggedness = random(5, 10);

    this.startNoise = zIndex * width + random(0, width / 2);
    this.endNoise = this.startNoise + this.jaggedness;
    this.zIndex = zIndex;
    if (zIndex==0) {
      $("body").css("background", this.fillColor);
    }
  }

  draw() {
    // perlin noise links:
    // - http://flafla2.github.io/2014/08/09/perlinnoise.html
    // - https://jonoshields.com/2017/03/29/creating-procedurally-generated-scenes/
    // - https://genekogan.com/code/p5js-perlin-noise/
    fill(this.fillColor);

    beginShape();
    vertex(-20, height);
    for (var x = 1; x < width + 20; x++) {
      let nx = map(x, 0, width, this.startNoise, this.endNoise);
      let y = this.height * noise(nx);
      vertex(x, height - y);
    }
    vertex(width + 21, height);
    endShape();
  }
}
