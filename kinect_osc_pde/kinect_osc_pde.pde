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
color[] userColor = new color[]{ color(3,250, 240), color(0,255,0), color(0,0,255), color(255,255,0), color(255,0,255), color(0,255,255)};

// turn joint distance into scalar form
float distanceScalar;
// diameter of joint marker in pixels
float jointMarkerSize = 100;

// threshold of level of confidence
float confidenceLevel = 0.6;
// the current confidence level that the kinect is tracking
float confidence;
// vector of current tracked position(s) for confidence checking
PVector currentPositionVector = new PVector();
PVector lastPositionVector = new PVector();

String[] positionLabels =  {
  "head", 
  "neck", 
  "leftShoulder", 
  "leftElbow", 
  "leftHand", 
  "rightShoulder", 
  "rightElbow",
  "rightHand", 
  "torso", 
  "leftHip", 
  "rightHip", 
  "leftKnee", 
  "leftFoot", 
  "rightFoot"
};

void setup()
{
  // draw setup
  size(640, 480);
  // TODO maybe theres a way to dynamically update this from
  // lumi via OSC depending on the time lumi is taking...
  // limit frame rate to compensate for lumi computation
  // the kinect v1 captures at 30 FPS
  frameRate(30);
  // start a new kinect object
  kinect = new SimpleOpenNI(this);
  // kinect.setMirror(true);

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
  oscP5 = new OscP5(this, 12001);
  oscSendServer = new NetAddress("127.0.0.1",12000);
  // oscP5.send("/kinect", new Object[] {"Kinect initialized in Processing"}, oscSendServer);
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

void draw(){
  background(0);
  image(kinect.rgbImage(),0,0);
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
        // for this position label, get 3d position coords
        confidence = kinect.getJointPositionSkeleton(userIDs[i], getSkeletonPositionKey(positionLabel), currentPositionVector);
        if (confidence > confidenceLevel) {
          // change draw color based on hand id#
          stroke(userColor[(i)]);
          // fill the ellipse with the same color
          fill(userColor[(i)]);

          // convert real world coord to projective space
          kinect.convertRealWorldToProjective(currentPositionVector, currentPositionVector);
          currentPositionVector.lerp(lastPositionVector, 0.5f);
          distanceScalar = (225/currentPositionVector.z);
          if (
            positionLabel == "head"
          ) {
            ellipse(currentPositionVector.x, currentPositionVector.y, distanceScalar*jointMarkerSize, distanceScalar*jointMarkerSize);
          }
          lastPositionVector = currentPositionVector;
          // add each position to an OSC bundle
          OscMessage messageOut = new OscMessage("/kinect");
          messageOut.add(userID);
          messageOut.add(positionLabel);
          messageOut.add(currentPositionVector.x);
          messageOut.add(currentPositionVector.y);
          messageOut.add(currentPositionVector.z);
          oscP5.send(messageOut, oscSendServer);
        }
      } //if(confidence > confidenceLevel)
    } //if(kinect.isTrackingSkeleton(userID[i]))
  } //for(int i=0;i<userID.length;i++)
} // void draw()

void onNewUser(SimpleOpenNI curContext, int userId){
  // start tracking of user id
  curContext.startTrackingSkeleton(userId);
  OscMessage messageOut = new OscMessage("/kinect");
  messageOut.add("tracking");
  messageOut.add(userID);
  oscP5.send(messageOut, oscSendServer);
} //void onNewUser(SimpleOpenNI curContext, int userId)

void onLostUser(SimpleOpenNI curContext, int userId){
  // print user lost and user id
  OscMessage messageOut = new OscMessage("/kinect");
  messageOut.add("lost");
  messageOut.add(userID);
  oscP5.send(messageOut, oscSendServer);
} //void onLostUser(SimpleOpenNI curContext, int userId)

void onVisibleUser(SimpleOpenNI curContext, int userId){
} //void onVisibleUser(SimpleOpenNI curContext, int userId)
