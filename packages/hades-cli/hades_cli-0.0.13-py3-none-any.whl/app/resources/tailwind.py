import os

class Tailwind:

    def __create_config_file(self):
        string = ""
        string += "/** @type {import('tailwindcss').Config} */\n"
        string += "export default {\n"
        string += "  content: ['./src/**/*.{js,jsx,ts,tsx}', './index.html'],\n"
        string += "  theme: {\n"
        string += "    extend: {},\n"
        string += "  },\n"
        string += "  plugins: [],\n"
        string += "}\n"

        with open("tailwind.config.js", "w") as f:
            f.write(string)

    def __create_index_css_file(self):
        string = ""
        string += "@tailwind base;\n"
        string += "@tailwind components;\n"
        string += "@tailwind utilities;\n"

        with open("src/index.css", "w") as f:
            f.write(string)

    def install(self):
        self.__create_config_file()
        self.__create_index_css_file()
        os.system("npx tailwindcss init -p")
        return "tailwindcss postcss autoprefixer"