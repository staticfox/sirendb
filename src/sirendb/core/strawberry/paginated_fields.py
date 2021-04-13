class PaginatedFields:
    def __init__(self):
        self.fields = {}

    def __setitem__(self, key, value):
        self.fields[key] = value

    def __getitem__(self, key):
        return self.fields[key]


paginated_fields = PaginatedFields()
