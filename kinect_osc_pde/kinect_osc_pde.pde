import SimpleOpenNI.*;
import oscP5.*;
import netP5.*;
OscP5 oscP5;
NetAddress oscSendServer;

// create kinect object
SimpleOpenNI  kinect;
// image storage from kinect
PImage kinectDepth;
// int of each user being  tracked
int[] userID;
// user colors
color[] userColor = new color[]{ color(255,0,0), color(0,255,0), color(0,0,255), color(255,255,0), color(255,0,255), color(0,255,255)};

// set up some calibration params
// TODO would be great to pass these in as args
// int closestValue;
// int closestX;
// int closestY;
// int farthestValue;
// int farthestX;
// int farthestY;


// postion of head to draw circle
PVector headPosition = new PVector(0, 0, 0);
// linear interpolate from previous position
PVector lastHeadPosition = new PVector(0, 0, 0);

// turn headPosition into scalar form
float distanceScalar;
// diameter of head drawn in pixels
float headSize = 200;

// threshold of level of confidence
float confidenceLevel = 0.5;
// the current confidence level that the kinect is tracking
float confidence;
// vector of tracked head for confidence checking
PVector confidenceVector = new PVector();

void setup()
{
  // create a window the size of the depth information
  size(1280, 480);

  // TODO maybe theres a way to dynamically update this from
  // lumi via OSC depending on the time lumi is taking...
  // limit frame rate to compensate for lumi computation
  // the kinect v1 captures at 30 FPS
  frameRate(30);

  // start a new kinect object
  kinect = new SimpleOpenNI(this);

  // enable depth sensor
  kinect.enableDepth();
  kinect.enableRGB();

  // enable skeleton generation for all joints
  kinect.enableUser();

  // draw thickness of drawer
  strokeWeight(3);
  // smooth out drawing
  smooth();

  /* start osc send server on port 12000 */
  oscP5 = new OscP5(this,12000);
  oscSendServer = new NetAddress("127.0.0.1",12000);
  /* send an OSC message to this sketch */
  oscP5.send("/kinect", new Object[] {"Kinect initialized in Processing"}, oscSendServer);
} // void setup()

//Updates Kinect. Gets users tracking and draws skeleton and head if confidence of tracking is above threshold

void draw(){
  background(0);
  // update the camera
  closestValue = 8000;

  kinect.update();
  // int[] depthValues = kinect.depthMap();

  // for (int y = 0; y < 480; y++){
  //   for (int x = 0; x < 640; x++){
  //     // reverse x by moving from right side of image
  //     int reversedX = 640 - x - 1;
  //     int i = reversedX + y * 640; // mult by 640 to access right depth array row
  //     int currentDepthValue = depthValues[i];
      
  //     // only look for values within range
  //     if (
  //       currentDepthValue > 610 && 
  //       currentDepthValue < 1525 && 
  //       currentDepthValue < closestValue) {
  //         closestValue = currentDepthValue;
  //         closestX = x;
  //         closestY = y;
  //     }
  //   }
  // }

  // draw depth image at coordinates (0,0)
  image(kinect.depthImage(),0,0);
  image(kinect.rgbImage(), 640,0);
  
  // get all user IDs of tracked users
  userID = kinect.getUsers();

  // loop through each user to see if tracking
  for(int i=0;i<userID.length;i++)
  {
    // if Kinect is tracking certain user then get joint vectors
    if(kinect.isTrackingSkeleton(userID[i]))
    {
      // get confidence level that Kinect is tracking head
      confidence = kinect.getJointPositionSkeleton(userID[i], SimpleOpenNI.SKEL_HEAD,confidenceVector);

      // if confidence of tracking is beyond threshold, then track user
      if(confidence > confidenceLevel)
      {
        OscMessage messageOut = new OscMessage("/kinect");
        messageOut.add(userID[i]); /* add an int to the osc message */
        messageOut.add(headPosition.x); /* add an int to the osc message */
        messageOut.add(headPosition.y); /* add an int to the osc message */
        messageOut.add(headPosition.z); /* add an int to the osc message */
        oscP5.send(messageOut, oscSendServer);

        // change draw color based on hand id#
        stroke(userColor[(i)]);
        // fill the ellipse with the same color
        fill(userColor[(i)]);
        // draw the rest of the body
        drawSkeleton(userID[i]);

      } //if(confidence > confidenceLevel)
    } //if(kinect.isTrackingSkeleton(userID[i]))
  } //for(int i=0;i<userID.length;i++)
} // void draw()

