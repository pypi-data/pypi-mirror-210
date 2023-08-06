class Utils:

    def copy_content(self, src, dest):
        with open(src, "r") as file:
            data = file.read()
        with open(dest, "w") as file:
            file.write(data)