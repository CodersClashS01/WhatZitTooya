class CogError(Exception):
    msg = 'Beim Hinzufügen des Cogs ist ein Error aufgetreten.' \
          'Bitte prüfe, ob der Cog existiert, ob Codefehler präsent sind,' \
          ' und ob der Cog ordnungsgemäß eingebunden wird.'

    def __str__(self):
        return self.msg
