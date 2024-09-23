import traceback


class EventHandler:
    def __init__(self) -> None:
        self.event_trigger_dict: dict[str, list] = {}

    def get_event_triggers(self, event_type: str):
        return self.event_trigger_dict.get(event_type, [])

    def add_event_trigger(self, event_type: str, source, callback):
        trigger = (source, callback)

        if event_type not in self.event_trigger_dict:
            self.event_trigger_dict[event_type] = [trigger]
        else:
            self.event_trigger_dict[event_type].append(trigger)

    def remove_all_event_triggers(self, source):
        for triggers in self.event_trigger_dict.values():
            removing_triggers = []
            for trigger in triggers:
                if source is trigger[0]:
                    removing_triggers.append(trigger)
            for trigger in removing_triggers:
                triggers.remove(trigger)

    def handle_event(self, event_type: str, *args):
        triggers = self.get_event_triggers(event_type)
        for source, callback in triggers:
            try:
                callback(*args)
            except KeyboardInterrupt:
                raise
            except:
                print(event_type, callback, "failed")
                traceback.print_exc()
