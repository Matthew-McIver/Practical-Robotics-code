import time
import networkx as nx
import pickle
from pathlib import Path
from robomotor import RoboMotor
from robocam import RoboCam

SLEEPVALUE = 0.9

def AlignToTag(Tag_ID):
    print(f"Aligning to tag {Tag_ID}...")
    margin_buffer = 20
    course_movement_value = 20
    fine_movement_value = 3
    additional_sleep_time = 0.3
    total_rotation = 0
    #To get the centre of the tag
    Centre = Camera.camera.resolution[0] /2

    time.sleep(SLEEPVALUE)
    tag_position = Camera.current_seen.get(Tag_ID)

    if tag_position is None:
        x_position = 0
        movement_value = course_movement_value
    else:
        x_position = tag_position[0]
        movement_value = fine_movement_value
    
    while abs(Centre - x_position) > margin_buffer:

        if x_position > Centre:
            Motor.left(movement_value)
        elif x_position < Centre:
            Motor.right(movement_value)

        total_rotation += movement_value
        if total_rotation >= 360:
            course_movement_value = 10
            fine_movement_value = 1
            time.sleep(SLEEPVALUE + additional_sleep_time)
        else:
            time.sleep(SLEEPVALUE)

        tag_position = Camera.current_seen.get(Tag_ID)

        if tag_position is None:
            x_position = 0
            movement_value = course_movement_value
        else:
            x_position = tag_position[0]
            movement_value = fine_movement_value
    print("Tag aligned!")

def TravelUntilObstacle(Tag_ID):
    RealignDistance = 50
    SafeStopValue = 8
    Sum = 0

    while Motor.IRDistance > SafeStopValue:
        Motor.forward(1)
        Sum += 1
        if Sum % RealignDistance == 0:
            AlignToTag(Tag_ID)
    return Sum

def PlotRoute(Tag_ID):
    target_nodes = [n for n in Graph.nodes if Tag_ID in Graph.nodes[n]["seen_tags"]]
    path = nx.algorithms.shortest_paths.weighted.dijkstra_path(Graph, glob_current_tag, target_nodes[0])
    #Makes new list of all nodes about to be travelled, excluding the last node, which is the current node
    path = path[1:]
    TravelRoute(path)

def TravelRoute(path):
    print(f"Travelling path {path}.")
    for n in path:
        TravelToNode(n)

def TravelToNode(Tag_ID):
    print(f"Travelling to {Tag_ID}.")
    global glob_current_tag
    prev_node = glob_current_tag
    AlignToTag(Tag_ID)
    distance = TravelUntilObstacle(Tag_ID)
    glob_current_tag = Tag_ID
    Graph.add_edge(prev_node, glob_current_tag, weight = distance)

path = Path(__file__).parent
savefile_path = path / Path("RoboGraph.pickle")
savefile = open(savefile_path.as_posix(), "rb")
Graph = pickle.load(savefile)
savefile.close()

Motor = RoboMotor()
Camera = RoboCam()
Motor.wakeup()
Camera.start_video_thread()

glob_current_tag = 6
glob_end_tag = 3

try:
    path = nx.algorithms.shortest_paths.weighted.dijkstra_path(Graph, glob_current_tag, glob_end_tag)
    #Makes new list of all nodes about to be travelled, excluding the last node, which is the current node
    path = path[1:]
    TravelRoute(path)

finally: 
    Motor.sleep()
    Motor.kill()
    Camera.continue_recording = False