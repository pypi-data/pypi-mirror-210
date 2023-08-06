"""
字体颜色设置
    url: https://www.jianshu.com/p/a6791ba66e3d
"""
# class A:
#
#     def __init__(self):
#         self.a = 100
#
#     def __get__(self, instance, owner):
#         return object.__getattribute__(self, "a")
#
#     def __set__(self, instance, value):
#         print(instance, value)
#         self.a = value
#
#     def __del__(self):
#         del self.a
#
# class B:
#     a = A()
#
# B().a = 1
# print(B().a)

from smawe_tools.config import Config

config = Config(interpolation_level=2)
# s1 = config.switch_to_section("s1")
# s2 = config.switch_to_section("s2")
# s3 = config.switch_to_section("s3")
# s1.set("k1", "v1")
# s1.set("k2", "v2")
# s1.set("k3", "v3")
# s2.set("k3", "v3")
# s2.set("kk2", "%(k3)s-kk2")
# s2.set("kk3", "%(kk2)s-kk3")
# s2.set("kk4", "${s1:k1}")
# print(s2.get("kk2"))
# for i in s2.values():
#     print(i)
#
# for i in s1:
#     print(i)
# print(config.get_sections())
# for i in config:
#     print(i)
#
# print(len(config))
# print(len(s1))
# config.switch_to_section("s1").set("k1", "v1")
# config.switch_to_section("s1").set("k2", "v2")
# config.switch_to_section("s1").set("k3", "v3")
# print(config.switch_to_section("s1").get_options())
# config.save_config("test.ini")
# print("save successfully")
if config.read_config("test.ini"):
    print("read config successfully")
    for i in config.switch_to_section("s2").values():
        print(i)
else:
    print("read config failure")
