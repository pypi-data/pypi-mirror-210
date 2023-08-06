import os

class Redux:

    def __generate_store(self):
        string = ""
        string += "import { configureStore } from '@reduxjs/toolkit';\n"
        string += "import { combineReducers } from 'redux';\n"
        string += "\n"
        string += "const rootReducer = combineReducers({\n"
        string += "  // reducers\n"
        string += "});\n"
        string += "\n"
        string += "const store = configureStore({\n"
        string += "  reducer: rootReducer\n"
        string += "});\n"
        string += "\n"
        string += "export default store;\n"

        with open("src/store/index.js", "w") as f:
            f.write(string)

    def __generate_reducers(self):
        os.mkdir("src/store/slices")

        string = ""
        string += "import { createSlice } from '@reduxjs/toolkit';\n"
        string += "\n"
        string += "const initialState = {\n"
        string += "  // state\n"
        string += "};\n"
        string += "\n"
        string += "const slice = createSlice({\n"
        string += "  name: 'slice',\n"
        string += "  initialState,\n"
        string += "  reducers: {\n"
        string += "    // reducers\n"
        string += "  }\n"
        string += "});\n"
        string += "\n"
        string += "export const { actions, reducer } = slice;\n"

        with open("src/store/slices/slice.js", "w") as f:
            f.write(string)

    def __generate_main_file(self):
        string = ""
        string += "import React from 'react';\n"
        string += "import ReactDOM from 'react-dom';\n"
        string += "import './index.css';\n"
        string += "import App from './App';\n"
        string += "import { Provider } from 'react-redux';\n"
        string += "import store from './store';\n"
        string += "\n"
        string += "const rootElement = document.getElementById('root');\n"
        string += "ReactDOM.createRoot(rootElement).render(\n"
        string += "  <React.StrictMode>\n"
        string += "    <Provider store={store}>\n"
        string += "      <App />\n"
        string += "    </Provider>\n"
        string += "  </React.StrictMode>\n"
        string += ");\n"


    def install(self, main_file = False):
        self.__generate_store()
        self.__generate_reducers()
        if main_file:
            self.__generate_main_file()
        return "@reduxjs/toolkit react-redux"