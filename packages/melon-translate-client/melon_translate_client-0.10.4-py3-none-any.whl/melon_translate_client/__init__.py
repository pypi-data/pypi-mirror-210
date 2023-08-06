"""Melon Translate client"""

# from redis_om import Migrator

from ._client import Client

__all__ = ["Client"]

#
# class _InitializeModule:
#     __instance = None
#
#     def __new__(cls, *args, **kwargs):
#         if not cls.__instance:
#             cls.__instance = super().__new__(cls, *args, **kwargs)
#         return cls.__instance
#
#     def __init__(self):
#         self.setup_lock()
#         self.setup_models()
#
#     def setup_lock(self):
#         pass
#
#     @staticmethod
#     def setup_models():
#         # redis = get_redis_connection()
#         Migrator().run()
#
#
# _ = _InitializeModule()
