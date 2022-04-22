// import SimpleOpenNI.*;
// import processing.opengl.*;

// // set bounds for playing space
// int MAX_X = 1000;
// int MIN_X = -1000;
// int MAX_Y = 1000;
// int MIN_Y = -1000;
// int MAX_Z = 800; // closest point
// int MIN_Z = -800; // farthest point
// float kinectAngleDegrees = -5;
// int kinectDistance = 0;
// PVector boundingBoxCenter = new PVector(0, 0, 2300);
// int box_w = MAX_X - MIN_X; 
// int box_h = MAX_Y - MIN_Y; 
// int box_d = MAX_Z-MIN_Z; 

// // for zooming / scale
// float s = 1;
// float pan = 0;
// float tilt = 0;

// // init OSC vars
// OscP5 oscP5;
// NetAddress oscSendServer;

// // create kinect object
// SimpleOpenNI  kinect;
// // image storage from kinect
// PImage kinectDepth;

// void setup()
// {
//   size(1280, 480);
//   size(1024, 768, OPENGL);
//   frameRate(30);

//   // start a new kinect object
//   kinect = new SimpleOpenNI(this);

//   // enable depth sensor
//   kinect.enableDepth();
//   // kinect.enableRGB();
//   // kinect.alternativeViewPointDepthToImage();

//   // enable skeleton generation for all joints
//   kinect.enableUser();

//   // draw thickness of drawer
//   strokeWeight(2);
//   // smooth out drawing
//   smooth();

//   // start osc send server on port 12000
//   oscP5 = new OscP5(this,12000);
//   oscSendServer = new NetAddress("127.0.0.1",12000);
//   oscP5.send("/kinect", new Object[] {"Kinect initialized in Processing"}, oscSendServer);
// } // void setup()

// //Updates Kinect. Gets users tracking and draws skeleton and head if confidence of tracking is above threshold
// void draw(){
//   background(0);
//   // update the camera
//   kinect.update();

//   translate(width/2, height/2, -500);
//   rotateX(radians(180));

//   translate(0, 0, 400);
//   rotateY(radians(map(mouseX, 0, width, -180, 180)));
//   rotateX(radians(map(mouseY, 0, height, -180, 180)));
//   translate(0, 0, s*-1000);
//   scale(s);

//   PVector[] depthPoints = kinect.depthMapRealWorld();

//   int depthPointsInBox = 0;

//   for (int i = 0; i < depthPoints.length; i+=10) {
//     PVector currentPoint = depthPoints[i];
//     // TODO get a range of values normalized off the relative depth user position (?)
//     // use center of mass?
//     stroke(0, 255, 0);
//     if (currentPoint.x > boundingBoxCenter.x - (box_w/2)){
//       if (currentPoint.y > boundingBoxCenter.y - (box_h/2)){
//         if (currentPoint.z > boundingBoxCenter.z - (box_d/2)){
//           if (currentPoint.x < boundingBoxCenter.x + (box_w/2)){
//             if (currentPoint.y < boundingBoxCenter.y + (box_h/2)){
//               if (currentPoint.z < boundingBoxCenter.z + (box_d/2)){
//                 point(currentPoint.x, currentPoint.y, currentPoint.z);
//               }
//             }
//           }
//         }
//       }
//     }
//   }
//   println(depthPointsInBox);

//   translate(boundingBoxCenter.x, boundingBoxCenter.y, boundingBoxCenter.z);
//   noFill();
//   stroke(255, 0, 0);
//   rotateX(radians(kinectAngleDegrees));
//   box(box_w, box_h, box_d);

// } // void draw()


// void keyPressed() {
//   // zoom in and out with up down
//   if(keyCode == 38){
//     s = s + 0.1;
//   }
//   if(keyCode == 40){
//     s = s - 0.1;
//   }
  
// }
