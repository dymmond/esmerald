from lilya.context import g


class Test:
    def get_name(self) -> str:
        return g.name
