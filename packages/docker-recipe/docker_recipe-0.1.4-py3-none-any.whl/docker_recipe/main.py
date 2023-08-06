import typing

import jinja2
import yaml
import pydantic


class DockerRecipeImage(pydantic.BaseModel):
    name: str
    Dockerfile: str
    latest: bool = False
    arguments: typing.Dict[str, str] = {}


class DockerRecipe(pydantic.BaseModel):
    images: typing.List[DockerRecipeImage]


def load_recipe(path: str) -> DockerRecipe:
    with open(path) as f_recipe:
        config_contents = f_recipe.read()

    return DockerRecipe(**yaml.load(config_contents, Loader=yaml.FullLoader))


def render_file(path: str, recipe: DockerRecipe) -> str:
    fsl = jinja2.FileSystemLoader('..')
    env = jinja2.Environment(loader=fsl)
    tpl = env.get_template(path)
    output = tpl.render({"recipe": recipe})

    return output if output.endswith("\n") else output + "\n"


def main():
    with open(".gitlab-ci.yml", 'w+') as f_gitlab_ci:
        f_gitlab_ci.write(render_file('.gitlab-ci.recipe.yml',
                                      load_recipe("docker-recipe.yml")))


if __name__ == '__main__':
    main()
