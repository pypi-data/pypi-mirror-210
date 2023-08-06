import os


class Chakra:

    def __generate_main_file(self):
        string = ""
        string += "import React from 'react';\n"
        string += "import ReactDOM from 'react-dom';\n"
        string += "import './index.css';\n"
        string += "import App from './App';\n"
        string += "import { ChakraProvider } from '@chakra-ui/react';\n"
        string += "import theme from './theme';\n"
        string += "\n"
        string += "const rootElement = document.getElementById('root');\n"
        string += "ReactDOM.createRoot(rootElement).render(\n"
        string += "  <React.StrictMode>\n"
        string += "    <ChakraProvider theme={theme}>\n"
        string += "      <App />\n"
        string += "    </ChakraProvider>,\n"
        string += "  </React.StrictMode>,\n"
        string += ");\n"

        with open("src/main.jsx", "w") as f:
            f.write(string)

    def install(self, main_file=False):
        if main_file:
            self.__generate_main_file()
        return "@chakra-ui/react @emotion/react @emotion/styled framer-motion"