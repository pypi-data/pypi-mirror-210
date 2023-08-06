import re


class Time:
    minutes: int
    seconds: int
    hundredths: int

    @property
    def value(self) -> int:
        return self.minutes * 6000 + self.seconds * 100 + self.hundredths

    def __init__(self, time) -> None:
        if type(time) is int:
            self.minutes  = time // 6000
            self.seconds = (time % 6000) // 100
            self.hundredths = time % 100
        elif type(time) is float:
            int_value = int(round(time*100))
            self.minutes = int_value // 6000
            self.seconds = (int_value % 6000) // 100
            self.hundredths = int_value % 100
        elif type(time) is str:
            m = re.match(r"(?P<minutes>\d*)?:?(?P<seconds>\d{2})[\.:]?(?P<hundredths>\d{1,2})?$", time)

            if m is None:
                if time == "NT" or int(time) == 0:
                    self.minutes = 0
                    self.seconds = 0
                    self.hundredths = 0
                    return
                else:
                    raise ValueError(f"Invalid time string: {time}")

            minutes = m.group("minutes")
            if minutes is None or minutes == "":
                self.minutes = 0
            else:
                self.minutes = int(minutes)

            seconds = m.group("seconds")
            self.seconds = int(seconds)

            hundredths = m.group("hundredths")
            if hundredths is None or hundredths == "":
                self.hundredths = 0
            elif len(hundredths) == 1:
                self.hundredths = int(hundredths) * 10
            else:
                self.hundredths = int(hundredths)

    def __repr__(self) -> str:
        if self.value == 0:
            return "NT"
        else:
            minutes = f"{self.minutes}:" if self.minutes > 0 else ""
            return f"{minutes}{self.seconds:02d}.{self.hundredths:02d}"

    def __eq__(self, __o: object) -> bool:
        if type(__o) is int or type(__o) is str:
            return self.value == Time(__o).value
        elif type(__o) is Time:
            return self.value == __o.value
        else:
            raise TypeError(f"Equality undefined for given type: {type(__o)}")