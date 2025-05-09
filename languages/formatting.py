class LocalizedString(str):
    def format(self, **kwargs):
        return super().format(**kwargs)
