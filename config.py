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


class GlobalConfig(ConfigWithCheck):
    def _valid_image_config(self, config):
        return isinstance(config, ImageConfig)


class ImageConfig(ConfigWithCheck):
    def _valid_store(self, value):
        return value in ['local', 'blank', 'notion', 's3']


global_config = GlobalConfig()

global_config.image_config = ImageConfig()

# 'local': download in to local disk
# 'blank': ignore all images
# 'notion': do not download image, use a URL provided by Notion.so instead (login required)
# 's3': do not download image, use a URL provided by Amazon S3 instead (URL might be outdated afterwards)
global_config.image_config.store = 'local'
