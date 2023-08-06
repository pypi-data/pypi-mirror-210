from crimm.StructEntities.TopoElements import Bond, Angle, Dihedral, Improper
from crimm.Modeller import TopologyLoader, ParameterLoader, SeqChainGenerator
from crimm.Modeller.TopoFixer import ResidueFixer

class Topology:
    def __init__(self) -> None:
        self.definitions = {}
        self.params = {}
        self._1to3 = None
        self._3to1 = None
        self._report_res = None
        self.resnames = None
        self.built_residues = None
    
    def load_definition(self, entity_type: str):
        definition = TopologyLoader(entity_type)
        param = ParameterLoader(entity_type)
        param.fill_ic(definition)
        self.definitions[entity_type] = definition
