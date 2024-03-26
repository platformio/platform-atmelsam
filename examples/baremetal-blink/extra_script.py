Import("env")

#
# Dump build environment (for debug)
# print(env.Dump())
#

env.Append(
  LINKFLAGS=[
      "-Tsrc/variant/linker_scripts/gcc/flash.ld",
  ]
)