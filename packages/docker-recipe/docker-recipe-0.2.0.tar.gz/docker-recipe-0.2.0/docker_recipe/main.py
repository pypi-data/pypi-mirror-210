import typing
import argparse
import os

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
    fsl = jinja2.FileSystemLoader(os.path.dirname(path))
    env = jinja2.Environment(loader=fsl)
    tpl = env.get_template(os.path.basename(path))
    output = tpl.render({"recipe": recipe})

    return output if output.endswith("\n") else output + "\n"


parser = argparse.ArgumentParser(description="Docker Recipe File")
parser.add_argument('-r',
                    '--docker-recipe',
                    default=os.path.join(os.getcwd(), 'docker-recipe.yml'),
                    help='Path to the docker-recipe.yml file. ' +
                         'Default is `docker-recipe.yml` in the current working directory.')

parser.add_argument('-g',
                    '--gitlab-ci-template',
                    default=os.path.join(os.getcwd(), '.gitlab-ci.recipe.yml'),
                    help='Path to the .gitlab-ci.recipe.yml file. ' +
                         'Default is `.gitlab-ci.recipe.yml` in the current working directory.')

parser.add_argument('-o',
                    '--gitlab-ci-output-file',
                    default=os.path.join(os.getcwd(), '.gitlab-ci.yml'),
                    help='Path to the .gitlab-ci.yml file. ' +
                         'Default is `.gitlab-ci.recipe.yml` in the current working directory.')


def main():
    args = parser.parse_args()

    with open(args.gitlab_ci_output_file, 'w+') as f_gitlab_ci:
        f_gitlab_ci.write(render_file(args.gitlab_ci_template,
                                      load_recipe(args.docker_recipe)))


if __name__ == '__main__':
    main()
