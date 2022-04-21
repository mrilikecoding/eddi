trap "exit" INT TERM ERR
trap "kill 0" EXIT

processing-java --sketch=/Users/katevangeloff/Development/lumi/kinect_osc_pde --run &
python main.py

wait