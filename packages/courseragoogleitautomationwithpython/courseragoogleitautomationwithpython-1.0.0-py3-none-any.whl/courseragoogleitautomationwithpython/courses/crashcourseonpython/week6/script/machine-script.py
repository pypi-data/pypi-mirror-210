from typing import List, Dict
import datetime


class MachineEvent:
    def __init__(self, event_type: str, user: str, machine_name: str, event_date: datetime):
        self._type = event_type
        self._user = user
        self._machine_name = machine_name
        self._date = event_date

    def date(self) -> datetime:
        return self._date

    def machine_name(self) -> str:
        return self._machine_name

    def type(self) -> str:
        return self._type

    def user(self) -> str:
        return self._user

    def __str__(self):
        return f"MachineEvent(type={self.type()}, user={self.user()}, machine={self.machine_name()}, date={self.date()})"


class MachineEventsMonitor:
    @staticmethod
    def get_even_dates(event: MachineEvent) -> datetime:
        return event.date()

    @staticmethod
    def current_users(some_events: List[MachineEvent]) -> Dict[str, set]:
        sorted_events: List[MachineEvent] = sorted(some_events, key=MachineEventsMonitor.get_even_dates)
        machines: Dict[str, set] = {}

        for event in sorted_events:
            if event.machine_name() not in machines:
                machines[event.machine_name()] = set()
            if event.type() == "login":
                machines[event.machine_name()].add(event.user())
            elif event.type() == "logout" and event.user() in machines[event.machine_name()]:
                machines[event.machine_name()].remove(event.user())

        return machines

    @staticmethod
    def generate_report(machines: Dict[str, set]) -> None:
        for machine, users in machines.items():
            if len(users) > 0:
                user_list = ", ".join(users)
                print(f"{machine}: {user_list}")


if __name__ == "__main__":
    events: List[MachineEvent] = [
        MachineEvent(event_date="2022-11-28T12:45:56+01:00", event_type="login", machine_name="myworkstation.local", user="jordan"),
        MachineEvent(event_date="2022-11-28T15:53:42+01:00", event_type="logout", machine_name="webserver.local", user="jordan"),
        MachineEvent(event_date="2022-11-28T18:53:21+01:00", event_type="login", machine_name="webserver.local", user="lane"),
        MachineEvent(event_date="2022-11-28T10:25:34+01:00", event_type="logout", machine_name="myworkstation.local", user="jordan"),
        MachineEvent(event_date="2022-11-28T08:08:20+01:00", event_type="login", machine_name="webserver.local", user="jordan"),
        MachineEvent(event_date="2022-11-28T11:24:24+01:00", event_type="login", machine_name="mailserver.local", user="chris"),
    ]
    current_users = MachineEventsMonitor.current_users(some_events=events)
    print(current_users)

    MachineEventsMonitor.generate_report(machines=current_users)
