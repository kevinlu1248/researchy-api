from typing import Callable


def cached_property(property_function: Callable) -> Callable:
    """
    For making properties store themselves as private properties.
    This is so that the same property does not get computed twice by storing the
    the result but at the same time unneeded properties never get called.
    """

    @property
    def decorated_property(self):
        # print("_{}__{}".format(type(self).__name__, property_function.__name__))
        prop_name = "__{}".format(property_function.__name__)
        prop_class_name = "_{}__{}".format(
            type(self).__name__, property_function.__name__
        )
        if not hasattr(self, prop_class_name):
            setattr(self, prop_class_name, property_function(self))
        return getattr(self, prop_class_name)

    return decorated_property


def indirectly_cached_property(property_function: Callable) -> Callable:
    """
    Like cached property but runs another function that indirectly sets the
    private variable to the solution.
    """

    @property
    def decorated_property(self):
        prop_name = "__{}".format(property_function.__name__)
        prop_class_name = "_{}__{}".format(
            type(self).__name__, property_function.__name__
        )
        if not hasattr(self, prop_class_name):
            property_function(self)
        return getattr(self, prop_class_name)

    return decorated_property
