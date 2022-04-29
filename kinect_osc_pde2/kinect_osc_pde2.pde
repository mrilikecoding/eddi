import SimpleOpenNI.*;
import oscP5.*;
import netP5.*;
import java.util.Map;

// init OSC vars
OscP5 oscP5;
NetAddress oscSendServer;
// init kinect var
SimpleOpenNI kinect;

// int of each user being  tracked
int[] userIDs;
// user colors
color[] userColors = new color[]{ color(255,0,0), color(0,255,0), color(0,0,255), color(255,255,0), color(255,0,255), color(0,255,255)};

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

// index static kinect position keys by label
HashMap<Integer, HashMap<String,PVector>> userCurrentPositions = new HashMap<Integer, HashMap<String, PVector>>();
HashMap<Integer, HashMap<String,PVector>> userLastPositions = new HashMap<Integer, HashMap<String, PVector>>();
String[] positionLabels =  {
    "head", "neck", "leftShoulder", "leftElbow", "leftHand", "rightShoulder", "rightElbow",
    "rightHand", "torso", "leftHip", "rightHip", "leftKnee", "leftFoot", "rightFoot"
};
HashMap<String, PVector> currentLoopUserPosition;
  
void setup() {
  // create a window the size of the depth information
  // size(1280, 480); // if we want to drop the rgb image alongside
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

  // Default drawing params
  strokeWeight(2);
  smooth();

  // start osc send server on port 12000
  oscP5 = new OscP5(this,12000);
  oscSendServer = new NetAddress("127.0.0.1",12000);
  oscP5.send("/kinect", new Object[] {"Kinect initialized in Processing"}, oscSendServer);
} // void setup()

void updateCurrentPositions(int userID) {
  // iterate through each position, get the joint position,
  // set the corresponding entry for the user in the currentPositions hashmap
  if (!userCurrentPositions.containsKey(userID))  {
    userCurrentPositions.put(userID, new HashMap<String, PVector>());
  }
  HashMap<String, PVector> userCurrentPosition = userCurrentPositions.get(userID);
  for (int i = 0; i < positionLabels.length; i++) {
    String positionLabel = positionLabels[i];
    PVector position;
    switch(positionLabel) {
      case "head":
        position = userCurrentPosition.containsKey(positionLabel) ? userCurrentPosition.get(positionLabel) : new PVector();
        kinect.getJointPositionSkeleton(userID, SimpleOpenNI.SKEL_HEAD, position);
        userCurrentPosition.put(positionLabel, position);
        break;
      // case "neck":
      //   position = userCurrentPosition.containsKey(positionLabel) ? userCurrentPosition.get(positionLabel) : new PVector();
      //   kinect.getJointPositionSkeleton(userID, SimpleOpenNI.SKEL_NECK, userCurrentPosition.get(positionLabel));
      //   userCurrentPosition.put(positionLabel, position);
      //   break;
      // case "leftShoulder":
      //   position = userCurrentPosition.containsKey(positionLabel) ? userCurrentPosition.get(positionLabel) : new PVector();
      //   kinect.getJointPositionSkeleton(userID, SimpleOpenNI.SKEL_LEFT_SHOULDER, userCurrentPosition.get(positionLabel));
      //   userCurrentPosition.put(positionLabel, position);
      //   break;
      // case "leftElbow":
      //   position = userCurrentPosition.containsKey(positionLabel) ? userCurrentPosition.get(positionLabel) : new PVector();
      //   kinect.getJointPositionSkeleton(userID, SimpleOpenNI.SKEL_LEFT_ELBOW, userCurrentPosition.get(positionLabel));
      //   userCurrentPosition.put(positionLabel, position);
      //   break;
      // case "leftHand":
      //   position = userCurrentPosition.containsKey(positionLabel) ? userCurrentPosition.get(positionLabel) : new PVector();
      //   kinect.getJointPositionSkeleton(userID, SimpleOpenNI.SKEL_LEFT_HAND, userCurrentPosition.get(positionLabel));
      //   userCurrentPosition.put(positionLabel, position);
      //   break;
      // case "rightShoulder":
      //   position = userCurrentPosition.containsKey(positionLabel) ? userCurrentPosition.get(positionLabel) : new PVector();
      //   kinect.getJointPositionSkeleton(userID, SimpleOpenNI.SKEL_RIGHT_SHOULDER, userCurrentPosition.get(positionLabel));
      //   userCurrentPosition.put(positionLabel, position);
      //   break;
      // case "rightElbow":
      //   position = userCurrentPosition.containsKey(positionLabel) ? userCurrentPosition.get(positionLabel) : new PVector();
      //   kinect.getJointPositionSkeleton(userID, SimpleOpenNI.SKEL_RIGHT_ELBOW, userCurrentPosition.get(positionLabel));
      //   userCurrentPosition.put(positionLabel, position);
      //   break;
      // case "rightHand":
      //   position = userCurrentPosition.containsKey(positionLabel) ? userCurrentPosition.get(positionLabel) : new PVector();
      //   kinect.getJointPositionSkeleton(userID, SimpleOpenNI.SKEL_RIGHT_HAND, userCurrentPosition.get(positionLabel));
      //   userCurrentPosition.put(positionLabel, position);
      //   break;
      // case "torso":
      //   position = userCurrentPosition.containsKey(positionLabel) ? userCurrentPosition.get(positionLabel) : new PVector();
      //   kinect.getJointPositionSkeleton(userID, SimpleOpenNI.SKEL_TORSO, userCurrentPosition.get(positionLabel));
      //   userCurrentPosition.put(positionLabel, position);
      //   break;
      // case "leftHip":
      //   position = userCurrentPosition.containsKey(positionLabel) ? userCurrentPosition.get(positionLabel) : new PVector();
      //   kinect.getJointPositionSkeleton(userID, SimpleOpenNI.SKEL_LEFT_HIP, userCurrentPosition.get(positionLabel));
      //   userCurrentPosition.put(positionLabel, position);
      //   break;
      // case "rightHip":
      //   position = userCurrentPosition.containsKey(positionLabel) ? userCurrentPosition.get(positionLabel) : new PVector();
      //   kinect.getJointPositionSkeleton(userID, SimpleOpenNI.SKEL_RIGHT_HIP, userCurrentPosition.get(positionLabel));
      //   userCurrentPosition.put(positionLabel, position);
      //   break;
      // case "leftKnee":
      //   position = userCurrentPosition.containsKey(positionLabel) ? userCurrentPosition.get(positionLabel) : new PVector();
      //   kinect.getJointPositionSkeleton(userID, SimpleOpenNI.SKEL_LEFT_KNEE, userCurrentPosition.get(positionLabel));
      //   userCurrentPosition.put(positionLabel, position);
      //   break;
      // case "rightKnee":
      //   position = userCurrentPosition.containsKey(positionLabel) ? userCurrentPosition.get(positionLabel) : new PVector();
      //   kinect.getJointPositionSkeleton(userID, SimpleOpenNI.SKEL_RIGHT_KNEE, userCurrentPosition.get(positionLabel));
      //   userCurrentPosition.put(positionLabel, position);
      //   break;
      // case "leftFoot":
      //   position = userCurrentPosition.containsKey(positionLabel) ? userCurrentPosition.get(positionLabel) : new PVector();
      //   kinect.getJointPositionSkeleton(userID, SimpleOpenNI.SKEL_LEFT_FOOT, userCurrentPosition.get(positionLabel));
      //   userCurrentPosition.put(positionLabel, position);
      //   break;
      // case "rightFoot":
      //   position = userCurrentPosition.containsKey(positionLabel) ? userCurrentPosition.get(positionLabel) : new PVector();
      //   kinect.getJointPositionSkeleton(userID, SimpleOpenNI.SKEL_RIGHT_FOOT, userCurrentPosition.get(positionLabel));
      //   userCurrentPosition.put(positionLabel, position);
      //   break;
    }
  }
}

