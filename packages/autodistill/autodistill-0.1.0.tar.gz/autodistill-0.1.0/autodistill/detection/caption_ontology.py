from dataclasses import dataclass
from typing import List, Tuple

from autodistill.detection import DetectionOntology

@dataclass
class CaptionOntology(DetectionOntology):
    promptMap: List[Tuple[str, str]]

    def prompts(self) -> List[str]:
        return super().prompts()
    
    def classToPrompt(self, cls: str) -> str:
        return super().classToPrompt(cls)
