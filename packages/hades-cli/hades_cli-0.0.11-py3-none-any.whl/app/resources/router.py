import os

class Router:

    def __create_app_file(self):
        string = ""
        string += "import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';\n"
        string += "\n"
        string += "import Home from './pages/Home';\n"
        string += "\n"
        string += "const App = () => {\n"
        string += "  return (\n"
        string += "    <BrowserRouter>\n"
        string += "      <Routes>\n"
        string += "        <Route path='/' element={<Home />} />\n"
        string += "        <Route path='*' element={<Navigate to='/' replace />} />\n"
        string += "      </Routes>\n"
        string += "    </BrowserRouter>\n"
        string += "  );\n"
        string += "};\n"
        string += "\n"
        string += "export default App;\n"

        with open("src/App.jsx", "w") as f:
            f.write(string)


    def __create_home_file(self):
        string = ""
        string += "const Home = () => {\n"
        string += "  return <div>React router installed!</div>;\n"
        string += "};\n"
        string += "\n"
        string += "export default Home;\n"

        with open("src/pages/Home.jsx", "w") as f:
            f.write(string)

    def install(self):
        self.__create_app_file()
        self.__create_home_file()
        return "react-router-dom@6"