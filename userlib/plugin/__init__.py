from dataclasses import dataclass


@dataclass
class PluginInfo:
    name: str
    description: str
    usage: str
