def get_action_data(**kwargs):
    return {
        "name": kwargs.get("name", "Agent Romeo"),
        "guid": kwargs.get("guid", "adb014e3-2c3b-4870-80b1-98078ba211fc"),
        "description": kwargs.get("description", "Describing shakespeares ass"),
        "prompt": kwargs.get(
            "prompt",
            "Answer the question using the context provided. If you can't answer the question using the context provided respond with \"I don't know\"",
        ),
        "model_config": kwargs.get(
            "model_config",
            {
                "topP": 0.8,
                "temperature": 0.8,
                "stopSequence": [],
                "frequencyPenalty": 0,
                "presencePenalty": -1.6,
                "maxResponseLength": 2101,
            },
        ),
        "appId": kwargs.get("appId", 1),
        "modelId": kwargs.get("modelId", 9),
        "experimentId": kwargs.get("experimentId", None),
        "agent_type": kwargs.get("agent_type", "simple"),
        "createdAt": kwargs.get("createdAt", "2023-03-02T11:49:21.163000"),
        "updatedAt": kwargs.get("updatedAt", "2023-04-05T11:27:15.215000"),
    }
