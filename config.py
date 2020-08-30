class ConfigWithCheck:
    def __setattr__(self, key, value):
        if key in self.__class__.__dict__:
            return
        check_func = getattr(self, '_valid_' + key, None)
        if check_func is None:
            raise AttributeError('{} does not have attribute {}'.format(self.__class__.__name__, key))
        if not check_func(value):
            raise AttributeError('Invalid value {} for {} of {}'.format(value, key, self.__class__.__name__))
        super().__setattr__(key, value)
