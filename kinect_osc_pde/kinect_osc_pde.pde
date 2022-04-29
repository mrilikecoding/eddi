import SimpleOpenNI.*;
import oscP5.*;
import netP5.*;

// init OSC vars
OscP5 oscP5;
NetAddress oscSendServer;

// create kinect object
SimpleOpenNI  kinect;

// int of each user being  tracked
// int[] userID;
int userID;
int[] userIDs;
int[] userMap;
// user colors
color[] userColor = new color[]{ color(255,0,0), color(0,255,0), color(0,0,255), color(255,255,0), color(255,0,255), color(0,255,255)};

// postion of head to draw circle
PVector headPosition = new PVector(0, 0, 0);
// linear interpolate from previous position
PVector lastHeadPosition = new PVector(0, 0, 0);
// postion of head to draw circle
PVector torsoPosition = new PVector(0, 0, 0);
// linear interpolate from previous position
PVector lastTorsoPosition = new PVector(0, 0, 0);

// turn headPosition into scalar form
float distanceScalar;
// diameter of head drawn in pixels
float headSize = 100;

// threshold of level of confidence
float confidenceLevel = 0.5;
// the current confidence level that the kinect is tracking
float confidence;
// vector of tracked position(s) for confidence checking
PVector positionVector = new PVector();

String[] positionLabels =  {
    "head", "neck", "leftShoulder", "leftElbow", "leftHand", "rightShoulder", "rightElbow",
    "rightHand", "torso", "leftHip", "rightHip", "leftKnee", "leftFoot", "rightFoot"
  };

void setup()
{
  // create a window the size of the depth information
  // size(1280, 480);

 String[] positionLabels =  {
    "head", "neck", "leftShoulder", "leftElbow", "leftHand", "rightShoulder", "rightElbow",
    "rightHand", "torso", "leftHip", "rightHip", "leftKnee", "leftFoot", "rightFoot"
  }; 

  // draw setup
  size(640, 480);
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
  strokeWeight(2);
  // smooth out drawing
  smooth();

  // start osc send server on port 12000
  oscP5 = new OscP5(this,12000);
  oscSendServer = new NetAddress("127.0.0.1",12000);
  oscP5.send("/kinect", new Object[] {"Kinect initialized in Processing"}, oscSendServer);
} // void setup()

int getSkeletonPositionKey(String position) {
  switch(position) {
    case "head":
      return SimpleOpenNI.SKEL_HEAD;
    case "neck":
      return SimpleOpenNI.SKEL_NECK;
    case "leftShoulder":
      return SimpleOpenNI.SKEL_LEFT_SHOULDER;
    case "leftElbow":
      return SimpleOpenNI.SKEL_LEFT_ELBOW;
    case "leftHand":
      return SimpleOpenNI.SKEL_LEFT_HAND;
    case "rightShoulder":
      return SimpleOpenNI.SKEL_RIGHT_SHOULDER;
    case "rightElbow":
      return SimpleOpenNI.SKEL_RIGHT_ELBOW;
    case "rightHand":
      return SimpleOpenNI.SKEL_RIGHT_HAND;
    case "torso":
      return SimpleOpenNI.SKEL_TORSO;
    case "leftHip":
      return SimpleOpenNI.SKEL_LEFT_HIP;
    case "rightHip":
      return SimpleOpenNI.SKEL_RIGHT_HIP;
    case "leftKnee":
      return SimpleOpenNI.SKEL_LEFT_KNEE;
    case "rightKnee":
      return SimpleOpenNI.SKEL_RIGHT_KNEE;
    case "leftFoot":
      return SimpleOpenNI.SKEL_LEFT_FOOT;
    case "rightFoot":
      return SimpleOpenNI.SKEL_RIGHT_FOOT;
    default:
      return 0;
  }
}

//Updates Kinect. Gets users tracking and draws skeleton and head if confidence of tracking is above threshold
void sendOSCPositionMessage(int userID, String positionLabel, PVector position) {
  OscMessage messageOut = new OscMessage("/kinect/" + position);
  messageOut.add(userID);
  messageOut.add(position.x);
  messageOut.add(position.y);
  messageOut.add(position.z);
  oscP5.send(messageOut, oscSendServer);
}

