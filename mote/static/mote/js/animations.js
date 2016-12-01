// Standard browser-friendly frame request code.

"use strict";

window.requestAnimFrame = (function(callback) {
    return window.requestAnimationFrame || window.webkitRequestAnimationFrame || window.mozRequestAnimationFrame || window.oRequestAnimationFrame || window.msRequestAnimationFrame ||
    function(callback) {
    	window.setTimeout(callback, 1000 / 60);
    };
})();

var canvas = document.getElementById("canvas");
if (canvas) {
    if (canvas.getContext){
    	var ctx = canvas.getContext('2d');
    }

    canvas.height = $('.hero').outerHeight();
    canvas.width = $('.hero').outerWidth();



    // --- PVector object ---

    // Basic constructor. These vectors consist of only x and y coordinates. (although vectors can consist of n number of variables - like 3D games would have 3: x,y,z)
    // From these two values we can determine direction:
    // If I travel 6 units to the right and 2 units up then I have travelled slightly upwards right.

    var PVector = function(x,y){
    	this.x = x;
    	this.y = y;
    }

    // Add one vector to another.
    // EG: If I'm travelling at 1 x_pixel and 1 y_pixel per second...then adding a (1,1) vector to my velocity will make me travel at (2,2)

    PVector.prototype.add = function(v){
    	this.x = this.x + v.x;
    	this.y = this.y + v.y;
    }

    // Opposite of add.
    // EG: (3,2) - (1,2) = (2,0)

    PVector.prototype.sub = function(v){
    	this.x = this.x - v.x;
    	this.y = this.y - v.y;
    }

    // Multiply by a scalar (scalars are single numbers that act as vector co-efficients)
    // EG: (1,2) * 3 = (3,6)
    // This is useful if you want to make your object travel 2 times as fast for example.

    PVector.prototype.mult = function(n){
    	this.x = this.x * n;
    	this.y = this.y * n;
    }

    // Opposite of mult()
    // EG: (9,6) / 3 = (3,2)

    PVector.prototype.div = function(n){
    	this.x = this.x / n;
    	this.y = this.y / n;
    }

    // Return the magnitude of the vector using (0,0) as the reference point.
    // This function uses the Pythagorean theorem: c^2 = x^2 + y^2
    // It is useful for finding distances as well as directions between objects.

    PVector.prototype.mag = function() {
    	return Math.sqrt((this.x * this.x) + (this.y * this.y));
    }

    // Normalise essentailly flattens a vector down to one "unit vector".
    // This is useful if you don't care how big the vector is, but rather which direction it is pointing in.

    PVector.prototype.normalize = function() {
    	var m = this.mag();
    	if (m != 0){
    		this.div(m);
    	}
    }

    // Optional: this prevents the vector from getting bigger than a certain size.
    // This is useful to prevent objects from accelerating infinitely.
    // EG: No matter how much you accelerate your chevy spark it will never drive faster than 140 - it's velocity vector is limited to 140.

    PVector.prototype.limit = function(max){
    	if (this.mag() > max){
    		this.normalize();
    		this.mult(max);
    	}
    }

    // This returns a copy of the vector. This is useful if we want to perform operations on a vector without changing the original.
    PVector.prototype.get = function(){
    	var vector_clone = new PVector(this.x, this.y);
    	return vector_clone;
    }

    // The below are javascript's equivalent of "static" methods.
    // What this means is that these methods cannot be called by object instances.
    // They can only be called by other functions inside the object or by calling them directly from the class.

    // This one accepts two vectors, adds them up and then returns the result as a new vector.
    // The difference between this and the prototyp.add() function is that this one leaves the original vectors untouched.
    PVector.add = function(v1,v2){
    	var v3 = new PVector(v1.x + v2.x, v1.y + v2.y);
    	return v3;
    }

    // opposite of above.
    PVector.sub = function(v1,v2){
    	var v3 = new PVector(v1.x - v2.x, v1.y - v2.y);
    	return v3;
    }

    var Electron = function(x, y, r, d){
      this.position = new PVector(x, y);
      this.radius = r;
      this.distance = d;
      this.speed = Math.random() * 0.1
      this.ticker = 0;
    }

    Electron.prototype.update = function(x, y){
      this.ticker += this.speed;
      this.position.x = x + this.distance * Math.sin(this.ticker);
      this.position.y = y + this.distance * Math.cos(this.ticker);
    }

    Electron.prototype.draw = function(){
      ctx.fillStyle = "rgba(255,255,255,0.4)";
      ctx.beginPath();
      ctx.arc(
        this.position.x,
        this.position.y,
        this.radius,
        0,
        2*Math.PI
      );
      ctx.fill();
    }


    var Atom = function(x, y){
      this.position = new PVector(x, y);
      this.radius = Math.random() * 20 + 3;
      this.velocity = new PVector(Math.random()/this.radius*10, Math.random()/this.radius*10);
      this.distance = this.radius * 3;
      this.electron = new Electron(
        x + Math.random() * this.radius - this.radius/2,
        y + Math.random() * this.radius - this.radius/2,
        this.radius / 3,
        this.distance
      );

    }

    Atom.prototype.draw = function(){
      ctx.fillStyle = "rgba(255,255,255,0.7)";
      ctx.beginPath();
      ctx.arc(
        this.position.x,
        this.position.y,
        this.radius,
        0,
        2*Math.PI
      );
      ctx.fill();

      ctx.strokeStyle = "rgba(255,255,255,0.2)";
      ctx.beginPath();
      ctx.arc(
        this.position.x,
        this.position.y,
        this.distance,
        0,
        2*Math.PI
      );
      ctx.stroke();
      this.electron.draw();

    }

    Atom.prototype.update = function(){
     if (this.position.y >= canvas.height
        || this.position.y <= 0 ){
       this.velocity.y = -this.velocity.y
     }

     if (this.position.x >= canvas.width
         || this.position.x <= 0 ){
       this.velocity.x = -this.velocity.x
     }

      this.position.add(this.velocity);


     this.electron.update(this.position.x, this.position.y);
    }





    // Main draw function

    var atoms = [];

    for (var i = 0; i < 10; i++){
      var atom = new Atom(Math.random() * canvas.width, Math.random() * canvas.height);
      atoms.push(atom);
    }



    draw();

    function draw() {

      ctx.clearRect(0,0, canvas.width, canvas.height);
      // Drawing goes here
      for (var i = 0; i < atoms.length; i++){

        for (var c = 1; c < atoms.length; c++){
          var opacity = PVector.sub(atoms[i].position, atoms[c].position);
          opacity = 5 / opacity.mag();
          ctx.strokeStyle = "rgba(255,255,255,"+opacity+")";
          //console.log(opacity);

          ctx.beginPath();
          ctx.lineTo(
            atoms[i].position.x,
            atoms[i].position.y
          );

          ctx.lineTo(
            atoms[c].position.x,
            atoms[c].position.y
          );

          ctx.stroke();
          ctx.closePath();

        }
        atoms[i].update();
        atoms[i].draw();

      }

    //effects performance sorry Pete :+1: -J
     // 	requestAnimFrame(function() {
        // draw(canvas, ctx);
      // });
    }
}
