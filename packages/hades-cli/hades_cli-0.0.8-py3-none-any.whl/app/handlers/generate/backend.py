import os
from inquirer import prompt, Text, List, Confirm
import json
import shutil

folders = [
    "handlers",
    "models",
    "services",
    "utils",
    "config",
    "constants",
]

__db_providers__ = {
    "none": None,
    "mongodb": "mongodb",
    "mysql": "mysql2",
    "postgresql": "pg",
    "sqlite": "sqlite3",
    "oracle": "oracledb",
    "mssql": "mssql",
}

__packages__ = {
    "devDeps": [
        "nodemon",
        "morgan",
    ],
    "deps": [
        "express",
        "cors",
        "dotenv",

    ]
}

__quetions__ = [
    Text('name', message='What is the name of your project?', default="my-proyect"),
    # Confirm('typescript', message='Do you want use typescript?', default=False),
    List('db-provider', message='Which database provider do you want to use?', choices=__db_providers__, default="none"),
    Text("port", message="Which port do you want to use?", default="3000"),
]


class BackendGenerator:

    port = None

    def generate_nodemon_file(self):
        string = ""
        string += "{"
        string += "  \"watch\": \"src\","
        string += "  \"ext\": \"js\","
        string += "  \"ignore\": ["
        string += "    \"node_modules\","
        string += "    \"dist\""
        string += "  ],"
        string += "  \"exec\": \"node src/index.js\""
        string += "}"
        with open("nodemon.json", "w") as f:
            f.write(string)

    def generate_index(self):
        string = ""
        string += "import express from 'express';\n"
        string += "import cors from 'cors';\n"
        string += "import morgan from 'morgan';\n"
        string += "import dotenv from 'dotenv';\n"
        string += "\n"
        string += "dotenv.config();\n"
        string += "\n"
        string += "const app = express();\n"
        string += "\n"
        string += "app.use(cors());\n"
        string += "app.use(morgan('dev'));\n"
        string += "app.use(express.json());\n"
        string += "\n"
        string += f"console.log('Running on http://localhost:{self.port}')\n"
        string += f"app.listen({self.port});\n"

        with open("src/index.js", "w") as f:
            f.write(string)


    def update_package_json(self):
        with open("package.json", "r") as f:
            package = json.load(f)

        package["type"] = "module"
        package["scripts"] = {}
        package["scripts"]["dev"] = "nodemon"
        package["scripts"]["start"] = "node src/index.js"

        with open("package.json", "w") as f:
            json.dump(package, f, indent=2)
    

    def run(self):
        answers = prompt(__quetions__)
        self.port = int(answers['port'])
        pwd = os.getcwd()

        if os.path.exists(f"{pwd}/{answers['name']}"):
            answer = prompt([ Confirm('overwrite', message='The project already exists, do you want to overwrite it?', default=False) ])
            if not answer['overwrite']:
                return
            shutil.rmtree(f"{pwd}/{answers['name']}")
        
        os.mkdir(f"{pwd}/{answers['name']}")
        os.chdir(f"{pwd}/{answers['name']}")
        os.system("yarn init -y")

        os.mkdir("src")
        [os.makedirs(f"src/{folder}", exist_ok=True) for folder in folders]

        self.update_package_json()

        if answers['db-provider'] is not None:
            provider = __db_providers__[answers['db-provider']]
            __packages__['deps'].append(provider)

        os.system(f"yarn add {' '.join(__packages__['deps'])}")
        os.system(f"yarn add -D {' '.join(__packages__['devDeps'])}")


        self.generate_nodemon_file()
        self.generate_index()
