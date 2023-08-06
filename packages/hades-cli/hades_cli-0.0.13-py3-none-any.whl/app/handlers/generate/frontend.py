import os
from inquirer import prompt, Text, Confirm, List
import boto3
from app.resources.redux import Redux
from app.resources.tailwind import Tailwind
from app.resources.router import Router
from app.resources.chakra import Chakra

__ui_frameworks__ = [
    "none",
    "chakra-ui",
    "material-ui",
    "react-bootstrap",
    "react-md",
    "semantic-ui",
    "ant-design",
]

__folders__ = [
    "components",
    "pages",
    "utils",
    "hooks",
    "services",
    "store",
    "styles",
    "types",
    "assets",
    "config",
    "constants"
]

bucket_name = "mycli.templates"
deps = []
devDeps = [
    "@iconify/react"
]

__questions__ = [
    Text('name', message='What is the name of your project?', default="my-proyect"),
    Confirm('typescript', message='Do you want use typescript?', default=False),
    Confirm('react-router',
            message='Do you want to install react-router?', default=True),
    Confirm('redux', message='Do you want to install redux?', default=True),
    Confirm('tailwind', message='Do you want to install tailwind?', default=True),
    List('ui-framework', message='Which UI framework do you want to use?',
         choices=__ui_frameworks__, default="none")
]


class FrontendGenerator:

    s3 = boto3.client('s3')

    def run(self):
        answers = prompt(__questions__)

        template = "react-ts" if answers['typescript'] else "react"
        os.system(f"yarn create vite {answers['name']} --template {template}")
        os.chdir(answers['name'])
        os.system("yarn")

        is_chakra = answers["ui-framework"] == "chakra-ui"
        main_file = not (is_chakra and answers["redux"])

        if not main_file:
            self.s3.download_file(bucket_name, "main.jsx", "src/main.jsx")
        
        [os.makedirs(f"src/{folder}", exist_ok=True) for folder in __folders__]

        if is_chakra:
            c = Chakra()
            chakra_cmd = c.install(main_file)
            deps.append(chakra_cmd)

        if answers['redux']:
            r = Redux()
            redux_cmd = r.install(main_file)
            deps.append(redux_cmd)

        if answers['react-router']:
            r = Router()
            router_cmd = r.install()
            deps.append(router_cmd)

        if answers['tailwind']:
            t = Tailwind()
            tailwind_cmd = t.install()
            devDeps.append(tailwind_cmd)
            
        os.unlink("src/App.css")

        os.system(f"yarn add {' '.join(deps)}")
        os.system(f"yarn add -D {' '.join(devDeps)}")
