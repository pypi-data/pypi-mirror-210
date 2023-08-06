from enum import Enum


class ProviderType(Enum):
    QUAO_QUANTUM_SIMULATOR = 'QUAO_QUANTUM_SIMULATOR'
    IBM_QUANTUM = 'IBM_QUANTUM'
    IBM_CLOUD = 'IBM_CLOUD'
    AWS_CLOUD = 'AWS_CLOUD'