//Updates Kinect. Gets users tracking and draws skeleton and head if confidence of tracking is above threshold
void draw() {
  background(0);
  kinect.update();
  image(kinect.depthImage(),0,0);
    
  userIDs = kinect.getUsers();
  // loop through each user to see if tracking
  for(int i=0; i <userIDs.length; i++) {
    // if Kinect is tracking certain user then get joint vectors
    int userID = userIDs[i];
    if(kinect.isTrackingSkeleton(userID)) {
      if (!userLastPositions.containsKey(userID))  {
        userLastPositions.put(userID, new HashMap<String, PVector>());
      }
      // get confidence level that Kinect is tracking head
      confidence = kinect.getJointPositionSkeleton(userID, SimpleOpenNI.SKEL_HEAD, confidenceVector);

      // if confidence of tracking is beyond threshold, then track user
      if(confidence > confidenceLevel)
      {
        // get current positions - current sensor reading
        updateCurrentPositions(userID);

        // HashMap<String, PVector> userPositions = new HashMap<String, PVector>();
        HashMap<String, PVector> currentLoopUserPosition = userCurrentPositions.get(userID);
        println("FUCK JAVA");
        // for (int j = 0; j < positionLabels.length; j++) {
        //   String label = positionLabels[j];
          // PVector currentCoordinates = userCurrentPosition.get(label);
          // set send coords by lerp between last position and current position
          // float interpolatedX = lerp(lastCoordinates.x, currentCoordinates.x, 1.0f);
          // float interpolatedY = lerp(lastCoordinates.y, currentCoordinates.y, 1.0f);
          // float interpolatedZ = lerp(lastCoordinates.z, currentCoordinates.z, 1.0f);
        //   // send lerp coordinates
        //   messageOut.add(userID);
        //   messageOut.add(label);
        //   messageOut.add(interpolatedX);
        //   messageOut.add(interpolatedY);
        //   messageOut.add(interpolatedZ);
        //   oscP5.send(messageOut, oscSendServer);
        //   // set last position var to lerp coords
        //   positions[label] = new PVector(interpolatedX, interpolatedHeadY, interpolatedHeadZ);
        // } // for loop j position labels
        // userLastPositions[userID] = positions;

        // // set user colors and draw head
        // stroke(userColors[(i)]);
        // fill(userColors[(i)]);
        //ellipse(userCurrentPosition.get("head").x, userCurrentPosition.get("head").y, distanceScalar*headSize,distanceScalar*headSize);

      } //if(confidence > confidenceLevel)
    } //if(kinect.isTrackingSkeleton(userID[i]))
  } //for(int i=0;i<userID.length;i++)
} // void draw()

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
