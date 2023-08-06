import setuptools
import distutils.command.build


class BuildCommand(distutils.command.build.build):
    def initialize_options(self):
        distutils.command.build.build.initialize_options(self)
        self.build_base = "pybuild"


if __name__ == "__main__":
    setuptools.setup(cmdclass={"build": BuildCommand})