void drawSkeleton(int userId){
   // get 3D position of head
  kinect.getJointPositionSkeleton(userId, SimpleOpenNI.SKEL_HEAD,headPosition);
  // convert real world point to projective space
  kinect.convertRealWorldToProjective(headPosition,headPosition);
  // create a distance scalar related to the depth in z dimension

  float interpolatedHeadX = lerp(lastHeadPosition.x, headPosition.x, 1.0f);
  float interpolatedHeadY = lerp(lastHeadPosition.y, headPosition.y, 1.0f);
  float interpolatedHeadZ = lerp(lastHeadPosition.z, headPosition.z, 1.0f);
  distanceScalar = (225/lastHeadPosition.z);
  ellipse(lastHeadPosition.x,lastHeadPosition.y, distanceScalar*headSize,distanceScalar*headSize);
  lastHeadPosition = new PVector(interpolatedHeadX, interpolatedHeadY, interpolatedHeadZ);

  //draw limb from head to neck
  //kinect.drawLimb(userId, SimpleOpenNI.SKEL_HEAD, SimpleOpenNI.SKEL_NECK);
 // //draw limb from neck to left shoulder
 // kinect.drawLimb(userId, SimpleOpenNI.SKEL_NECK, SimpleOpenNI.SKEL_LEFT_SHOULDER);
 // //draw limb from left shoulde to left elbow
 // kinect.drawLimb(userId, SimpleOpenNI.SKEL_LEFT_SHOULDER, SimpleOpenNI.SKEL_LEFT_ELBOW);
 // //draw limb from left elbow to left hand
 // kinect.drawLimb(userId, SimpleOpenNI.SKEL_LEFT_ELBOW, SimpleOpenNI.SKEL_LEFT_HAND);
 // //draw limb from neck to right shoulder
 // kinect.drawLimb(userId, SimpleOpenNI.SKEL_NECK, SimpleOpenNI.SKEL_RIGHT_SHOULDER);
 // //draw limb from right shoulder to right elbow
 // kinect.drawLimb(userId, SimpleOpenNI.SKEL_RIGHT_SHOULDER, SimpleOpenNI.SKEL_RIGHT_ELBOW);
 // //draw limb from right elbow to right hand
 // kinect.drawLimb(userId, SimpleOpenNI.SKEL_RIGHT_ELBOW, SimpleOpenNI.SKEL_RIGHT_HAND);
 ////draw limb from left shoulder to torso
 // kinect.drawLimb(userId, SimpleOpenNI.SKEL_LEFT_SHOULDER, SimpleOpenNI.SKEL_TORSO);
 // //draw limb from right shoulder to torso
 // kinect.drawLimb(userId, SimpleOpenNI.SKEL_RIGHT_SHOULDER, SimpleOpenNI.SKEL_TORSO);
 // //draw limb from torso to left hip
 // kinect.drawLimb(userId, SimpleOpenNI.SKEL_TORSO, SimpleOpenNI.SKEL_LEFT_HIP);
 // //draw limb from left hip to left knee
 // kinect.drawLimb(userId, SimpleOpenNI.SKEL_LEFT_HIP,  SimpleOpenNI.SKEL_LEFT_KNEE);
 // //draw limb from left knee to left foot
 // kinect.drawLimb(userId, SimpleOpenNI.SKEL_LEFT_KNEE, SimpleOpenNI.SKEL_LEFT_FOOT);
 // //draw limb from torse to right hip
 // kinect.drawLimb(userId, SimpleOpenNI.SKEL_TORSO, SimpleOpenNI.SKEL_RIGHT_HIP);
 // //draw limb from right hip to right knee
 // kinect.drawLimb(userId, SimpleOpenNI.SKEL_RIGHT_HIP, SimpleOpenNI.SKEL_RIGHT_KNEE);
 // //draw limb from right kneee to right foot
 // kinect.drawLimb(userId, SimpleOpenNI.SKEL_RIGHT_KNEE, SimpleOpenNI.SKEL_RIGHT_FOOT);
} // void drawSkeleton(int userId)

void onNewUser(SimpleOpenNI curContext, int userId){
  println("New User Detected - userId: " + userId);
  // start tracking of user id
  curContext.startTrackingSkeleton(userId);
} //void onNewUser(SimpleOpenNI curContext, int userId)

void onLostUser(SimpleOpenNI curContext, int userId){
  // print user lost and user id
  println("User Lost - userId: " + userId);
} //void onLostUser(SimpleOpenNI curContext, int userId)

void onVisibleUser(SimpleOpenNI curContext, int userId){
} //void onVisibleUser(SimpleOpenNI curContext, int userId)

void mousePressed(){
  int[] depthValues = kinect.depthMap();
  int clickPosition = mouseX + (mouseY * 640);
  int clickedDepth = depthValues[clickPosition];
  float inches = clickedDepth / 25.4;
  println("inches: " + inches);
}