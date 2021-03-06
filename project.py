#
#                             _ooOoo_
#                            o8888888o
#                            88" . "88
#                            (| -_- |)
#                            O\  =  /O
#                         ____/`---'\____
#                       .'  \\|     |//  `.
#                      /  \\|||  :  |||//  \
#                     /  _||||| -:- |||||-  \
#                     |   | \\\  -  /// |   |
#                     | \_|  ''\---/''  |   |
#                     \  .-\__  `-`  ___/-. /
#                   ___`. .'  /--.--\  `. . __
#                ."" '<  `.___\_<|>_/___.'  >'"".
#               | | :  `- \`.;`\ _ /`;.`/ - ` : | |
#               \  \ `-.   \_ __\ /__ _/   .-` /  /
#          ======`-.____`-.___\_____/___.-`____.-'======
#                             `=---='
#          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#                     佛祖保佑        永无BUG
#

try:
    import MalmoPython
except:
    from malmo import MalmoPython
import os
import sys
import time
import json
from agent import Agent
import random
import utils


if __name__ == "__main__":

    # read mission from 
    with open('mission.xml','r') as iFile:
        missionXML = iFile.read()
        iFile.close()

    agent_host = MalmoPython.AgentHost()
    try:
        agent_host.parse(sys.argv)
    except RuntimeError as e:
        print('ERROR:', e)
        print(agent_host.getUsage())
        exit(1)
    if agent_host.receivedArgument("help"):
        print(agent_host.getUsage())
        exit(0)
    
    iRepeat = 120
    agent = Agent()

    # repeat mission for 
    for i in range(iRepeat):
        agent.pastActions = []
        my_mission = MalmoPython.MissionSpec(missionXML, True)
        my_mission_record = MalmoPython.MissionRecordSpec()

        # Start mission
        max_retries = 3
        my_client_pool = MalmoPython.ClientPool()
        my_client_pool.add(MalmoPython.ClientInfo("127.0.0.1", 10000))
        for retry in range(max_retries):
            try:
                agent_host.startMission(my_mission, my_client_pool, my_mission_record, 0, "Monster Killer")
                break
            except RuntimeError as e:
                if retry == max_retries - 1:
                    print("Error starting mission:", e)
                    exit(1)
                else:
                    time.sleep(2)
        
        # Wait until mission starts:
        print("Waiting for the mission to start")
        world_state = agent_host.getWorldState()
        while not world_state.has_mission_begun:
            time.sleep(0.1)
            world_state = agent_host.getWorldState()
            for error in world_state.errors:
                print("Error:", error.text)
        print()
        print("Mission started: ",i, " with n = 1"," and with eps = ",agent.epsilon)

        # Mission running
        # let agent hunger s.t. no life recovery
        agent_host.sendCommand("chat " +  "/effect @p minecraft:hunger 5 201")
        #agent_host.sendCommand("chat " + "/replaceitem entity @p slot.armor.chest minecraft:diamond_chestplate 1 0")
        #agent_host.sendCommand("chat " + "/replaceitem entity @p slot.armor.head minecraft:diamond_helmet 1 0")
        #agent_host.sendCommand("chat " + "/replaceitem entity @p slot.armor.legs minecraft:diamond_leggings 1 0")
        #agent_host.sendCommand("chat " + "/replaceitem entity @p slot.armor.feet minecraft:diamond_boots 1 0")
        
        
        time.sleep(2)
        observations = agent.getObservations(world_state)
        # generate enemy after hunger
        #agent_host.sendCommand("chat " +  "/summon minecraft:witch ~ ~0 ~15")
        #agent_host.sendCommand("chat " +  "/summon villager_golem ~2 ~0 ~10")
        agent_host.sendCommand("chat " +  "/summon zombie ~2 ~0 ~5")
        time.sleep(0.5)

        agent.run(agent_host)
        
        # Mission ended, analyze Q-table
        print("Mission ended")
        # delete state where enemy died
        for t in agent.q_table:
            if t[0] < 0:
                del agent.q_table[t]
                break
        for state in sorted(agent.q_table.keys()):
            lowest = -10000
            theaction = 0
            for action in agent.q_table[state]:
                if agent.q_table[state][action] > lowest:
                    lowest = agent.q_table[state][action]
                    theaction = action
            print("On state: ",state," best action is ",theaction," with q_value of ", lowest)

        # teleport to end current mission
        tp_command = "tp 0 255 0"
        agent_host.sendCommand(tp_command)
        time.sleep(1) # sleep for 1s, otherwise it will not restart
            #if agent.Heart == 0:
            #if i+1 % 10 == 0:
            #   agent.epsilon-=0.01
            #else:
            
        # reset agent parameters
        agent.resetAgent()
