def get_application_data(**kwargs):
    return {
        "id": kwargs.get('id', 1),
        "enabled": kwargs.get('enabled', True),
        "name": kwargs.get('name', 'new-test-name'),
        "app_type": kwargs.get('app_type', 'simple'),
        "workspaceId": kwargs.get('workspace_id', 1),
        "guid": kwargs.get('guid', '39032480-bd0e-4b15-ad42-513a504c4dc2'),
        "createdById": kwargs.get('created_by_id', 'cleogi474000018fijzmbyycs'),
        "model_config": kwargs.get(
            'model_config',
            {
                'topP': 1,
                'temperature': 0.7,
                'stopSequence': [],
                'presencePenalty': 0,
                'frequencyPenalty': 0,
                'maxResponseLength': 250,
            },
        ),
        "deleted": kwargs.get('deleted', False),
        "updatedAt": kwargs.get('updated_at', '2023-04-24T01:06:47.512000'),
        "createdAt": kwargs.get('created_at', '2023-02-28T16:22:06.984000'),
        "description": kwargs.get(
            'description',
            'A ridiculously long description of this app that should go over the limit and look bad in the header',
        ),
    }
