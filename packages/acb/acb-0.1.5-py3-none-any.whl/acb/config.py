import typing as t
from importlib import import_module
from inspect import getargvalues
from inspect import getmodule
from inspect import getouterframes
from inspect import getsourcelines
from inspect import stack

from acb.actions import dump
from acb.actions import load
from aiopath import AsyncPath
from inflection import camelize
from inflection import titleize
from inflection import underscore
from pydantic import BaseModel
from pydantic import BaseSettings
from pydantic import Extra


class AppSettings(BaseSettings):
    class Config:
        extra = Extra.allow
        arbitrary_types_allowed = True

    async def __call__(self) -> None:
        adapter_name = underscore(self.__class__.__name__.replace("Settings", ""))
        yml_path = ac.settings_path / adapter_name
        if not await yml_path.exists() and not ac.deployed:
            await dump.yml(self.dict(), yml_path)
        yml_settings = await load.yml(yml_path)
        if adapter_name == "debug":
            app_mods = [path.stem async for path in ac.basedir.rglob("*.py")]
            all_mods = app_mods + list(ac.app.adapters)
            for mod in [mod for mod in all_mods if mod not in yml_settings]:
                yml_settings[mod] = False
        super().__init__(**yml_settings)
        setattr(ac, adapter_name, self)
        if not ac.deployed:
            await dump.yml(yml_settings, yml_path)


class Debug(AppSettings):
    production = False
    main = False
    logger = False
    database = False
    cache = False


class App(AppSettings):
    project: str = "acb"
    name: str = "acb-app"
    title: str = None
    adapters: dict = {}

    def __init__(self, **values: t.Any) -> None:
        super().__init__(**values)
        self.title = self.title or titleize(self.name)


class AppConfig(BaseSettings):
    deployed = False
    basedir: AsyncPath = None
    tmp: AsyncPath = "tmp"
    config_path: AsyncPath = None
    settings_path: AsyncPath = None
    debug: Debug = Debug()
    app: App = App()

    async def __call__(self, deployed: bool = False) -> None:
        self.basedir = AsyncPath().cwd()
        self.tmp = self.basedir / "tmp"
        self.config_path = self.basedir / "config.py"
        self.settings_path = self.basedir / "settings"
        await self.settings_path.mkdir(exist_ok=True)
        self.deployed = True if self.basedir.name == "app" else deployed
        # deployed = True if basedir.name == "srv" else False
        # self.debug = False if deployed else True
        # self.secrets = await SecretManager().init()
        print(getsourcelines(App))
        if not await self.config_path.exists():
            await self.config_path.write_text(
                f"from acb.config import AppSettings\n\n{getsourcelines(App)}"
            )
        # configs = dict()
        if self.basedir.name != "acb":
            app_settings = import_module("config")
            await app_settings.App()()
        await self.debug()
        for cat, adapter in self.app.adapters:
            module = import_module(".".join(["acb", "adapters", cat, adapter]))
            adapter_settings = getattr(module, f"{camelize(adapter)}Settings")
            await adapter_settings()()
        # super().__init__(**configs)

    class Config:
        extra = "allow"
        arbitrary_types_allowed = False


ac = AppConfig()


class InspectStack(BaseModel):
    @staticmethod
    def calling_function():
        frm = stack()[2]
        return AsyncPath(getmodule(frm[0]).__file__).stem

    @staticmethod
    def calling_page(calling_frame):
        calling_stack = getouterframes(calling_frame)
        page = ""
        for f in calling_stack:
            if f[3] == "render_template_string":
                page = getargvalues(f[0]).locals["context"]["page"]
        return page


inspect_ = InspectStack()
