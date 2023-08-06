async def update_id(data, actor):
    data["id"] = actor.generate_new_object_id()
    if "object" in data and isinstance(data["object"], dict):
        if "id" in data["object"]:
            obj_in_store = await actor.retrieve(data["object"]["id"])
            print(obj_in_store)
            if not obj_in_store:
                data["object"]["id"] = actor.generate_new_object_id()
        else:
            data["object"]["id"] = actor.generate_new_object_id()

    return data
