import logging

def appendSystem(systemKey,sim,sim2app,mode):

    logger = logging.getLogger("pyUAMMD")

    #########################
    #Appending system
    #System structure:
    #   systemKey: {
    #       "parameters": {"name": ..., "backup": ..., ...},
    #       "labels": [..., ...],
    #       "data": [[...],
    #                [...],
    #                ...]

    # Four cases:
    # 1) system NOT in sim and system NOT in sim2app
    # 2) system NOT in sim and system in sim2app
    # 3) system in sim and system NOT in sim2app
    # 4) system in sim and system in sim2app

    systemInSim     = (systemKey in sim)
    systemInSim2app = (systemKey in sim2app)

    # 1) system NOT in sim and system NOT in sim2app
    if not systemInSim and not systemInSim2app:
        #Do nothing
        pass
    # 2) system NOT in sim and system in sim2app
    elif not systemInSim and systemInSim2app:
        sim[systemKey] = copy.deepcopy(sim2app[systemKey])
    # 3) system in sim and system NOT in sim2app
    elif systemInSim and not systemInSim2app:
        #Do nothing
        pass
    # 4) system in sim and system in sim2app
    elif systemInSim and systemInSim2app:
        if "labels" in sim[systemKey]:
            logger.error("Systems with labels are not supported")
            raise Exception("Systems with labels are not supported")
        if "data" in sim[systemKey]:
            logger.error("Systems with data are not supported")
            raise Exception("Systems with data are not supported")

        parametersInSim     = ("parameters" in sim[systemKey])
        parametersInSim2app = ("parameters" in sim2app[systemKey])

        if not parametersInSim and not parametersInSim2app:
            #Do nothing
            pass
        elif not parametersInSim and parametersInSim2app:
            sim[systemKey]["parameters"] = copy.deepcopy(sim2app[systemKey]["parameters"])
        elif parametersInSim and not parametersInSim2app:
            #Do nothing
            pass
        elif parametersInSim and parametersInSim2app:

            #Check if parameter name is present in both systems.
            nameInSim     = ("name" in sim[systemKey]["parameters"])
            nameInSim2app = ("name" in sim2app[systemKey]["parameters"])

            if not nameInSim and not nameInSim2app:
                #Do nothing
                pass
            elif not nameInSim and nameInSim2app:
                sim[systemKey]["parameters"]["name"] = copy.deepcopy(sim2app[systemKey]["parameters"]["name"])
            elif nameInSim and not nameInSim2app:
                #Do nothing
                pass
            elif nameInSim and nameInSim2app:
                if mode == "modelId":
                    #Name must be the same
                    if sim[systemKey]["parameters"]["name"] != sim2app[systemKey]["parameters"]["name"]:
                        self.logger.error("System name must be the same. (Mode: modelId)")
                        raise Exception("System name must be the same.")
                elif mode == "batchId":
                    #Combine names
                    sim[systemKey]["parameters"]["name"] = sim[systemKey]["parameters"]["name"] + \
                                                          "_" + \
                                                          sim2app[systemKey]["parameters"]["name"]

            #Check if parameters share some keys. If yes, check if they are the same.
            #If parameters do not share some keys or the shared keys are the same, append them.
            for key in sim[systemKey]["parameters"]:
                if key == "name":
                    continue
                elif key in sim2app[systemKey]["parameters"]:
                    if sim[systemKey]["parameters"][key] != sim2app[systemKey]["parameters"][key]:
                        logger.error("Shared system parameters are not the same")
                        raise Exception("Shared system parameters are not the same")

            for key in sim2app[systemKey]["parameters"]:
                if key == "name":
                    continue
                else:
                    sim[systemKey]["parameters"][key] = sim2app[systemKey]["parameters"][key]


    #System appended
    #########################

