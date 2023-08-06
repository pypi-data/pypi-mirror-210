import judo
from judo.data_types import dtype

from fragile.core.api_classes import Callback
from fragile.core.typing import StateDict


class StoreInitAction(Callback):
    name = "store_init_action"
    default_inputs = {"init_actions": {"clone": True}}
    default_outputs = ("init_actions",)

    @property
    def param_dict(self) -> StateDict:
        return {"init_actions": dict(self.swarm.param_dict["actions"])}

    def before_env(self):
        if self.swarm.epoch == 0:
            self.update(init_actions=judo.copy(self.get("actions")))


class TrackWalkersId(Callback):
    default_inputs = {"id_walkers": {"clone": True}, "parent_ids": {"clone": True}}
    default_param_dict = {
        "id_walkers": {"dtype": dtype.hash_type},
        "parent_ids": {"dtype": dtype.hash_type},
    }

    def update_ids(self, inactives: bool = True):
        with judo.Backend.use_backend("numpy"):
            name = "states" if "states" in self.swarm.state.names else "observs"
            actives = judo.to_numpy(self.swarm.state.actives)
            new_ids_all = self.swarm.state.hash_batch(name)
            parent_ids = judo.copy(judo.to_numpy(self.get("parent_ids", inactives=inactives)))
            new_ids = judo.copy(judo.to_numpy(self.get("id_walkers", inactives=True)))
            parent_ids[actives] = judo.copy(new_ids[actives])
            new_ids[actives] = new_ids_all[actives]
        self.update(
            parent_ids=judo.to_backend(parent_ids),
            id_walkers=judo.to_backend(new_ids),
            inactives=inactives,
        )

    def after_env(self):
        self.update_ids()