void draw(){
  background(0);
  // update the camera
  kinect.update();
    
  userIDs = kinect.getUsers();
  // loop through each user to see if tracking
  for(int i=0;i<userIDs.length;i++) {
    // if Kinect is tracking certain user then get joint vectors
    if(kinect.isTrackingSkeleton(userIDs[i])) {
      // get confidence level that Kinect is tracking head
      // int targetPosition = skeletonPositionKey.get("head");
      for (int j = 0; j < positionLabels.length; j++) {
        String positionLabel = positionLabels[j];
        confidence = kinect.getJointPositionSkeleton(userIDs[i], getSkeletonPositionKey(positionLabel), confidenceVector);
        if (confidence > confidenceLevel) {
          sendOSCPositionMessage(userID, positionLabel, confidenceVector);
          // change draw color based on hand id#
          stroke(userColor[(i)]);
          // fill the ellipse with the same color
          fill(userColor[(i)]);

          kinect.convertRealWorldToProjective(confidenceVector, confidenceVector);
          distanceScalar = (225/confidenceVector.z);
          ellipse(confidenceVector.x, confidenceVector.y, distanceScalar*headSize,distanceScalar*headSize);

          // draw the rest of the body
          // drawSkeleton(userIDs[i]);
        }
      } //if(confidence > confidenceLevel)
    } //if(kinect.isTrackingSkeleton(userID[i]))
  } //for(int i=0;i<userID.length;i++)
} // void draw()

void drawSkeleton(int userId){
   // get 3D position of head
  kinect.getJointPositionSkeleton(userId, SimpleOpenNI.SKEL_HEAD,headPosition);
  kinect.getJointPositionSkeleton(userId, SimpleOpenNI.SKEL_TORSO,torsoPosition);
  // convert real world point to projective space
  kinect.convertRealWorldToProjective(headPosition,headPosition);
  kinect.convertRealWorldToProjective(torsoPosition,torsoPosition);
  // create a distance scalar related to the depth in z dimension

  float interpolatedHeadX = lerp(lastHeadPosition.x, headPosition.x, 1.0f);
  float interpolatedHeadY = lerp(lastHeadPosition.y, headPosition.y, 1.0f);
  float interpolatedHeadZ = lerp(lastHeadPosition.z, headPosition.z, 1.0f);
  float interpolatedTorsoX = lerp(lastTorsoPosition.x, torsoPosition.x, 1.0f);
  float interpolatedTorsoY = lerp(lastTorsoPosition.y, torsoPosition.y, 1.0f);
  float interpolatedTorsoZ = lerp(lastTorsoPosition.z, torsoPosition.z, 1.0f);
  distanceScalar = (225/lastHeadPosition.z);
  ellipse(lastHeadPosition.x,lastHeadPosition.y, distanceScalar*headSize,distanceScalar*headSize);
  ellipse(lastTorsoPosition.x,lastTorsoPosition.y, distanceScalar*headSize,distanceScalar*headSize);
  lastHeadPosition = new PVector(interpolatedHeadX, interpolatedHeadY, interpolatedHeadZ);
  lastTorsoPosition = new PVector(interpolatedTorsoX, interpolatedTorsoY, interpolatedTorsoZ);
} // void drawSkeleton(int userId)

void onNewUser(SimpleOpenNI curContext, int userId){
  // start tracking of user id
  curContext.startTrackingSkeleton(userId);
  println("Tracking User: " + userId);
} //void onNewUser(SimpleOpenNI curContext, int userId)

void onLostUser(SimpleOpenNI curContext, int userId){
  // print user lost and user id
  println("User Lost - userId: " + userId);
} //void onLostUser(SimpleOpenNI curContext, int userId)

void onVisibleUser(SimpleOpenNI curContext, int userId){
} //void onVisibleUser(SimpleOpenNI curContext, int userId)
